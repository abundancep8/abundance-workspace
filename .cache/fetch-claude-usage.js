#!/usr/bin/env node
/**
 * Fetch Claude API usage and cost tracking
 * Cron task: Runs periodically, logs to .cache/claude-usage.json
 * Alerts webhook if 75% of budget exceeded
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Configuration
const RATES = {
  input: 0.4 / 1_000_000,   // $0.4 per 1M input tokens
  output: 1.2 / 1_000_000,  // $1.2 per 1M output tokens
};

const BUDGET = {
  daily: 5.00,
  monthly: 155.00,
};

const ALERT_THRESHOLD = 0.75; // 75% of budget

const CACHE_DIR = path.join(process.cwd(), '.cache');
const CACHE_FILE = path.join(CACHE_DIR, 'claude-usage.json');

// Ensure cache directory exists
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

/**
 * Fetch usage from Anthropic console
 * TODO: Implement actual fetch mechanism
 * Options:
 * 1. Browser automation (Playwright/Puppeteer) + scraping
 * 2. Anthropic API endpoint (if available)
 * 3. Manual export via curl
 */
async function fetchUsageData() {
  // PLACEHOLDER: Replace with actual data source
  // For now, return mock data structure
  console.error('⚠️  Usage data fetch not implemented. Update this function with:');
  console.error('   - Browser automation (Playwright/Puppeteer)');
  console.error('   - Anthropic API call (if available)');
  console.error('   - Manual curl + auth');
  
  // Return empty structure for now
  return {
    tokens_today: 0,
    output_tokens_today: 0,
    input_tokens_today: 0,
    tokens_month: 0,
    output_tokens_month: 0,
    input_tokens_month: 0,
  };
}

/**
 * Calculate costs
 */
function calculateCosts(usageData) {
  const cost_today =
    usageData.input_tokens_today * RATES.input +
    usageData.output_tokens_today * RATES.output;

  const cost_month =
    usageData.input_tokens_month * RATES.input +
    usageData.output_tokens_month * RATES.output;

  return { cost_today, cost_month };
}

/**
 * Determine status
 */
function getStatus(cost_today, cost_month) {
  const daily_percent = (cost_today / BUDGET.daily) * 100;
  const monthly_percent = (cost_month / BUDGET.monthly) * 100;

  if (cost_today > BUDGET.daily * ALERT_THRESHOLD) {
    return `ALERT_DAILY (${daily_percent.toFixed(1)}%)`;
  }
  if (cost_month > BUDGET.monthly * ALERT_THRESHOLD) {
    return `ALERT_MONTHLY (${monthly_percent.toFixed(1)}%)`;
  }

  return `OK (Daily: ${daily_percent.toFixed(1)}% | Monthly: ${monthly_percent.toFixed(1)}%)`;
}

/**
 * Post alert to webhook
 */
async function postWebhookAlert(data) {
  const webhookUrl = process.env.WEBHOOK_MONITOR_URL;
  if (!webhookUrl) {
    console.error('❌ WEBHOOK_MONITOR_URL not set. Skipping webhook.');
    return;
  }

  const payload = JSON.stringify({
    alert_type: data.status.split('(')[0].trim(),
    timestamp: data.timestamp,
    cost_today: data.cost_today,
    budget_daily: data.budget_daily,
    daily_percent: ((data.cost_today / data.budget_daily) * 100).toFixed(1),
    cost_month: data.cost_month,
    budget_monthly: data.budget_monthly,
    monthly_percent: ((data.cost_month / data.budget_monthly) * 100).toFixed(1),
  });

  return new Promise((resolve, reject) => {
    const options = {
      hostname: new URL(webhookUrl).hostname,
      path: new URL(webhookUrl).pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': payload.length,
      },
    };

    const req = https.request(options, (res) => {
      console.log(`✅ Webhook posted (${res.statusCode})`);
      resolve();
    });

    req.on('error', (err) => {
      console.error('❌ Webhook failed:', err.message);
      reject(err);
    });

    req.write(payload);
    req.end();
  });
}

/**
 * Main
 */
async function main() {
  try {
    console.log('📊 Fetching Claude API usage...');
    const usageData = await fetchUsageData();

    const { cost_today, cost_month } = calculateCosts(usageData);
    const status = getStatus(cost_today, cost_month);

    const logEntry = {
      timestamp: new Date().toISOString(),
      tokens_today: usageData.tokens_today,
      cost_today: parseFloat(cost_today.toFixed(4)),
      tokens_month: usageData.tokens_month,
      cost_month: parseFloat(cost_month.toFixed(4)),
      budget_daily: BUDGET.daily,
      budget_monthly: BUDGET.monthly,
      status,
    };

    // Log to file
    fs.writeFileSync(CACHE_FILE, JSON.stringify(logEntry, null, 2));
    console.log(`✅ Logged to ${CACHE_FILE}`);
    console.log(`   Status: ${status}`);
    console.log(`   Cost Today: $${cost_today.toFixed(2)} / $${BUDGET.daily}`);
    console.log(`   Cost Month: $${cost_month.toFixed(2)} / $${BUDGET.monthly}`);

    // Trigger webhook if over threshold
    const daily_alert = cost_today > BUDGET.daily * ALERT_THRESHOLD;
    const monthly_alert = cost_month > BUDGET.monthly * ALERT_THRESHOLD;

    if (daily_alert || monthly_alert) {
      console.log('🚨 Budget threshold exceeded. Posting webhook alert...');
      await postWebhookAlert(logEntry);
    }
  } catch (err) {
    console.error('❌ Error:', err.message);
    process.exit(1);
  }
}

main();
