/**
 * Supabase + Mailgun Integration
 * 
 * Main client for logging tasks, storing memories, and syncing learning cycles.
 * 
 * Usage:
 *   const { supabase, mailgun, logTask, saveMemory } = require('./supabase-integration');
 *   
 *   await logTask({
 *     task_name: 'email-campaign',
 *     model_used: 'claude-haiku',
 *     tokens_used: 2500,
 *     cost: 0.05,
 *     duration_ms: 3500,
 *     status: 'success'
 *   });
 */

require('dotenv').config({ path: '.env.local' });
const { createClient } = require('@supabase/supabase-js');
const FormData = require('form-data');
const https = require('https');
const http = require('http');

// ===== SUPABASE CLIENT =====
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_KEY = process.env.SUPABASE_ANON_KEY;

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.warn('⚠️  Supabase credentials not found. Set SUPABASE_URL and SUPABASE_ANON_KEY in .env.local');
}

const supabase = createClient(SUPABASE_URL || 'http://localhost:54321', SUPABASE_KEY || 'dummy-key');

// ===== MAILGUN CLIENT =====
const MAILGUN_API_KEY = process.env.MAILGUN_API_KEY;
const MAILGUN_DOMAIN = process.env.MAILGUN_DOMAIN;

if (!MAILGUN_API_KEY || !MAILGUN_DOMAIN) {
  console.warn('⚠️  Mailgun credentials not found. Set MAILGUN_API_KEY and MAILGUN_DOMAIN in .env.local');
}

/**
 * Log a task execution to Supabase
 * @param {Object} task - Task details
 * @param {string} task.task_name - Name of the task
 * @param {string} task.model_used - Model used (claude, kimi, gemini, etc.)
 * @param {number} task.tokens_used - Total tokens consumed
 * @param {number} task.cost - Cost in USD
 * @param {number} task.duration_ms - Duration in milliseconds
 * @param {string} task.status - 'success', 'error', 'timeout'
 * @param {string} [task.error_message] - Error message if status is 'error'
 * @param {Object} [task.metadata] - Additional metadata (JSON)
 * @returns {Promise<Object>} Inserted row
 */
async function logTask(task) {
  try {
    const { data, error } = await supabase
      .from('task_log')
      .insert([
        {
          task_name: task.task_name,
          model_used: task.model_used,
          tokens_used: task.tokens_used,
          cost: task.cost,
          duration_ms: task.duration_ms,
          status: task.status,
          error_message: task.error_message || null,
          metadata: task.metadata || {}
        }
      ])
      .select();

    if (error) {
      console.error('❌ Error logging task to Supabase:', error.message);
      return null;
    }

    console.log(`✅ Task logged: ${task.task_name} (${task.model_used}, ${task.tokens_used} tokens, $${task.cost.toFixed(4)})`);
    return data?.[0] || null;
  } catch (err) {
    console.error('Exception in logTask:', err.message);
    return null;
  }
}

/**
 * Save a memory (decision, pattern, insight) to Supabase
 * @param {string} sessionId - Session ID
 * @param {string} memoryType - 'decision', 'pattern', 'insight', 'error', 'optimization'
 * @param {string} content - Memory content
 * @param {Object} [metadata] - Additional metadata
 * @returns {Promise<Object>} Inserted row
 */
async function saveMemory(sessionId, memoryType, content, metadata = {}) {
  try {
    const { data, error } = await supabase
      .from('agent_memory')
      .insert([
        {
          session_id: sessionId,
          memory_type: memoryType,
          content,
          metadata
        }
      ])
      .select();

    if (error) {
      console.error('❌ Error saving memory:', error.message);
      return null;
    }

    console.log(`✅ Memory saved: ${memoryType} (${sessionId.substring(0, 8)}...)`);
    return data?.[0] || null;
  } catch (err) {
    console.error('Exception in saveMemory:', err.message);
    return null;
  }
}

/**
 * Get recent task logs
 * @param {number} [limit=100] - Number of recent tasks to fetch
 * @param {string} [model] - Filter by model (optional)
 * @returns {Promise<Array>} Recent tasks
 */
async function getRecentTasks(limit = 100, model = null) {
  try {
    let query = supabase
      .from('task_log')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(limit);

    if (model) {
      query = query.eq('model_used', model);
    }

    const { data, error } = await query;

    if (error) {
      console.error('❌ Error fetching tasks:', error.message);
      return [];
    }

    return data || [];
  } catch (err) {
    console.error('Exception in getRecentTasks:', err.message);
    return [];
  }
}

/**
 * Calculate metrics for dashboard
 * @returns {Promise<Object>} Metrics object
 */
async function calculateMetrics() {
  try {
    // Last 24 hours
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

    const { data: tasks, error } = await supabase
      .from('task_log')
      .select('*')
      .gte('created_at', oneDayAgo);

    if (error || !tasks) {
      console.error('❌ Error calculating metrics:', error?.message);
      return {};
    }

    const totalTasks = tasks.length;
    const totalTokens = tasks.reduce((sum, t) => sum + (t.tokens_used || 0), 0);
    const totalCost = tasks.reduce((sum, t) => sum + (t.cost || 0), 0);
    const successCount = tasks.filter(t => t.status === 'success').length;
    const successRate = totalTasks > 0 ? (successCount / totalTasks) * 100 : 0;
    const avgDuration = totalTasks > 0 ? tasks.reduce((sum, t) => sum + (t.duration_ms || 0), 0) / totalTasks : 0;

    // Model breakdown
    const modelBreakdown = {};
    tasks.forEach(t => {
      if (!modelBreakdown[t.model_used]) {
        modelBreakdown[t.model_used] = { count: 0, tokens: 0, cost: 0 };
      }
      modelBreakdown[t.model_used].count += 1;
      modelBreakdown[t.model_used].tokens += t.tokens_used || 0;
      modelBreakdown[t.model_used].cost += t.cost || 0;
    });

    return {
      totalTasks,
      totalTokens,
      totalCost: parseFloat(totalCost.toFixed(4)),
      successRate: parseFloat(successRate.toFixed(2)),
      avgDuration: Math.round(avgDuration),
      modelBreakdown,
      timeRange: '24 hours'
    };
  } catch (err) {
    console.error('Exception in calculateMetrics:', err.message);
    return {};
  }
}

/**
 * Send email via Mailgun
 * @param {Object} email - Email object
 * @param {string} email.to - Recipient email
 * @param {string} email.subject - Email subject
 * @param {string} email.html - HTML body
 * @param {string} [email.text] - Text body (optional)
 * @param {string} [email.from] - From address (default: noreply@domain)
 * @returns {Promise<Object>} Mailgun response
 */
async function sendEmail(email) {
  if (!MAILGUN_API_KEY || !MAILGUN_DOMAIN) {
    console.warn('⚠️  Mailgun not configured. Email not sent.');
    return null;
  }

  return new Promise((resolve) => {
    const from = email.from || `noreply@${MAILGUN_DOMAIN}`;
    const auth = Buffer.from(`api:${MAILGUN_API_KEY}`).toString('base64');

    const postData = new URLSearchParams();
    postData.append('from', from);
    postData.append('to', email.to);
    postData.append('subject', email.subject);
    postData.append('html', email.html);
    if (email.text) postData.append('text', email.text);

    const options = {
      hostname: 'api.mailgun.net',
      path: `/v3/${MAILGUN_DOMAIN}/messages`,
      method: 'POST',
      headers: {
        Authorization: `Basic ${auth}`,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': Buffer.byteLength(postData.toString())
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => (body += chunk));
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          console.log(`✅ Email sent to ${email.to}`);
          resolve(JSON.parse(body));
        } else {
          console.error(`❌ Mailgun error (${res.statusCode}):`, body);
          resolve(null);
        }
      });
    });

    req.on('error', (err) => {
      console.error('❌ Mailgun request error:', err.message);
      resolve(null);
    });

    req.write(postData.toString());
    req.end();
  });
}

/**
 * Send daily summary email
 * @param {string} toEmail - Recipient email
 * @returns {Promise<Object>} Mailgun response
 */
async function sendDailySummary(toEmail) {
  const metrics = await calculateMetrics();

  const html = `
    <h2>🤖 Agent Performance Summary (Last 24 Hours)</h2>
    <table border="1" cellpadding="10">
      <tr><td><strong>Total Tasks</strong></td><td>${metrics.totalTasks || 0}</td></tr>
      <tr><td><strong>Total Tokens Used</strong></td><td>${metrics.totalTokens || 0}</td></tr>
      <tr><td><strong>Total Cost</strong></td><td>$${metrics.totalCost || '0.00'}</td></tr>
      <tr><td><strong>Success Rate</strong></td><td>${metrics.successRate || 0}%</td></tr>
      <tr><td><strong>Avg Duration</strong></td><td>${metrics.avgDuration || 0}ms</td></tr>
    </table>
    
    <h3>Model Breakdown</h3>
    <ul>
      ${Object.entries(metrics.modelBreakdown || {})
        .map(([model, data]) => `<li>${model}: ${data.count} tasks, ${data.tokens} tokens, $${data.cost.toFixed(4)}</li>`)
        .join('')}
    </ul>
    
    <p><small>Generated at ${new Date().toISOString()}</small></p>
  `;

  return sendEmail({
    to: toEmail,
    subject: '📊 Agent Performance Summary',
    html,
    text: `Agent Summary: ${metrics.totalTasks} tasks, ${metrics.totalTokens} tokens, $${metrics.totalCost}`
  });
}

/**
 * Export dashboard data as JSON
 * @returns {Promise<Object>} Full dashboard data
 */
async function exportDashboardData() {
  const metrics = await calculateMetrics();
  const tasks = await getRecentTasks(1000);
  
  return {
    metrics,
    recentTasks: tasks,
    exportedAt: new Date().toISOString()
  };
}

module.exports = {
  supabase,
  logTask,
  saveMemory,
  getRecentTasks,
  calculateMetrics,
  sendEmail,
  sendDailySummary,
  exportDashboardData
};
