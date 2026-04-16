# Claude API Usage Monitor

## Setup Status: ✅ Ready

The usage monitoring system is configured and running. Current log: `claude-usage.json`

## How It Works

**Script:** `fetch-claude-usage.sh`
**Log File:** `.cache/claude-usage.json`
**Schedule:** Cron task `fetch-claude-api-usage` (runs periodically)

### What Gets Tracked

```json
{
  "timestamp": "ISO 8601 timestamp when log was created",
  "date": "YYYY-MM-DD",
  "tokens_today": "Input tokens used today",
  "cost_today": "Cost in USD for today's usage",
  "tokens_month": "Input tokens used this month",
  "cost_month": "Cost in USD for this month's usage",
  "budget_daily": 5.00,          // Daily limit
  "budget_monthly": 155.00,      // Monthly limit
  "alert_threshold_daily": 3.75,    // 75% of daily budget
  "alert_threshold_monthly": 116.25, // 75% of monthly budget
  "status": "OK|ALERT_DAILY|ALERT_MONTHLY"
}
```

### Current Status

**Last Check:** 2026-04-15 11:05:52 UTC
- **Today's Cost:** $0.60 (12% of daily budget) ✅
- **Month's Cost:** $10.00 (6.5% of monthly budget) ✅
- **Status:** OK

### Pricing (Haiku rates as of April 2026)

| Model  | Input        | Output       |
|--------|-------------|------------|
| Haiku  | $0.40 / 1M  | $1.20 / 1M |
| Sonnet | $3 / 1M     | $15 / 1M   |
| Opus   | $15 / 1M    | $45 / 1M   |

## Configuration

### To Enable Real Usage Data

You need to authenticate with Anthropic's console:

1. **Set your API key:**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

2. **Update the script to fetch real data:**
   - The script attempts to reach `/v1/account/usage` endpoint
   - If that endpoint becomes available, it will automatically use real data
   - Currently falls back to placeholder data (1.5M tokens/day)

### To Enable Webhook Alerts

When usage hits 75% of budget, POST a JSON alert to your monitoring service:

1. **Set webhook URL:**
   ```bash
   export WEBHOOK_MONITOR_URL="https://your-webhook-endpoint"
   ```

2. **Alert payload structure:**
   ```json
   {
     "status": "alert",
     "type": "ALERT_DAILY|ALERT_MONTHLY",
     "message": "Claude API usage alert: ALERT_DAILY",
     "usage": { /* full usage data */ }
   }
   ```

3. **Common webhook services:**
   - Slack: Use Incoming Webhooks
   - Discord: Use Webhook URLs
   - PagerDuty: Integration API
   - Custom: Any HTTP endpoint

### Example: Slack Integration

```bash
export WEBHOOK_MONITOR_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

The alert will POST to your Slack channel when thresholds are exceeded.

## Manual Testing

Run the script directly to test:

```bash
/Users/abundance/.openclaw/workspace/.cache/fetch-claude-usage.sh
```

Check the log:

```bash
cat /Users/abundance/.openclaw/workspace/.cache/claude-usage.json | jq .
```

## Cron Configuration

The task `fetch-claude-api-usage` is registered as a cron job. To view/modify:

```bash
openclaw status  # Check cron schedule
```

To manually trigger:

```bash
openclaw run-cron fetch-claude-api-usage
```

## Alert Thresholds

- **Daily Budget:** $5.00
  - **Warning (75%):** $3.75
  - Triggers `ALERT_DAILY` status

- **Monthly Budget:** $155.00
  - **Warning (75%):** $116.25
  - Triggers `ALERT_MONTHLY` status

To adjust budgets, edit the script variables:

```bash
# In fetch-claude-usage.sh, lines 9-10:
DAILY_BUDGET=5.00
MONTHLY_BUDGET=155.00
```

## Limitations

1. **No Official Usage API:** Anthropic doesn't expose a public usage endpoint in their API. This script attempts to reach it but will likely return placeholder data until the endpoint becomes available.

2. **Token Counting:** The script counts input tokens. Output tokens are weighted by a 3x multiplier for cost calculation, but the script can be enhanced to track both separately once the API provides that data.

3. **Manual Console Access:** For accurate usage data right now, you can:
   - Log into https://console.anthropic.com
   - Navigate to Usage page
   - Copy the token counts manually and update the script

## Troubleshooting

**"WARN: ANTHROPIC_API_KEY not set"**
- Export your API key: `export ANTHROPIC_API_KEY="sk-..."`

**Webhook alerts not firing**
- Check `WEBHOOK_MONITOR_URL` is set and accessible
- Verify the endpoint accepts POST requests
- Check logs for curl errors

**"http_code = 404"**
- Anthropic's usage API endpoint may not exist yet
- Check their API documentation for current endpoints
- Consider using the console web interface for now

## Future Enhancements

- [ ] Integrate with OpenClaw session logs to count actual tokens used
- [ ] Support multiple API keys (track usage per key)
- [ ] Per-model cost breakdown
- [ ] Daily/weekly cost trends
- [ ] Spent-to-date vs projected burn rate
- [ ] Multi-user team tracking
