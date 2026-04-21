#!/usr/bin/env node

/**
 * Claude API Usage Monitor
 * Tracks daily/monthly costs and alerts when thresholds are exceeded
 * 
 * Haiku rates (April 2026):
 * - Input:  $0.40 per 1M tokens
 * - Output: $1.20 per 1M tokens
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Config
const CACHE_DIR = path.join(__dirname);
const USAGE_FILE = path.join(CACHE_DIR, 'claude-usage.json');
const WEBHOOK_URL = process.env.WEBHOOK_MONITOR || null;

const HAIKU_RATES = {
  input: 0.40 / 1_000_000,   // $0.40 per 1M
  output: 1.20 / 1_000_000   // $1.20 per 1M
};

const BUDGETS = {
  daily: 5.00,
  monthly: 155.00,
  alert_threshold: 0.75 // Alert at 75% of budget
};

/**
 * Parse usage data from Anthropic console
 * Expected input format:
 * {
 *   tokens_today: { input: 1000, output: 5000 },
 *   tokens_month: { input: 50000, output: 250000 }
 * }
 */
function calculateCosts(tokensInput, tokensOutput) {
  return {
    input_cost: tokensInput * HAIKU_RATES.input,
    output_cost: tokensOutput * HAIKU_RATES.output,
    total_cost: (tokensInput * HAIKU_RATES.input) + (tokensOutput * HAIKU_RATES.output)
  };
}

function updateUsage(todayData, monthData) {
  const timestamp = new Date().toISOString();
  
  const costToday = calculateCosts(
    todayData.input || 0,
    todayData.output || 0
  );
  
  const costMonth = calculateCosts(
    monthData.input || 0,
    monthData.output || 0
  );

  const dailyPercent = (costToday.total_cost / BUDGETS.daily) * 100;
  const monthlyPercent = (costMonth.total_cost / BUDGETS.monthly) * 100;

  let status = 'OK';
  let alert = false;

  if (costToday.total_cost > (BUDGETS.daily * BUDGETS.alert_threshold)) {
    status = 'ALERT_DAILY';
    alert = true;
  } else if (costMonth.total_cost > (BUDGETS.monthly * BUDGETS.alert_threshold)) {
    status = 'ALERT_MONTHLY';
    alert = true;
  }

  const record = {
    timestamp,
    tokens_today: { input: todayData.input || 0, output: todayData.output || 0 },
    cost_today: parseFloat(costToday.total_cost.toFixed(4)),
    percent_daily: parseFloat(dailyPercent.toFixed(2)),
    tokens_month: { input: monthData.input || 0, output: monthData.output || 0 },
    cost_month: parseFloat(costMonth.total_cost.toFixed(4)),
    percent_monthly: parseFloat(monthlyPercent.toFixed(2)),
    budget_daily: BUDGETS.daily,
    budget_monthly: BUDGETS.monthly,
    alert_threshold: BUDGETS.alert_threshold * 100,
    status
  };

  // Write log
  fs.writeFileSync(USAGE_FILE, JSON.stringify(record, null, 2));
  console.log(`[${timestamp}] Usage logged: ${status}`);
  console.log(`  Daily: $${record.cost_today.toFixed(2)} / $${BUDGETS.daily} (${record.percent_daily}%)`);
  console.log(`  Monthly: $${record.cost_month.toFixed(2)} / $${BUDGETS.monthly} (${record.percent_monthly}%)`);

  // Trigger webhook if alert
  if (alert && WEBHOOK_URL) {
    sendWebhookAlert(record);
  }

  return record;
}

function sendWebhookAlert(record) {
  const payload = JSON.stringify({
    type: 'claude-api-budget-alert',
    severity: record.status === 'ALERT_DAILY' ? 'critical' : 'warning',
    message: `Claude API usage at ${record.percent_daily}% daily / ${record.percent_monthly}% monthly`,
    data: record,
    timestamp: new Date().toISOString()
  });

  const options = {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': payload.length
    }
  };

  const req = https.request(WEBHOOK_URL, options, (res) => {
    console.log(`[WEBHOOK] Status: ${res.statusCode}`);
  });

  req.on('error', (err) => {
    console.error(`[WEBHOOK] Error: ${err.message}`);
  });

  req.write(payload);
  req.end();
}

/**
 * Main entry point
 * 
 * Usage from cron:
 * node .cache/claude-usage-monitor.js --today-input 1000 --today-output 5000 --month-input 50000 --month-output 250000
 */
function main() {
  const args = process.argv.slice(2);
  
  let todayInput = 0, todayOutput = 0, monthInput = 0, monthOutput = 0;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--today-input') todayInput = parseInt(args[++i], 10);
    if (args[i] === '--today-output') todayOutput = parseInt(args[++i], 10);
    if (args[i] === '--month-input') monthInput = parseInt(args[++i], 10);
    if (args[i] === '--month-output') monthOutput = parseInt(args[++i], 10);
  }

  if (!todayInput && !todayOutput && !monthInput && !monthOutput) {
    console.error('No usage data provided. Usage:');
    console.error('  node claude-usage-monitor.js --today-input N --today-output N --month-input N --month-output N');
    process.exit(1);
  }

  updateUsage(
    { input: todayInput, output: todayOutput },
    { input: monthInput, output: monthOutput }
  );
}

if (require.main === module) {
  main();
}

module.exports = { updateUsage, calculateCosts, HAIKU_RATES, BUDGETS };
