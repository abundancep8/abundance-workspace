# Claude API Usage Tracker

## Setup

1. **Script location:** `.cache/fetch-claude-usage.js` (executable)
2. **Output:** `.cache/claude-usage.json`
3. **Webhook alerts:** Set `WEBHOOK_MONITOR_URL` env var

## Configuration

### Budget (edit in script)
- **Daily:** $5.00
- **Monthly:** $155.00
- **Alert threshold:** 75% ($3.75 daily, $116.25 monthly)

### Rates (current Claude Haiku)
- **Input:** $0.4 / 1M tokens
- **Output:** $1.2 / 1M tokens

## Implementing Data Fetch

The script has a `fetchUsageData()` placeholder. You need one of these:

### Option 1: Browser Automation (Recommended)

Uses Playwright to log into Anthropic console and scrape usage.

```bash
npm install playwright
```

Then replace `fetchUsageData()`:

```javascript
const { chromium } = require('playwright');

async function fetchUsageData() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // Navigate to Anthropic console
  await page.goto('https://console.anthropic.com/dashboard');
  
  // Log in (requires ANTHROPIC_USERNAME and ANTHROPIC_PASSWORD env vars)
  await page.fill('[name="email"]', process.env.ANTHROPIC_USERNAME);
  await page.fill('[name="password"]', process.env.ANTHROPIC_PASSWORD);
  await page.click('button:has-text("Sign in")');
  await page.waitForNavigation();
  
  // Extract usage data (selectors may change)
  const usage = await page.evaluate(() => {
    return {
      tokens_today: parseInt(document.querySelector('[data-test="tokens-today"]').textContent),
      tokens_month: parseInt(document.querySelector('[data-test="tokens-month"]').textContent),
      // ... extract input/output breakdown if available
    };
  });
  
  await browser.close();
  return usage;
}
```

**Pros:** Works with current console UI
**Cons:** Brittle (console changes break selectors), slow, requires credentials

### Option 2: Anthropic API (If Available)

If Anthropic offers a usage API endpoint:

```javascript
async function fetchUsageData() {
  const response = await fetch('https://api.anthropic.com/v1/usage', {
    headers: {
      'Authorization': `Bearer ${process.env.ANTHROPIC_API_KEY}`,
    },
  });
  
  const data = await response.json();
  
  return {
    tokens_today: data.usage.input_tokens + data.usage.output_tokens,
    input_tokens_today: data.usage.input_tokens,
    output_tokens_today: data.usage.output_tokens,
    tokens_month: data.usage_month.input_tokens + data.usage_month.output_tokens,
    input_tokens_month: data.usage_month.input_tokens,
    output_tokens_month: data.usage_month.output_tokens,
  };
}
```

**Check:** Does this exist? Test with curl first.

### Option 3: Manual Export + Script

Export usage from console, store locally, script reads it:

1. Go to: https://console.anthropic.com/account/usage
2. Take screenshot or download CSV/JSON
3. Parse locally in the script

```javascript
async function fetchUsageData() {
  const csv = fs.readFileSync('.cache/usage-export.csv', 'utf8');
  const lines = csv.split('\n');
  
  return {
    tokens_today: parseInt(lines[1].split(',')[1]),
    // ... parse other fields
  };
}
```

**Pros:** Simple, reliable
**Cons:** Requires manual update daily/monthly

## Running

### Manual Test
```bash
node .cache/fetch-claude-usage.js
```

### Via Cron

Add to crontab:

```bash
# Run every 4 hours
0 */4 * * * cd /Users/abundance/.openclaw/workspace && WEBHOOK_MONITOR_URL=https://your-webhook.com node .cache/fetch-claude-usage.js
```

Or via OpenClaw cron:

```bash
openclaw cron add "fetch-claude-usage" --schedule "0 */4 * * *" --command "node /Users/abundance/.openclaw/workspace/.cache/fetch-claude-usage.js"
```

## Output Format

```json
{
  "timestamp": "2026-04-18T15:04:00.000Z",
  "tokens_today": 1250000,
  "cost_today": 1.75,
  "tokens_month": 45000000,
  "cost_month": 68.00,
  "budget_daily": 5.00,
  "budget_monthly": 155.00,
  "status": "OK (Daily: 35.0% | Monthly: 43.9%)"
}
```

## Webhook Alert Format

Posted when daily cost > $3.75 OR monthly > $116.25:

```json
{
  "alert_type": "ALERT_DAILY",
  "timestamp": "2026-04-18T15:04:00.000Z",
  "cost_today": 3.80,
  "budget_daily": 5.00,
  "daily_percent": "76.0",
  "cost_month": 68.00,
  "budget_monthly": 155.00,
  "monthly_percent": "43.9"
}
```

## Next Steps

1. **Choose fetch method** (browser automation recommended)
2. **Implement `fetchUsageData()`** in the script
3. **Test manually:** `node .cache/fetch-claude-usage.js`
4. **Set webhook URL:** `export WEBHOOK_MONITOR_URL=https://...`
5. **Schedule cron job**

---

**Debug:** Run with `DEBUG=1` for verbose logging (add to script if needed)
