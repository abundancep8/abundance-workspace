# Claude API Usage Monitoring - Setup Guide

**Last Updated:** Monday, April 13th, 2026 — 6:05 AM (America/Los_Angeles)  
**Cron Job ID:** d6012c39-c139-42c0-b31b-90fe88869b67  
**Status:** ⚠️ Awaiting data source configuration

## Overview

This cron job monitors your Claude API usage and triggers alerts when you exceed 75% of your daily/monthly budget:

- **Daily Budget:** $5.00 (alert at $3.75)
- **Monthly Budget:** $155.00 (alert at $116.25)
- **Pricing:** $0.4/1M input tokens + $1.2/1M output tokens (Haiku rates)
- **Log Location:** `~/.openclaw/workspace/.cache/claude-usage.json`

## The Challenge

Anthropic **does not yet expose a public API** for usage data. The usage dashboard is only accessible via their web console (https://console.anthropic.com/account/usage), which requires login.

## Solutions

### ✅ SOLUTION 1: Manual Update (Easiest, Now Available)

Use the provided interactive script to manually enter usage data from the console:

```bash
# Interactive mode (you'll be prompted)
bash ~/.openclaw/workspace/.cache/update-usage-manual.sh

# Or pass values as environment variables
INPUT_TODAY=123456 OUTPUT_TODAY=789012 \
INPUT_MONTH=1234567 OUTPUT_MONTH=7890123 \
bash ~/.openclaw/workspace/.cache/update-usage-manual.sh
```

**Steps:**
1. Visit https://console.anthropic.com/account/usage
2. Note your input/output token counts
3. Run the script above
4. It will calculate costs and log to `.cache/claude-usage.json`
5. If over threshold, it will trigger webhook alerts (if configured)

### 🔮 SOLUTION 2: Wait for Anthropic API (Future)

Monitor https://docs.anthropic.com for a usage API endpoint. When available:

```bash
# This will work once Anthropic releases it
curl -s https://api.anthropic.com/v1/usage \
  -H "x-api-key: $ANTHROPIC_API_KEY"
```

The monitoring script already has hooks for this; it just needs Anthropic to expose the endpoint.

### 🌐 SOLUTION 3: Browser Automation (Advanced)

If you want to automate scraping from the console, you'd need to:

1. Store Anthropic credentials securely in `.secrets/`
2. Use browser automation to log in and scrape the dashboard
3. This is fragile (UI changes break it) and complex

**Not recommended unless absolutely necessary.**

## How to Set Up Automated Cron Updates

### Option A: Schedule Manual Updates in Your Calendar

Add a recurring reminder to check usage weekly/daily and run:
```bash
bash ~/.openclaw/workspace/.cache/update-usage-manual.sh
```

### Option B: Set Environment Variables in Cron Config

If you want cron to run automatically with pre-set values:

Edit `~/.openclaw/config/cron` (or wherever your cron config is) and add:

```bash
# Claude usage monitor (runs daily at 6:00 AM)
0 6 * * * \
  export WORKSPACE=/Users/abundance/.openclaw/workspace && \
  INPUT_TODAY=$(get_daily_tokens) OUTPUT_TODAY=$(get_daily_output) \
  INPUT_MONTH=$(get_monthly_tokens) OUTPUT_MONTH=$(get_monthly_output) \
  bash $WORKSPACE/.cache/claude-usage-monitor.sh
```

(You'd need helper functions `get_daily_tokens()` etc. to fetch from somewhere.)

## Webhook Configuration

If you want alerts when thresholds are exceeded, configure your webhook:

```bash
export WEBHOOK_URL="https://your-webhook.example.com/monitor"
bash ~/.openclaw/workspace/.cache/claude-usage-monitor.sh
```

The webhook will receive:
```json
{
  "timestamp": "2026-04-13T06:05:34Z",
  "alert_type": "claude_budget_threshold",
  "status": "warning",
  "daily": {
    "cost": 3.85,
    "limit": 3.75,
    "budget": 5.00,
    "exceeded": 1,
    "percent": 77.0
  },
  "monthly": {
    "cost": 95.50,
    "limit": 116.25,
    "budget": 155.00,
    "exceeded": 0,
    "percent": 61.6
  },
  "tokens": {
    "today": 1234567,
    "month": 45678901
  }
}
```

## Current Log Format

File: `~/.openclaw/workspace/.cache/claude-usage.json`

```json
{
  "timestamp": "2026-04-13T06:05:34Z",
  "tokens_today": 0,
  "tokens_today_breakdown": {
    "input": 0,
    "output": 0
  },
  "cost_today": "0.00",
  "cost_today_usd": 0.00,
  "tokens_month": 0,
  "tokens_month_breakdown": {
    "input": 0,
    "output": 0
  },
  "cost_month": "0.00",
  "cost_month_usd": 0.00,
  "budget_daily": "5.00",
  "budget_daily_usd": 5.00,
  "budget_monthly": "155.00",
  "budget_monthly_usd": 155.00,
  "daily_limit_75pct": "3.75",
  "monthly_limit_75pct": "116.25",
  "daily_exceeded": 0,
  "monthly_exceeded": 0,
  "status": "ok"
}
```

## Recommended Workflow

**For now (until Anthropic releases a usage API):**

1. **Weekly check:** Every Sunday, visit https://console.anthropic.com/account/usage
2. **Quick update:** Run the manual update script with your current numbers
3. **Monitoring:** Check `.cache/claude-usage.json` for cost trends
4. **Alerts:** If webhook is configured, you'll be notified when threshold is exceeded

This takes ~2 minutes per week and keeps you in control.

## Files

| File | Purpose |
|------|---------|
| `claude-usage-monitor.sh` | Main monitoring script (called by cron) |
| `update-usage-manual.sh` | Interactive script to enter usage data |
| `claude-usage.json` | Current usage log |
| `CLAUDE_USAGE_SETUP_GUIDE.md` | This file |

## Testing

Test the monitoring with sample data:

```bash
# Simulate high usage scenario
INPUT_TODAY=4500000 OUTPUT_TODAY=1000000 \
INPUT_MONTH=100000000 OUTPUT_MONTH=30000000 \
bash ~/.openclaw/workspace/.cache/update-usage-manual.sh
```

This will show warnings (cost exceeds 75% of daily budget).

## Next Steps

1. ✅ Visit https://console.anthropic.com/account/usage
2. ✅ Run: `bash ~/.openclaw/workspace/.cache/update-usage-manual.sh`
3. ✅ Enter your current usage numbers
4. ✅ Check `~/.openclaw/workspace/.cache/claude-usage.json` to verify
5. ✅ Set up a weekly reminder to repeat steps 1-3

---

**Questions?** Check the logging output or view the monitoring scripts for details.
