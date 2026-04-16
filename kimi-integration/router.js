#!/usr/bin/env node

/**
 * KIMI K2.5 Router
 * Smart task routing between Kimi K2.5 (cost-optimized) and Claude (quality-critical)
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY || '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';
const LOG_FILE = path.join(__dirname, 'logs', 'performance.jsonl');
const MODELS = {
  kimi: 'kimi/k2.5',
  claude: 'anthropic/claude-3.5-sonnet'
};

// Ensure log file exists
if (!fs.existsSync(LOG_FILE)) {
  fs.writeFileSync(LOG_FILE, '');
}

/**
 * Determine which model to use based on task characteristics
 */
function routeTask(task) {
  const {
    type = 'general',
    estimatedTokens = 0,
    timeSensitive = false,
    qualityCritical = false,
    taskName = 'unknown'
  } = task;

  // Always keep on Claude: Discord, real-time, quality-critical
  if (timeSensitive || qualityCritical || type === 'discord' || type === 'jarvis') {
    return { model: 'claude', reason: 'Quality/real-time requirement' };
  }

  // Route to Kimi: Research, batch, long-context, cost-sensitive
  const routeToKimi = 
    type === 'research' ||
    type === 'batch_processing' ||
    type === 'long_context' ||
    estimatedTokens > 10000;

  if (routeToKimi) {
    return { 
      model: 'kimi', 
      reason: `${type} task${estimatedTokens > 10000 ? ' (>10k tokens)' : ''}` 
    };
  }

  // Default to Claude for general tasks
  return { model: 'claude', reason: 'General task (default)' };
}

/**
 * Log performance metrics after task execution
 */
function logPerformance(taskName, model, inputTokens, outputTokens, executionTimeMs, success) {
  const record = {
    timestamp: new Date().toISOString(),
    taskName,
    model,
    inputTokens,
    outputTokens,
    totalTokens: inputTokens + outputTokens,
    executionTimeMs,
    success,
    cost: calculateCost(model, inputTokens, outputTokens)
  };

  fs.appendFileSync(LOG_FILE, JSON.stringify(record) + '\n');
  return record;
}

/**
 * Calculate cost per task
 * Kimi K2.5: $0.14/M input, $0.42/M output (via OpenRouter)
 * Claude 3.5 Sonnet: $3/M input, $15/M output (via OpenRouter)
 */
function calculateCost(model, inputTokens, outputTokens) {
  const costs = {
    kimi: { input: 0.00014, output: 0.00042 },
    claude: { input: 0.003, output: 0.015 }
  };
  
  const modelCosts = costs[model.includes('kimi') ? 'kimi' : 'claude'];
  return (inputTokens * modelCosts.input) + (outputTokens * modelCosts.output);
}

/**
 * Call OpenRouter API
 */
async function callOpenRouter(messages, model, maxTokens = 2000) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify({
      model: MODELS[model] || model,
      messages,
      max_tokens: maxTokens,
      temperature: 0.7
    });

    const options = {
      hostname: 'openrouter.io',
      port: 443,
      path: '/api/v1/chat/completions',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'HTTP-Referer': 'https://openclaw.io',
        'X-Title': 'OpenClaw Kimi Integration',
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload)
      }
    };

    const startTime = Date.now();
    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', chunk => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          
          if (response.error) {
            reject(new Error(`API Error: ${response.error.message}`));
            return;
          }

          const executionTimeMs = Date.now() - startTime;
          resolve({
            content: response.choices[0].message.content,
            inputTokens: response.usage.prompt_tokens,
            outputTokens: response.usage.completion_tokens,
            executionTimeMs,
            model: response.model
          });
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(payload);
    req.end();
  });
}

/**
 * Execute task with automatic routing
 */
async function executeTask(task) {
  const { taskName = 'unknown', messages, maxTokens = 2000, ...taskAttrs } = task;
  
  // Route the task
  const routing = routeTask({ ...taskAttrs, taskName });
  const model = routing.model;

  try {
    console.log(`[${taskName}] Routing to ${model.toUpperCase()} - ${routing.reason}`);

    // Call the appropriate model
    const result = await callOpenRouter(messages, model, maxTokens);

    // Log performance
    const logEntry = logPerformance(
      taskName,
      model,
      result.inputTokens,
      result.outputTokens,
      result.executionTimeMs,
      true
    );

    console.log(`[${taskName}] ✓ Complete in ${logEntry.executionTimeMs}ms | Cost: $${logEntry.cost.toFixed(5)}`);

    return {
      success: true,
      model,
      content: result.content,
      tokens: { input: result.inputTokens, output: result.outputTokens },
      cost: logEntry.cost,
      executionTimeMs: result.executionTimeMs
    };
  } catch (error) {
    logPerformance(taskName, model, 0, 0, 0, false);
    console.error(`[${taskName}] ✗ Failed:`, error.message);
    throw error;
  }
}

/**
 * Generate performance report
 */
function generateReport() {
  if (!fs.existsSync(LOG_FILE)) {
    return { totalTasks: 0, summary: 'No data' };
  }

  const lines = fs.readFileSync(LOG_FILE, 'utf-8').trim().split('\n').filter(Boolean);
  const records = lines.map(line => JSON.parse(line));

  if (records.length === 0) {
    return { totalTasks: 0, summary: 'No data' };
  }

  const byModel = {};
  let totalCost = 0;
  let totalTokens = 0;

  records.forEach(r => {
    if (!byModel[r.model]) {
      byModel[r.model] = { tasks: 0, totalTokens: 0, totalCost: 0, avgTime: 0, times: [] };
    }
    byModel[r.model].tasks++;
    byModel[r.model].totalTokens += r.totalTokens;
    byModel[r.model].totalCost += r.cost;
    byModel[r.model].times.push(r.executionTimeMs);
    totalCost += r.cost;
    totalTokens += r.totalTokens;
  });

  // Calculate averages
  Object.keys(byModel).forEach(model => {
    byModel[model].avgTime = byModel[model].times.length > 0
      ? Math.round(byModel[model].times.reduce((a, b) => a + b, 0) / byModel[model].times.length)
      : 0;
  });

  return {
    totalTasks: records.length,
    totalTokens,
    totalCost: parseFloat(totalCost.toFixed(5)),
    byModel,
    estimatedDailyCost: parseFloat((totalCost * 24).toFixed(5)), // Rough estimate
    records: records.slice(-10) // Last 10 records
  };
}

module.exports = {
  routeTask,
  executeTask,
  callOpenRouter,
  logPerformance,
  generateReport,
  calculateCost
};

// CLI usage
if (require.main === module) {
  const command = process.argv[2];

  if (command === 'report') {
    const report = generateReport();
    console.log('\n=== PERFORMANCE REPORT ===');
    console.log(JSON.stringify(report, null, 2));
  } else if (command === 'test') {
    console.log('Run: node tests/test-suite.js');
  } else {
    console.log('Usage: node router.js [report|test]');
  }
}
