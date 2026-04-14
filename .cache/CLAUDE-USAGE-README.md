# Claude API Usage Monitoring

This folder contains cron scripts to monitor your Claude API usage and trigger alerts when spending thresholds are exceeded.

## Setup

### 1. Choose Your Data Source

Since Anthropic doesn't provide a public usage API, you have two options:

#### Option A: Browser Automation (Recommended for Automation)
```bash
# Install dependencies
npm install puppeteer

# Set your Anthropic credentials
export ANTHROPIC_EMAIL="your-email@example.com"
export ANTHROPIC_PASSWORD="your-password"

# Fetch usage data
node .cache/claude-usage-fetch.js
```

This updates `.cache/claude-usage-config.json` with the latest token counts from your console.

#### Option B: Manual Entry
Edit `.cache/claude-usage-config.json` directly with your latest token counts from the Anthropic console:

```json
{
  "tokens_today_input": 125000,
  "tokens_today_output": 45000,
  "tokens_month_input": 3500000,
  "tokens_month_output": 1200000
}
```

### 2. Set Webhook URL (Optional)

If you want alerts sent to a webhook when thresholds are exceeded:

```bash
export WEBHOOK_MONITOR_URL="https://your-webhook-endpoint.com/claude-usage"
```

### 3. Run the Monitor

**One-time check:**
```bash
./.cache/claude-usage-cron.sh
```

**View results:**
```bash
cat .cache/claude-usage.json | jq .
```

**Set up as cron job:**

Add to your crontab (`crontab -e`):

```bash
# Run every hour
0 * * * * cd /Users/abundance/.openclaw/workspace && .cache/claude-usage-cron.sh >> .cache/claude-usage.log 2>&1

# Or every 30 minutes
*/30 * * * * cd /Users/abundance/.openclaw/workspace && .cache/claude-usage-cron.sh >> .cache/claude-usage.log 2>&1
```

## Thresholds

- **Daily Alert:** $3.75 (75% of $5.00 daily budget)
- **Monthly Alert:** $116.25 (75% of $155.00 monthly budget)

Edit `claude-usage-cron.sh` to adjust these values.

## Pricing Rates

Current Haiku rates (update if prices change):
- Input: $0.4 per 1M tokens
- Output: $1.2 per 1M tokens

## Output Format

`claude-usage.json`:
```json
{
  "timestamp": "2026-04-13T19:04:00Z",
  "tokens_today": 170000,
  "tokens_today_breakdown": {
    "input": 125000,
    "output": 45000
  },
  "cost_today": 1.29,
  "tokens_month": 4700000,
  "tokens_month_breakdown": {
    "input": 3500000,
    "output": 1200000
  },
  "cost_month": 2.05,
  "budget_daily": 5.00,
  "budget_monthly": 155.00,
  "status": "normal",
  "alert_reason": ""
}
```

## Webhook Alert Payload

When thresholds are exceeded, POST to your webhook:

```json
{
  "event": "claude_usage_alert",
  "timestamp": "2026-04-13T19:04:00Z",
  "status": "warning",
  "alert_reason": "Monthly spend at $116.25 of $155.00 budget",
  "cost_today": 3.99,
  "cost_month": 116.50,
  "budget_daily": 5.00,
  "budget_monthly": 155.00
}
```

## Troubleshooting

### `Anthropic doesn't have a public API`

True. The browser automation approach is the most reliable for automated monitoring. If you prefer, you can:
- Manually update `claude-usage-config.json` with data from the console
- Check the Anthropic console UI manually and edit the file

### Browser automation fails

- Verify credentials (ANTHROPIC_EMAIL, ANTHROPIC_PASSWORD)
- Check that the Anthropic console HTML structure hasn't changed
- Update CSS selectors in `claude-usage-fetch.js` if needed
- Check the console for detailed error messages

### Webhook not firing

- Verify `WEBHOOK_MONITOR_URL` is set and correct
- Check that your webhook endpoint is accessible
- Look for curl errors in the cron log

## Integration with OpenClaw

This cron job is registered with OpenClaw's cron scheduler. To disable or modify:
- Update the cron expression in your OpenClaw config
- Or manually remove it from crontab if using system cron

---

**Last Updated:** April 13, 2026
**Status:** Ready for deployment
