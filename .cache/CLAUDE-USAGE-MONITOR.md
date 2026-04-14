# Claude API Usage Monitor

Automated cron job that tracks Claude API spending against daily ($5.00) and monthly ($155.00) budgets.

## Status

✅ **Running** — Cron job `d6012c39-c139-42c0-b31b-90fe88869b67` is configured and executes `claude-usage-monitor.sh`

## Files

- `claude-usage-monitor.sh` — Main monitoring script
- `claude-usage.json` — Current usage log (updated by cron job)
- `CLAUDE-USAGE-MONITOR.md` — This file

## How It Works

1. **Fetches usage data** from environment variables (Anthropic doesn't expose a public API)
2. **Calculates costs** using official rates:
   - Input: $0.40 per 1M tokens (Haiku)
   - Output: $1.20 per 1M tokens (Haiku)
3. **Logs to JSON** with timestamp, tokens, costs, budget status
4. **Triggers webhook** if usage exceeds 75% of daily or monthly budget
5. **Runs silently** when within budget

## Thresholds

| Budget | 75% Threshold |
|--------|--------------|
| Daily: $5.00 | $3.75 |
| Monthly: $155.00 | $116.25 |

## Logging Usage Data

Since Anthropic doesn't expose a public usage API, you need to provide token counts via environment variables:

```bash
export ANTHROPIC_INPUT_TOKENS_TODAY=50000
export ANTHROPIC_OUTPUT_TOKENS_TODAY=20000
export ANTHROPIC_INPUT_TOKENS_MONTH=1500000
export ANTHROPIC_OUTPUT_TOKENS_MONTH=600000

/Users/abundance/.openclaw/workspace/.cache/claude-usage-monitor.sh
```

### Data Sources

Possible ways to feed token counts:

1. **Manual tracking** — Manually set env vars before running cron
2. **OpenClaw session logs** — Parse `session_status` output to extract token usage
3. **Anthropic console scraping** — Use browser automation to extract usage from console.anthropic.com
4. **Billing API integration** — When Anthropic releases a public usage API, update the script

## Webhook Alert

If usage exceeds thresholds, the script triggers a webhook POST:

```json
{
  "timestamp": "2026-04-14T01:05:04Z",
  "alert_type": "warning_daily",
  "cost_today": 3.85,
  "cost_month": 120.50,
  "daily_budget": 5.00,
  "monthly_budget": 155.00,
  "message": "Claude API usage alert triggered"
}
```

**To enable webhooks**, set the environment variable:

```bash
export WEBHOOK_MONITOR_URL="https://your-webhook-endpoint.com/alert"
```

## Manual Test

```bash
# Test alert threshold (creates sample data exceeding daily budget)
ANTHROPIC_INPUT_TOKENS_TODAY=15000000 \
ANTHROPIC_OUTPUT_TOKENS_TODAY=5000000 \
WEBHOOK_MONITOR_URL="https://your-endpoint.com" \
/Users/abundance/.openclaw/workspace/.cache/claude-usage-monitor.sh
```

## Integration with OpenClaw

To automatically feed real usage data, integrate with `session_status` calls:

```bash
# Pseudocode: Extract tokens from session_status JSON
tokens=$(openclaw session_status --json | jq '.total_tokens')
```

## Known Limitations

- ⚠️ Anthropic doesn't expose a public usage API (as of April 2026)
- Current implementation uses environment variables for demo/manual operation
- For production, you'll need to either:
  - Implement Anthropic console scraping with Playwright/browser automation
  - Wait for Anthropic's usage API to become available
  - Use a third-party billing aggregator with Anthropic integration

## Next Steps

1. Set up environment variables with actual token counts
2. Configure webhook URL if you want threshold alerts
3. Verify the cron job is running via OpenClaw's scheduler
4. Monitor `.cache/claude-usage.json` for spending trends
