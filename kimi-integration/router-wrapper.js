#!/usr/bin/env node

/**
 * KIMI K2.5 Router Wrapper
 * Integrates Kimi routing into existing cron jobs via OpenRouter API
 * Accepts agentTurn payloads from OpenClaw cron system and routes to Kimi when optimal
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const router = require('./router.js');

const KIMI_ROUTER_ENABLED = process.env.KIMI_ROUTER_ENABLED !== 'false';
const LOG_FILE = path.join(__dirname, 'logs', 'performance.jsonl');
const TASK_LOG_FILE = path.join(__dirname, 'logs', 'task-executions.jsonl');

// Ensure log directories exist
['logs'].forEach(dir => {
  const fullPath = path.join(__dirname, dir);
  if (!fs.existsSync(fullPath)) {
    fs.mkdirSync(fullPath, { recursive: true });
  }
});

/**
 * Determine if we should route a cron job task to Kimi
 */
function shouldRouteToKimi(jobName, taskDescription) {
  const kimiOptimal = {
    // Analysis tasks (high tokens, non-time-sensitive)
    'weekly-synthesis-patterns': true,
    'nightly-self-improvement': true,
    'hourly-token-check': true,
    'youtube-comment-monitor': true,
    'daily-blotato-video-generation': false, // Keep on Claude for generation quality
  };

  return kimiOptimal[jobName] === true;
}

/**
 * Execute a cron job task with router
 */
async function executeCronTask(jobName, taskMessage, estimatedTokens = 5000) {
  const startTime = Date.now();
  
  try {
    // Determine routing
    const shouldRoute = shouldRouteToKimi(jobName, taskMessage);
    const model = shouldRoute ? 'kimi' : 'claude';
    
    console.log(`[CRON:${jobName}] Starting | Model: ${model.toUpperCase()}`);
    
    // Create task for router
    const task = {
      taskName: jobName,
      type: 'batch_processing',
      estimatedTokens: estimatedTokens,
      timeSensitive: false,
      qualityCritical: jobName.includes('blotato') || jobName.includes('youtube-dm'),
      messages: [
        {
          role: 'user',
          content: taskMessage
        }
      ],
      maxTokens: 2000
    };
    
    // Execute with router
    const result = await router.executeTask(task);
    
    const executionTimeMs = Date.now() - startTime;
    
    // Log task execution
    const taskLog = {
      timestamp: new Date().toISOString(),
      jobName,
      model: result.model,
      success: result.success,
      tokens: result.tokens,
      cost: result.cost,
      executionTimeMs,
      contentLength: result.content ? result.content.length : 0
    };
    
    fs.appendFileSync(TASK_LOG_FILE, JSON.stringify(taskLog) + '\n');
    
    console.log(`[CRON:${jobName}] ✓ Complete in ${executionTimeMs}ms | Model: ${result.model} | Cost: $${result.cost.toFixed(5)}`);
    
    return {
      success: true,
      model: result.model,
      output: result.content,
      cost: result.cost,
      tokens: result.tokens,
      executionTimeMs
    };
    
  } catch (error) {
    const executionTimeMs = Date.now() - startTime;
    
    // Log failure
    const taskLog = {
      timestamp: new Date().toISOString(),
      jobName,
      success: false,
      error: error.message,
      executionTimeMs
    };
    
    fs.appendFileSync(TASK_LOG_FILE, JSON.stringify(taskLog) + '\n');
    
    console.error(`[CRON:${jobName}] ✗ Failed in ${executionTimeMs}ms: ${error.message}`);
    
    throw error;
  }
}

/**
 * Process a queue of cron tasks (for batch execution)
 */
async function processCronQueue(tasks) {
  const results = [];
  let totalCost = 0;
  let totalTime = 0;
  
  for (const task of tasks) {
    try {
      const result = await executeCronTask(task.name, task.message, task.estimatedTokens);
      results.push(result);
      totalCost += result.cost;
      totalTime += result.executionTimeMs;
    } catch (err) {
      results.push({
        success: false,
        jobName: task.name,
        error: err.message
      });
    }
  }
  
  return {
    totalTasks: tasks.length,
    successCount: results.filter(r => r.success).length,
    totalCost,
    totalTime,
    avgTimeMs: Math.round(totalTime / results.length),
    results
  };
}

/**
 * Generate deployment status dashboard
 */
function generateDeploymentStatus() {
  if (!fs.existsSync(TASK_LOG_FILE)) {
    return { status: 'No data yet' };
  }
  
  const lines = fs.readFileSync(TASK_LOG_FILE, 'utf-8').trim().split('\n').filter(Boolean);
  const records = lines.map(line => JSON.parse(line));
  
  if (records.length === 0) {
    return { status: 'No data yet' };
  }
  
  const byJob = {};
  let totalCost = 0;
  
  records.forEach(r => {
    if (!byJob[r.jobName]) {
      byJob[r.jobName] = {
        runs: 0,
        successes: 0,
        failures: 0,
        totalCost: 0,
        models: {}
      };
    }
    
    byJob[r.jobName].runs++;
    if (r.success) {
      byJob[r.jobName].successes++;
      byJob[r.jobName].totalCost += r.cost || 0;
      totalCost += r.cost || 0;
      
      if (!byJob[r.jobName].models[r.model]) {
        byJob[r.jobName].models[r.model] = 0;
      }
      byJob[r.jobName].models[r.model]++;
    } else {
      byJob[r.jobName].failures++;
    }
  });
  
  return {
    deploymentActive: true,
    totalJobsRun: records.length,
    uniqueJobs: Object.keys(byJob).length,
    totalCost: parseFloat(totalCost.toFixed(5)),
    byJob,
    lastRun: records[records.length - 1].timestamp
  };
}

// Export for use in other modules
module.exports = {
  executeCronTask,
  processCronQueue,
  shouldRouteToKimi,
  generateDeploymentStatus
};

// CLI usage
if (require.main === module) {
  const command = process.argv[2];
  const jobName = process.argv[3];
  const taskMessage = process.argv[4];
  
  if (command === 'execute' && jobName && taskMessage) {
    executeCronTask(jobName, taskMessage).then(result => {
      console.log('\n=== EXECUTION RESULT ===');
      console.log(JSON.stringify(result, null, 2));
      process.exit(0);
    }).catch(err => {
      console.error('ERROR:', err.message);
      process.exit(1);
    });
  } else if (command === 'status') {
    const status = generateDeploymentStatus();
    console.log('\n=== KIMI K2.5 DEPLOYMENT STATUS ===');
    console.log(JSON.stringify(status, null, 2));
  } else {
    console.log('Usage:');
    console.log('  node router-wrapper.js execute <jobName> <taskMessage>');
    console.log('  node router-wrapper.js status');
  }
}
