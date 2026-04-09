#!/usr/bin/env node

/**
 * External API Webhook Monitor
 * Receives webhooks from all external APIs (Claude, OpenAI, X, Printify, Etsy, Gumroad, Stripe, YouTube)
 * Logs to .cache/external-api-events.jsonl
 * Triggers alerts if thresholds crossed
 * 
 * Usage: node webhook-monitor.js [--port 3000]
 */

const fs = require('fs');
const path = require('path');
const http = require('http');

const CACHE_DIR = path.join(__dirname, '.cache');
const EVENT_LOG = path.join(CACHE_DIR, 'external-api-events.jsonl');

// Budget thresholds (in dollars)
const BUDGETS = {
  'claude': { daily: 5.00, monthly: 155.00 },
  'openai': { daily: 50.00, monthly: 1000.00 }, // Placeholder, can be customized
  'x': { daily: 0, monthly: 0 }, // Organic mode
  'printify': { daily: 1.35, monthly: 40.00 },
  'etsy': { daily: 0.85, monthly: 25.00 },
  'gumroad': { daily: 0, monthly: 0 }, // Webhooks only
  'stripe': { daily: 0, monthly: 0 }, // Variable (% of revenue)
  'youtube': { daily: 0, monthly: 0 }, // Free tier
};

/**
 * Log an API event
 */
function logEvent(service, event, data = {}) {
  const entry = {
    timestamp: new Date().toISOString(),
    service,
    event,
    data,
  };

  try {
    fs.appendFileSync(EVENT_LOG, JSON.stringify(entry) + '\n');
    console.log(`[WEBHOOK] ${service} - ${event}`);
  } catch (err) {
    console.error(`Failed to log event: ${err.message}`);
  }

  return entry;
}

/**
 * Check if threshold is crossed and alert
 */
function checkThreshold(service, costToday, costMonth) {
  const budget = BUDGETS[service];
  if (!budget) return null;

  const dailyPercent = (costToday / budget.daily) * 100;
  const monthlyPercent = (costMonth / budget.monthly) * 100;

  let status = 'ok';
  if (dailyPercent >= 100 || monthlyPercent >= 100) {
    status = 'critical';
    console.error(`🔴 CRITICAL: ${service} exceeded budget!`);
  } else if (dailyPercent >= 75 || monthlyPercent >= 75) {
    status = 'warning';
    console.warn(`⚠️  WARNING: ${service} at ${Math.max(dailyPercent, monthlyPercent).toFixed(0)}% of budget`);
  } else if (dailyPercent >= 50 || monthlyPercent >= 50) {
    status = 'caution';
    console.log(`🟡 CAUTION: ${service} at ${Math.max(dailyPercent, monthlyPercent).toFixed(0)}% of budget`);
  }

  // If critical or warning, trigger Discord alert (would integrate with Discord API)
  if (status === 'critical' || status === 'warning') {
    alertProsperity(service, status, { dailyPercent, monthlyPercent, costToday, costMonth });
  }

  return status;
}

/**
 * Send alert to Prosperity (Discord integration)
 */
function alertProsperity(service, status, data) {
  // TODO: Integrate with Discord API to send alert to Prosperity
  // For now, just log it
  const message = `[ALERT] ${service.toUpperCase()} API - ${status.toUpperCase()}\n` +
    `Daily: ${data.costToday.toFixed(2)} (${data.dailyPercent.toFixed(0)}%)\n` +
    `Month: ${data.costMonth.toFixed(2)} (${data.monthlyPercent.toFixed(0)}%)`;
  
  console.log(`\n${'='.repeat(60)}`);
  console.log(message);
  console.log(`${'='.repeat(60)}\n`);
}

/**
 * HTTP Server for receiving webhooks
 */
function startServer(port = 3000) {
  const server = http.createServer(async (req, res) => {
    if (req.method === 'POST') {
      let body = '';

      req.on('data', chunk => {
        body += chunk.toString();
      });

      req.on('end', () => {
        try {
          const data = JSON.parse(body);
          const service = req.url.split('/')[2]; // /monitor/:service

          // Route to appropriate handler
          switch (service) {
            case 'claude':
              handleClaudeWebhook(data, res);
              break;
            case 'openai':
              handleOpenAIWebhook(data, res);
              break;
            case 'x':
              handleXWebhook(data, res);
              break;
            case 'printify':
              handlePrintifyWebhook(data, res);
              break;
            case 'etsy':
              handleEtsyWebhook(data, res);
              break;
            case 'gumroad':
              handleGumroadWebhook(data, res);
              break;
            case 'stripe':
              handleStripeWebhook(data, res);
              break;
            case 'youtube':
              handleYouTubeWebhook(data, res);
              break;
            default:
              res.writeHead(404);
              res.end('Unknown service');
          }
        } catch (err) {
          console.error(`Webhook error: ${err.message}`);
          res.writeHead(400);
          res.end('Invalid JSON');
        }
      });
    } else if (req.method === 'GET' && req.url === '/status') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'running', port }));
    } else {
      res.writeHead(404);
      res.end('Not found');
    }
  });

  server.listen(port, () => {
    console.log(`✅ Webhook monitor listening on port ${port}`);
    console.log(`   Claude:  POST http://localhost:${port}/monitor/claude`);
    console.log(`   OpenAI:  POST http://localhost:${port}/monitor/openai`);
    console.log(`   X:       POST http://localhost:${port}/monitor/x`);
    console.log(`   Printify: POST http://localhost:${port}/monitor/printify`);
    console.log(`   Etsy:    POST http://localhost:${port}/monitor/etsy`);
    console.log(`   Gumroad: POST http://localhost:${port}/monitor/gumroad`);
    console.log(`   Stripe:  POST http://localhost:${port}/monitor/stripe`);
    console.log(`   YouTube: POST http://localhost:${port}/monitor/youtube`);
  });
}

/**
 * Webhook Handlers
 */

function handleClaudeWebhook(data, res) {
  const { tokens_today, cost_today, cost_month } = data;
  logEvent('claude', 'usage_update', data);
  checkThreshold('claude', cost_today, cost_month);
  
  res.writeHead(200);
  res.end('OK');
}

function handleOpenAIWebhook(data, res) {
  const { cost_today, cost_month } = data;
  logEvent('openai', 'usage_update', data);
  checkThreshold('openai', cost_today || 0, cost_month || 0);
  
  res.writeHead(200);
  res.end('OK');
}

function handleXWebhook(data, res) {
  const { api_calls, cost_month } = data;
  logEvent('x', 'api_usage', data);
  if (cost_month > 0) {
    checkThreshold('x', 0, cost_month);
  }
  
  res.writeHead(200);
  res.end('OK');
}

function handlePrintifyWebhook(data, res) {
  const { cost_today, cost_month } = data;
  logEvent('printify', 'usage_update', data);
  checkThreshold('printify', cost_today || 0, cost_month || 0);
  
  res.writeHead(200);
  res.end('OK');
}

function handleEtsyWebhook(data, res) {
  const { cost_today, cost_month } = data;
  logEvent('etsy', 'usage_update', data);
  checkThreshold('etsy', cost_today || 0, cost_month || 0);
  
  res.writeHead(200);
  res.end('OK');
}

function handleGumroadWebhook(data, res) {
  const { event_type, product_id, customer_email, amount } = data;
  logEvent('gumroad', event_type, data);
  
  res.writeHead(200);
  res.end('OK');
}

function handleStripeWebhook(data, res) {
  const { event_type, amount, fee } = data;
  logEvent('stripe', event_type, data);
  
  res.writeHead(200);
  res.end('OK');
}

function handleYouTubeWebhook(data, res) {
  const { quota_used, quota_limit } = data;
  logEvent('youtube', 'quota_update', data);
  
  res.writeHead(200);
  res.end('OK');
}

/**
 * Main
 */
const port = process.argv[2] ? parseInt(process.argv[2]) : 3000;
startServer(port);
