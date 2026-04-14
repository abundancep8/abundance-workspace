#!/usr/bin/env node

/**
 * Claude API Usage Fetcher
 * 
 * Since Anthropic doesn't provide a public usage API, this script uses browser automation
 * to fetch usage data from the Anthropic console.
 * 
 * Requirements:
 * - Anthropic console login credentials (set ANTHROPIC_EMAIL + ANTHROPIC_PASSWORD env vars)
 * - Playwright or Puppeteer installed
 * 
 * Usage:
 *   node claude-usage-fetch.js
 * 
 * This updates .cache/claude-usage-config.json with the latest token counts,
 * which the shell script then uses for cost calculations and alerts.
 */

const fs = require('fs');
const path = require('path');

// Try to use Puppeteer (browser automation)
let puppeteer;
try {
  puppeteer = require('puppeteer');
} catch {
  console.error('Puppeteer not installed. Run: npm install puppeteer');
  process.exit(1);
}

const CACHE_DIR = path.join(__dirname, '.cache');
const CONFIG_FILE = path.join(CACHE_DIR, 'claude-usage-config.json');

async function fetchUsageData() {
  const email = process.env.ANTHROPIC_EMAIL;
  const password = process.env.ANTHROPIC_PASSWORD;

  if (!email || !password) {
    console.error('Error: ANTHROPIC_EMAIL and ANTHROPIC_PASSWORD env vars required');
    console.error('Set these in your shell profile or pass them explicitly');
    process.exit(1);
  }

  let browser;
  try {
    browser = await puppeteer.launch({ headless: true });
    const page = await browser.newPage();

    // Navigate to console
    console.log('Fetching Anthropic usage data...');
    await page.goto('https://console.anthropic.com', { waitUntil: 'networkidle2' });

    // Check if login is needed
    const loginButton = await page.$('[data-testid="login-button"]');
    if (loginButton) {
      await loginButton.click();
      await page.waitForNavigation({ waitUntil: 'networkidle2' });
    }

    // Fill login form (adjust selectors as needed)
    await page.type('[type="email"]', email, { delay: 50 });
    await page.type('[type="password"]', password, { delay: 50 });
    await page.click('button[type="submit"]');

    // Wait for redirect to dashboard
    await page.waitForNavigation({ waitUntil: 'networkidle2' });

    // Navigate to billing/usage page
    await page.goto('https://console.anthropic.com/account/billing/overview', {
      waitUntil: 'networkidle2',
    });

    // Extract usage data (selectors may vary — adjust if page layout changes)
    const usageData = await page.evaluate(() => {
      // This is a placeholder; actual selectors depend on Anthropic's UI
      const todayEl = document.querySelector('[data-metric="tokens-today"]');
      const monthEl = document.querySelector('[data-metric="tokens-month"]');
      const inputEl = document.querySelector('[data-metric="tokens-input"]');
      const outputEl = document.querySelector('[data-metric="tokens-output"]');

      return {
        tokens_today: parseInt(todayEl?.textContent?.replace(/\D/g, '') || 0),
        tokens_month: parseInt(monthEl?.textContent?.replace(/\D/g, '') || 0),
        tokens_today_input: parseInt(
          inputEl?.textContent?.match(/input:?\s*(\d+)/i)?.[1] || 0
        ),
        tokens_today_output: parseInt(
          outputEl?.textContent?.match(/output:?\s*(\d+)/i)?.[1] || 0
        ),
      };
    });

    // Save config
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(usageData, null, 2));
    console.log(`✓ Saved usage data: ${CONFIG_FILE}`);
    console.log(`  Today: ${usageData.tokens_today} tokens`);
    console.log(`  Month: ${usageData.tokens_month} tokens`);

  } catch (error) {
    console.error('Error fetching usage:', error.message);
    console.error(
      '\nNote: If selectors fail, check the Anthropic console HTML and update them in this script.'
    );
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
}

fetchUsageData();
