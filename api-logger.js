#!/usr/bin/env node

/**
 * API Logger — Every API call gets logged here
 * Used by: Printify sync, Etsy sync, YouTube batch upload, X organic (if API), Gumroad webhook
 * 
 * Usage:
 * const logger = require('./api-logger.js');
 * logger.logCall('Printify', 'GET /products', 0.05, 'batch-sync');
 * logger.logCall('Etsy', 'PUT /listings', 0.10, 'inventory-sync');
 * 
 * Output: .cache/api-call-log.jsonl (append-only)
 */

const fs = require('fs');
const path = require('path');

const CACHE_DIR = path.join(__dirname, '.cache');
const LOG_FILE = path.join(CACHE_DIR, 'api-call-log.jsonl');
const SPEND_FILE = path.join(CACHE_DIR, 'api-spend-daily.json');

/**
 * Log an API call
 * @param {string} service - Service name (Printify, Etsy, X, YouTube, Gumroad)
 * @param {string} endpoint - API endpoint (e.g., 'GET /products')
 * @param {number} cost - Cost in USD
 * @param {string} purpose - Why this call was made (e.g., 'batch-sync', 'order-check')
 * @param {object} metadata - Optional metadata (status, items_affected, etc.)
 */
function logCall(service, endpoint, cost, purpose, metadata = {}) {
  const now = new Date();
  const entry = {
    timestamp: now.toISOString(),
    service,
    endpoint,
    cost,
    purpose,
    metadata,
    date: now.toISOString().split('T')[0], // YYYY-MM-DD
  };

  // Append to log file
  try {
    fs.appendFileSync(LOG_FILE, JSON.stringify(entry) + '\n');
    console.log(`[API LOG] ${service} ${endpoint} (+$${cost.toFixed(4)}) — ${purpose}`);
  } catch (err) {
    console.error(`Failed to log API call: ${err.message}`);
  }

  // Update daily spend
  updateDailySpend(service, cost, now.toISOString().split('T')[0]);
}

/**
 * Update cumulative daily spend for a service
 */
function updateDailySpend(service, cost, date) {
  try {
    let spending = {};
    if (fs.existsSync(SPEND_FILE)) {
      spending = JSON.parse(fs.readFileSync(SPEND_FILE, 'utf8'));
    }

    // Initialize service if needed
    if (!spending[service]) {
      spending[service] = {};
    }

    // Add today's spend
    spending[service][date] = (spending[service][date] || 0) + cost;

    // Write back
    fs.writeFileSync(SPEND_FILE, JSON.stringify(spending, null, 2));
  } catch (err) {
    console.error(`Failed to update daily spend: ${err.message}`);
  }
}

/**
 * Get total spend for a service on a given date
 */
function getSpend(service, date) {
  try {
    const spending = JSON.parse(fs.readFileSync(SPEND_FILE, 'utf8'));
    return spending[service]?.[date] || 0;
  } catch {
    return 0;
  }
}

/**
 * Get monthly summary
 */
function getMonthlySummary(month) {
  // month format: 'YYYY-MM'
  try {
    const spending = JSON.parse(fs.readFileSync(SPEND_FILE, 'utf8'));
    const summary = {};

    for (const [service, dates] of Object.entries(spending)) {
      summary[service] = 0;
      for (const [date, cost] of Object.entries(dates)) {
        if (date.startsWith(month)) {
          summary[service] += cost;
        }
      }
    }

    return summary;
  } catch {
    return {};
  }
}

/**
 * Alert if service exceeds budget
 */
function checkBudget(service, date, budget) {
  const spend = getSpend(service, date);
  const percent = (spend / budget) * 100;

  if (percent >= 100) {
    console.error(`🚨 CRITICAL: ${service} spent $${spend.toFixed(2)} of $${budget} budget (${percent.toFixed(0)}%)`);
    return 'critical';
  } else if (percent >= 75) {
    console.warn(`⚠️  WARNING: ${service} spent $${spend.toFixed(2)} of $${budget} budget (${percent.toFixed(0)}%)`);
    return 'warning';
  } else if (percent >= 50) {
    console.log(`🟡 CAUTION: ${service} spent $${spend.toFixed(2)} of $${budget} budget (${percent.toFixed(0)}%)`);
    return 'caution';
  }

  return 'ok';
}

module.exports = {
  logCall,
  getSpend,
  getMonthlySummary,
  checkBudget,
};

// CLI Usage: node api-logger.js log <service> <endpoint> <cost> <purpose>
if (require.main === module) {
  const [, , command, service, endpoint, cost, purpose] = process.argv;

  if (command === 'log') {
    logCall(service, endpoint, parseFloat(cost), purpose);
  } else if (command === 'spend') {
    console.log(JSON.stringify(JSON.parse(fs.readFileSync(SPEND_FILE, 'utf8')), null, 2));
  } else if (command === 'check') {
    const [, , , svc, dt, bud] = process.argv;
    const status = checkBudget(svc, dt, parseFloat(bud));
    console.log(`Status: ${status}`);
  } else {
    console.log('Usage: node api-logger.js log <service> <endpoint> <cost> <purpose>');
    console.log('       node api-logger.js spend');
    console.log('       node api-logger.js check <service> <date> <budget>');
  }
}
