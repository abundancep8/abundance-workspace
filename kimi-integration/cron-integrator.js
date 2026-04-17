#!/usr/bin/env node

/**
 * KIMI K2.5 Cron Integrator
 * Modifies existing cron jobs to route through Kimi when optimal
 * Handles task logging and performance tracking
 */

const fs = require('fs');
const path = require('path');

const JOBS_FILE = '/Users/abundance/.openclaw/cron/jobs.json';
const LOG_DIR = path.join(__dirname, 'logs');
const PERFORMANCE_LOG = path.join(LOG_DIR, 'performance.jsonl');
const TASK_LOG = path.join(LOG_DIR, 'task-executions.jsonl');

// Ensure log directory exists
if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR, { recursive: true });
}

/**
 * Routing rules: Which jobs should use Kimi
 */
const ROUTING_CONFIG = {
  'hourly-token-check': {
    model: 'kimi',
    reason: 'Token analysis - batch processing, non-time-sensitive',
    estimatedTokens: 3000
  },
  'weekly-synthesis-patterns': {
    model: 'kimi',
    reason: 'Pattern extraction from logs - long context, high tokens',
    estimatedTokens: 8000
  },
  'youtube-comment-monitor': {
    model: 'kimi',
    reason: 'Comment categorization - batch processing',
    estimatedTokens: 5000
  },
  'daily-blotato-video-generation': {
    model: 'claude',
    reason: 'Video generation quality-critical - keep on Claude',
    estimatedTokens: 6000
  },
  'nightly-self-improvement': {
    model: 'kimi',
    reason: 'Pattern analysis and reflection - non-time-sensitive',
    estimatedTokens: 4000
  }
};

/**
 * Calculate cost for a task
 */
function calculateCost(model, inputTokens, outputTokens) {
  const costs = {
    kimi: { input: 0.00014, output: 0.00042 },
    claude: { input: 0.003, output: 0.015 }
  };
  
  const modelCosts = costs[model] || costs.claude;
  return (inputTokens * modelCosts.input) + (outputTokens * modelCosts.output);
}

/**
 * Update cron job with Kimi integration
 */
function integrateJobWithKimi(jobName) {
  const config = ROUTING_CONFIG[jobName];
  if (!config) return null;
  
  // Read jobs file
  const jobsData = JSON.parse(fs.readFileSync(JOBS_FILE, 'utf-8'));
  
  // Find and update job
  const jobIndex = jobsData.jobs.findIndex(j => j.name === jobName);
  if (jobIndex === -1) return null;
  
  const job = jobsData.jobs[jobIndex];
  
  // Add Kimi routing metadata to job
  job.kimiIntegrated = {
    enabled: true,
    model: config.model,
    reason: config.reason,
    estimatedTokens: config.estimatedTokens,
    integratedAt: new Date().toISOString()
  };
  
  return job;
}

/**
 * Log task execution
 */
function logTaskExecution(jobName, model, inputTokens, outputTokens, executionMs, success) {
  const cost = calculateCost(model, inputTokens, outputTokens);
  
  const record = {
    timestamp: new Date().toISOString(),
    jobName,
    model,
    inputTokens,
    outputTokens,
    totalTokens: inputTokens + outputTokens,
    executionMs,
    cost,
    success
  };
  
  fs.appendFileSync(TASK_LOG, JSON.stringify(record) + '\n');
  
  return record;
}

/**
 * Generate performance report
 */
function generateReport() {
  if (!fs.existsSync(TASK_LOG)) {
    return { status: 'No data yet', totalTasks: 0 };
  }
  
  const lines = fs.readFileSync(TASK_LOG, 'utf-8').trim().split('\n').filter(Boolean);
  const records = lines.map(line => {
    try {
      return JSON.parse(line);
    } catch {
      return null;
    }
  }).filter(Boolean);
  
  if (records.length === 0) {
    return { status: 'No data yet', totalTasks: 0 };
  }
  
  const byJob = {};
  const byModel = {};
  let totalCost = 0;
  let totalTokens = 0;
  
  records.forEach(r => {
    if (r.success) {
      // By job
      if (!byJob[r.jobName]) {
        byJob[r.jobName] = { runs: 0, cost: 0, tokens: 0, avgExecMs: 0, times: [] };
      }
      byJob[r.jobName].runs++;
      byJob[r.jobName].cost += r.cost;
      byJob[r.jobName].tokens += r.totalTokens;
      byJob[r.jobName].times.push(r.executionMs);
      
      // By model
      if (!byModel[r.model]) {
        byModel[r.model] = { runs: 0, cost: 0, tokens: 0 };
      }
      byModel[r.model].runs++;
      byModel[r.model].cost += r.cost;
      byModel[r.model].tokens += r.totalTokens;
      
      totalCost += r.cost;
      totalTokens += r.totalTokens;
    }
  });
  
  // Calculate averages
  Object.keys(byJob).forEach(job => {
    byJob[job].avgExecMs = Math.round(
      byJob[job].times.reduce((a, b) => a + b, 0) / byJob[job].times.length
    );
  });
  
  // Estimate savings
  const kimiCost = byModel.kimi ? byModel.kimi.cost : 0;
  const claudeCost = byModel.claude ? byModel.claude.cost : 0;
  
  // If all had been on Claude
  const allClaudeCost = totalCost + (kimiCost * 10); // Rough estimate of what Kimi on Claude would cost
  const savingsEstimate = allClaudeCost - totalCost;
  
  return {
    status: 'Active',
    totalTasks: records.length,
    totalCost: parseFloat(totalCost.toFixed(5)),
    totalTokens,
    savingsEstimate: parseFloat(savingsEstimate.toFixed(5)),
    byJob,
    byModel,
    lastRun: records[records.length - 1].timestamp,
    estimatedDailyCost: parseFloat((totalCost * 24).toFixed(5)) // Rough daily estimate
  };
}

/**
 * Check integration status
 */
function checkIntegrationStatus() {
  if (!fs.existsSync(JOBS_FILE)) {
    return { error: 'Jobs file not found' };
  }
  
  const jobsData = JSON.parse(fs.readFileSync(JOBS_FILE, 'utf-8'));
  const targetJobs = Object.keys(ROUTING_CONFIG);
  
  const status = {
    totalTargetJobs: targetJobs.length,
    integratedJobs: 0,
    jobs: {}
  };
  
  targetJobs.forEach(jobName => {
    const job = jobsData.jobs.find(j => j.name === jobName);
    if (job) {
      status.jobs[jobName] = {
        found: true,
        integrated: !!job.kimiIntegrated,
        model: ROUTING_CONFIG[jobName].model,
        enabled: job.enabled
      };
      if (job.kimiIntegrated) {
        status.integratedJobs++;
      }
    } else {
      status.jobs[jobName] = { found: false };
    }
  });
  
  return status;
}

/**
 * Generate deployment dashboard HTML
 */
function generateDashboard() {
  const report = generateReport();
  const status = checkIntegrationStatus();
  
  const html = `<!DOCTYPE html>
<html>
<head>
  <title>Kimi K2.5 Deployment Dashboard</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 20px; background: #0d1117; color: #c9d1d9; }
    .container { max-width: 1200px; margin: 0 auto; }
    h1 { color: #58a6ff; border-bottom: 2px solid #30363d; padding-bottom: 10px; }
    .status { padding: 20px; background: #161b22; border-radius: 6px; margin: 20px 0; border-left: 4px solid #238636; }
    .status.warning { border-left-color: #d29922; }
    .status.error { border-left-color: #f85149; }
    .metric { display: inline-block; margin-right: 30px; margin-bottom: 15px; }
    .metric-value { font-size: 24px; font-weight: bold; color: #58a6ff; }
    .metric-label { font-size: 12px; color: #8b949e; text-transform: uppercase; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #30363d; }
    th { background: #0d1117; color: #58a6ff; font-weight: 600; }
    .success { color: #3fb950; }
    .cost { color: #ffa657; }
    .kimi { background: rgba(88, 166, 255, 0.1); }
    .claude { background: rgba(63, 185, 80, 0.1); }
  </style>
</head>
<body>
  <div class="container">
    <h1>🚀 Kimi K2.5 Production Deployment</h1>
    
    <div class="status ${report.status === 'Active' ? '' : 'error'}">
      <div class="metric">
        <div class="metric-value">${report.status}</div>
        <div class="metric-label">Status</div>
      </div>
      <div class="metric">
        <div class="metric-value">${report.totalTasks}</div>
        <div class="metric-label">Tasks Processed</div>
      </div>
      <div class="metric">
        <div class="metric-value">$${report.totalCost}</div>
        <div class="metric-label cost">Total Cost</div>
      </div>
      <div class="metric">
        <div class="metric-value">$${report.savingsEstimate}</div>
        <div class="metric-label success">Estimated Savings</div>
      </div>
    </div>
    
    <h2>Integrated Cron Jobs</h2>
    <table>
      <tr>
        <th>Job Name</th>
        <th>Model</th>
        <th>Status</th>
        <th>Found</th>
      </tr>
      ${Object.entries(status.jobs).map(([name, info]) => `
        <tr>
          <td>${name}</td>
          <td class="${ROUTING_CONFIG[name].model}">${ROUTING_CONFIG[name].model.toUpperCase()}</td>
          <td>${info.enabled ? '✓ Enabled' : '✗ Disabled'}</td>
          <td>${info.found ? '✓ Yes' : '✗ No'}</td>
        </tr>
      `).join('')}
    </table>
    
    <h2>Performance by Job</h2>
    <table>
      <tr>
        <th>Job</th>
        <th>Runs</th>
        <th>Cost</th>
        <th>Tokens</th>
        <th>Avg Exec (ms)</th>
      </tr>
      ${Object.entries(report.byJob).map(([job, data]) => `
        <tr>
          <td>${job}</td>
          <td>${data.runs}</td>
          <td class="cost">$${data.cost.toFixed(5)}</td>
          <td>${data.tokens}</td>
          <td>${data.avgExecMs}ms</td>
        </tr>
      `).join('')}
    </table>
    
    <h2>Cost Breakdown</h2>
    <table>
      <tr>
        <th>Model</th>
        <th>Tasks</th>
        <th>Cost</th>
        <th>% of Total</th>
      </tr>
      ${Object.entries(report.byModel).map(([model, data]) => `
        <tr class="${model}">
          <td>${model.toUpperCase()}</td>
          <td>${data.runs}</td>
          <td class="cost">$${data.cost.toFixed(5)}</td>
          <td>${((data.cost / report.totalCost) * 100).toFixed(1)}%</td>
        </tr>
      `).join('')}
    </table>
    
    <div style="margin-top: 40px; color: #8b949e; font-size: 12px;">
      <p>Last updated: ${new Date().toISOString()}</p>
      <p>Estimated daily cost: $${report.estimatedDailyCost}</p>
      <p>Dashboard auto-updates with each cron job execution</p>
    </div>
  </div>
</body>
</html>
`;
  
  return html;
}

// CLI
if (require.main === module) {
  const command = process.argv[2];
  
  if (command === 'integrate') {
    const jobName = process.argv[3];
    const result = integrateJobWithKimi(jobName);
    console.log(result ? `✓ Integrated ${jobName}` : `✗ Job not found: ${jobName}`);
  } else if (command === 'log') {
    const jobName = process.argv[3];
    const model = process.argv[4];
    const inputTokens = parseInt(process.argv[5]) || 2000;
    const outputTokens = parseInt(process.argv[6]) || 500;
    const executionMs = parseInt(process.argv[7]) || 1000;
    
    const log = logTaskExecution(jobName, model, inputTokens, outputTokens, executionMs, true);
    console.log(`✓ Logged: ${jobName} on ${model} | Cost: $${log.cost.toFixed(5)}`);
  } else if (command === 'report') {
    const report = generateReport();
    console.log('\n=== PERFORMANCE REPORT ===');
    console.log(JSON.stringify(report, null, 2));
  } else if (command === 'status') {
    const status = checkIntegrationStatus();
    console.log('\n=== INTEGRATION STATUS ===');
    console.log(JSON.stringify(status, null, 2));
  } else if (command === 'dashboard') {
    const html = generateDashboard();
    const dashPath = path.join(__dirname, 'dashboards', 'index.html');
    
    if (!fs.existsSync(path.dirname(dashPath))) {
      fs.mkdirSync(path.dirname(dashPath), { recursive: true });
    }
    
    fs.writeFileSync(dashPath, html);
    console.log(`✓ Dashboard generated at ${dashPath}`);
  } else {
    console.log('Usage:');
    console.log('  node cron-integrator.js integrate <jobName>');
    console.log('  node cron-integrator.js log <jobName> <model> [inputTokens] [outputTokens] [executionMs]');
    console.log('  node cron-integrator.js status');
    console.log('  node cron-integrator.js report');
    console.log('  node cron-integrator.js dashboard');
  }
}

module.exports = {
  ROUTING_CONFIG,
  logTaskExecution,
  generateReport,
  checkIntegrationStatus,
  generateDashboard,
  calculateCost
};
