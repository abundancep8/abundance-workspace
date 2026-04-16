#!/usr/bin/env node

/**
 * Supabase Sync Script (Hourly)
 * 
 * Runs every hour to:
 * 1. Sync Claude-Mem learnings to Supabase
 * 2. Calculate performance metrics
 * 3. Update dashboard metrics
 * 4. Send alerts if thresholds exceeded
 * 
 * Usage:
 *   node supabase-sync.js
 * 
 * Or with cron:
 *   0 * * * * cd /path/to/workspace && node supabase-sync.js
 */

require('dotenv').config({ path: '.env.local' });
const fs = require('fs');
const path = require('path');
const { supabase, logTask, saveMemory, calculateMetrics, sendEmail } = require('./supabase-integration');

const MEMORY_DIR = path.join(__dirname, 'memory');
const SYNC_STATE_FILE = path.join(__dirname, '.supabase-sync-state.json');
const COST_THRESHOLD = parseFloat(process.env.COST_THRESHOLD_DAILY || '10.0');

/**
 * Load last sync state
 */
function loadSyncState() {
  if (fs.existsSync(SYNC_STATE_FILE)) {
    try {
      return JSON.parse(fs.readFileSync(SYNC_STATE_FILE, 'utf8'));
    } catch (e) {
      console.log('Creating new sync state');
      return { lastSyncTime: new Date().toISOString(), processedFiles: [] };
    }
  }
  return { lastSyncTime: new Date().toISOString(), processedFiles: [] };
}

/**
 * Save sync state
 */
function saveSyncState(state) {
  fs.writeFileSync(SYNC_STATE_FILE, JSON.stringify(state, null, 2));
}

/**
 * Extract memories from daily log file
 */
function extractMemoriesFromDaily(filePath, sessionId) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const memories = [];

    // Parse markdown for memory blocks
    const decisionMatch = content.match(/## Decisions?\n([\s\S]*?)(?=##|$)/i);
    const patternsMatch = content.match(/## Patterns?\n([\s\S]*?)(?=##|$)/i);
    const insightsMatch = content.match(/## Insights?\n([\s\S]*?)(?=##|$)/i);
    const errorsMatch = content.match(/## Errors?\n([\s\S]*?)(?=##|$)/i);

    if (decisionMatch) {
      memories.push({
        type: 'decision',
        content: decisionMatch[1].trim()
      });
    }
    if (patternsMatch) {
      memories.push({
        type: 'pattern',
        content: patternsMatch[1].trim()
      });
    }
    if (insightsMatch) {
      memories.push({
        type: 'insight',
        content: insightsMatch[1].trim()
      });
    }
    if (errorsMatch) {
      memories.push({
        type: 'error',
        content: errorsMatch[1].trim()
      });
    }

    return memories;
  } catch (err) {
    console.error(`Error extracting memories from ${filePath}:`, err.message);
    return [];
  }
}

/**
 * Sync daily memories to Supabase
 */
async function syncDailyMemories() {
  console.log('\n📚 Syncing daily memories...');

  if (!fs.existsSync(MEMORY_DIR)) {
    console.log('No memory directory found. Skipping.');
    return;
  }

  const state = loadSyncState();
  const files = fs.readdirSync(MEMORY_DIR).filter(f => f.match(/^\d{4}-\d{2}-\d{2}\.md$/));

  let synced = 0;

  for (const file of files) {
    if (state.processedFiles.includes(file)) {
      continue; // Already processed
    }

    const filePath = path.join(MEMORY_DIR, file);
    const sessionId = `memory:${file}`;
    const memories = extractMemoriesFromDaily(filePath, sessionId);

    for (const mem of memories) {
      await saveMemory(sessionId, mem.type, mem.content, { source: 'daily_log' });
      synced++;
    }

    state.processedFiles.push(file);
  }

  if (synced > 0) {
    state.lastSyncTime = new Date().toISOString();
    saveSyncState(state);
    console.log(`✅ Synced ${synced} memories from ${Math.ceil(synced / 3)} daily files`);
  } else {
    console.log('✅ No new memories to sync');
  }
}

/**
 * Calculate and store performance metrics
 */
async function updateMetrics() {
  console.log('\n📊 Calculating metrics...');

  const metrics = await calculateMetrics();

  if (!metrics.totalTasks) {
    console.log('No tasks in last 24 hours');
    return;
  }

  console.log(`✅ Metrics calculated:`);
  console.log(`   - Tasks: ${metrics.totalTasks}`);
  console.log(`   - Tokens: ${metrics.totalTokens}`);
  console.log(`   - Cost: $${metrics.totalCost.toFixed(4)}`);
  console.log(`   - Success Rate: ${metrics.successRate.toFixed(2)}%`);
  console.log(`   - Avg Duration: ${metrics.avgDuration}ms`);

  // Store metrics in Supabase
  try {
    const { data, error } = await supabase
      .from('performance_metrics')
      .insert([
        {
          metric_type: 'tasks_24h',
          metric_value: metrics.totalTasks,
          period: 'last_day',
          details: { model_breakdown: metrics.modelBreakdown }
        },
        {
          metric_type: 'tokens_24h',
          metric_value: metrics.totalTokens,
          period: 'last_day'
        },
        {
          metric_type: 'cost_24h',
          metric_value: metrics.totalCost,
          period: 'last_day'
        },
        {
          metric_type: 'success_rate',
          metric_value: metrics.successRate,
          period: 'last_day'
        }
      ]);

    if (error) {
      console.error('❌ Error storing metrics:', error.message);
    } else {
      console.log('✅ Metrics stored in Supabase');
    }
  } catch (err) {
    console.error('Exception storing metrics:', err.message);
  }

  // Check cost threshold
  if (metrics.totalCost > COST_THRESHOLD) {
    console.warn(`⚠️  Cost threshold exceeded! $${metrics.totalCost} > $${COST_THRESHOLD}`);
    await sendCostAlert(metrics.totalCost);
  }
}

/**
 * Send cost alert email
 */
async function sendCostAlert(dailyCost) {
  const userEmail = process.env.ALERT_EMAIL || 'abundancep@icloud.com';

  const html = `
    <h2>⚠️ Cost Alert</h2>
    <p>Your 24-hour AI agent cost has exceeded the threshold:</p>
    <p><strong>Daily Cost: $${dailyCost.toFixed(4)}</strong></p>
    <p><strong>Threshold: $${COST_THRESHOLD.toFixed(4)}</strong></p>
    <p>Check your dashboard for details: <a href="https://your-domain.com/dashboard">View Dashboard</a></p>
  `;

  await sendEmail({
    to: userEmail,
    subject: '⚠️ Agent Cost Alert',
    html,
    text: `Cost alert: $${dailyCost.toFixed(4)} exceeds threshold of $${COST_THRESHOLD.toFixed(4)}`
  });
}

/**
 * Clean up old records (keep last 90 days)
 */
async function cleanupOldRecords() {
  console.log('\n🧹 Cleaning up old records...');

  const ninetyDaysAgo = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000).toISOString();

  try {
    // Delete old task logs
    const { error: logError } = await supabase
      .from('task_log')
      .delete()
      .lt('created_at', ninetyDaysAgo);

    if (logError) {
      console.error('Error deleting old logs:', logError.message);
    } else {
      console.log('✅ Old task logs cleaned up');
    }

    // Delete old memories
    const { error: memError } = await supabase
      .from('agent_memory')
      .delete()
      .lt('created_at', ninetyDaysAgo);

    if (memError) {
      console.error('Error deleting old memories:', memError.message);
    } else {
      console.log('✅ Old memories cleaned up');
    }
  } catch (err) {
    console.error('Exception during cleanup:', err.message);
  }
}

/**
 * Main sync function
 */
async function main() {
  console.log('\n🔄 Starting Supabase sync...');
  console.log(`⏰ Sync started at ${new Date().toISOString()}`);

  try {
    // Check Supabase connection
    const { data, error } = await supabase.from('task_log').select('count', { count: 'exact' }).limit(1);
    if (error) {
      console.error('❌ Cannot connect to Supabase:', error.message);
      process.exit(1);
    }

    // Run sync tasks
    await syncDailyMemories();
    await updateMetrics();
    await cleanupOldRecords();

    console.log('\n✅ Sync completed successfully at', new Date().toISOString());
  } catch (err) {
    console.error('\n❌ Sync failed:', err.message);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch(err => {
    console.error('Fatal error:', err.message);
    process.exit(1);
  });
}

module.exports = { syncDailyMemories, updateMetrics, cleanupOldRecords };
