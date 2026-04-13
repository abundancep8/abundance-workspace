# Claude API Usage Monitor Setup

## Overview
This cron task tracks Claude API usage and costs, logging to `.cache/claude-usage.json` and alerting when budget thresholds are exceeded.

**Current Time:** Sunday, April 12th, 2026 — 8:04 PM (America/Los_Angeles)

## Configuration

### Pricing Rates
- **Input:** $0.4 per 1M tokens
- **Output:** $1.2 per 1M tokens

### Budget Thresholds
- **Daily Budget:** $5.00
  - Alert at: $3.75 (75%)
- **Monthly Budget:** $155.00
  - Alert at: $116.25 (75%)

## Implementation Status

### ✅ What's Ready
- Logging infrastructure in place
- Cost calculation formulas
- JSON output format
- Webhook alert system (configured)
- Python & Bash scripts ready

### ❌ What Needs Setup

#### Option 1: Environment Variables (Manual)
Set usage data via environment variables:
```bash
export USAGE_DATA_DAILY='input=123456 output=789012'
export USAGE_DATA_MONTH='input=1234567 output=7890123'
python3 ~/.openclaw/workspace/.cache/claude-usage-monitor.py
```

#### Option 2: Anthropic API (Awaiting Release)
Anthropic does not currently expose a public API endpoint for usage data. This will be available when/if they release it. Code is ready to integrate it.

#### Option 3: Browser Automation (Manual Login)
The Chrome browser can fetch from `https://console.anthropic.com/account/usage` but requires:
- Active Anthropic Console login session
- UI elements to remain stable (not guaranteed between Anthropic updates)

#### Option 4: Webhook from Anthropic (Ideal)
If Anthropic supports webhook notifications for usage, configure:
```bash
export WEBHOOK_SOURCE_URL="<anthropic-webhook-endpoint>"
```

## Manual Usage Fetching

For now, you can manually update usage by:

1. Visit https://console.anthropic.com/account/usage
2. Check the usage stats for today and this month
3. Run the monitor with:
```bash
USAGE_DATA_DAILY='input=<tokens_in> output=<tokens_out>' \
USAGE_DATA_MONTH='input=<tokens_in> output=<tokens_out>' \
python3 ~/.openclaw/workspace/.cache/claude-usage-monitor.py
```

## Webhook Configuration

To enable alerts, set:
```bash
export WEBHOOK_URL="https://your-webhook-endpoint.com/monitor"
```

The webhook will receive:
```json
{
  "timestamp": "2026-04-13T03:04:00Z",
  "tokens_today": 123456,
  "input_tokens_today": 100000,
  "output_tokens_today": 23456,
  "cost_today": 0.0334,
  "tokens_month": 1234567,
  "input_tokens_month": 1000000,
  "output_tokens_month": 234567,
  "cost_month": 0.6814,
  "budget_daily": 5.00,
  "budget_monthly": 155.00,
  "percent_daily": 0.7,
  "percent_monthly": 0.4,
  "status": "ok"
}
```

## Log File Format

Location: `~/.openclaw/workspace/.cache/claude-usage.json`

```json
{
  "timestamp": "2026-04-13T03:04:00Z",
  "tokens_today": 123456,
  "input_tokens_today": 100000,
  "output_tokens_today": 23456,
  "cost_today": 0.0334,
  "tokens_month": 1234567,
  "input_tokens_month": 1000000,
  "output_tokens_month": 234567,
  "cost_month": 0.6814,
  "budget_daily": 5.00,
  "budget_monthly": 155.00,
  "percent_daily": 0.7,
  "percent_monthly": 0.4,
  "status": "ok"
}
```

Status values:
- `ok` - Within budget
- `warning_daily` - Daily threshold exceeded
- `warning_monthly` - Monthly threshold exceeded

## Testing

Test the logger with sample data:
```bash
USAGE_DATA_DAILY='input=4500000 output=1000000' \
USAGE_DATA_MONTH='input=100000000 output=30000000' \
python3 ~/.openclaw/workspace/.cache/claude-usage-monitor.py
```

This will trigger daily alert (cost: ~$2.80 out of $5.00 daily budget).

## Cron Integration

In `HEARTBEAT.md` or as a scheduled cron, add:
```bash
# Fetch Claude API usage (requires manual update for now)
# Set USAGE_DATA_* environment variables before running
# Once Anthropic releases usage API, this will automate
USAGE_DATA_DAILY='input=XXX output=XXX' \
USAGE_DATA_MONTH='input=XXX output=XXX' \
python3 ~/.openclaw/workspace/.cache/claude-usage-monitor.py
```

## Next Steps

1. **Immediate:** Manually check usage at https://console.anthropic.com/account/usage and run monitor with real data
2. **Short-term:** Set up webhook endpoint if alerts are needed
3. **Long-term:** Monitor Anthropic API announcements for usage endpoint release
