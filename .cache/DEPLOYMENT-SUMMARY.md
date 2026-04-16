# Claude API Usage Monitor - Deployment Summary

**Deployed:** April 16, 2026 @ 09:05 UTC
**Status:** ✓ Ready

## What Was Set Up

### 1. Core Monitoring Script
- **File:** `fetch-claude-usage-enhanced.py`
- **Purpose:** Fetches Claude API usage and logs to JSON
- **Frequency:** Hourly (configurable)
- **Output:** `.cache/claude-usage.json`

### 2. Cron Job Configuration
- **OpenClaw Config:** `.openclaw/crons/fetch-claude-api-usage.yaml`
- **Schedule:** Every hour at the top of the hour (0 * * * *)
- **Timeout:** 30 seconds
- **Logging:** `.cache/claude-usage-cron.log`

### 3. Cost Tracking
- **Input Rate:** $0.4 per 1M tokens
- **Output Rate:** $1.2 per 1M tokens
- **Daily Budget:** $5.00 (alert at $3.75)
- **Monthly Budget:** $155.00 (alert at $116.25)

### 4. Alert System
- **Status Levels:** OK, WARNING, ALERT_DAILY, ALERT_MONTHLY
- **Webhook Integration:** POST to `WEBHOOK_MONITOR_URL` on alert
- **Alert Data:** Includes costs, percentages, and timestamps

## Current Usage

```json
{
  "date": "2026-04-16",
  "cost_today": 0.0,
  "cost_month": 0.012192,
  "percent_daily": 0.0,
  "percent_monthly": 0.01,
  "status": "OK"
}
```

## Configuration Steps Remaining

### 1. Configure Webhook (Optional)

To enable alerts:

```bash
export WEBHOOK_MONITOR_URL="https://your-webhook.com/api/alerts"
```

Add to shell profile for persistence.

### 2. Test the System

Run manually:
```bash
python3 ~/.openclaw/workspace/.cache/fetch-claude-usage-enhanced.py
```

Check output:
```bash
cat ~/.openclaw/workspace/.cache/claude-usage.json | jq
```

## Files Created

| File | Purpose |
|------|---------|
| `fetch-claude-usage-cron.py` | Initial implementation |
| `fetch-claude-usage-enhanced.py` | Production script |
| `setup-claude-usage-cron.sh` | Management utilities |
| `claude-usage.json` | Current usage log |
| `.openclaw/crons/fetch-claude-api-usage.yaml` | OpenClaw cron config |
| `CLAUDE-USAGE-MONITOR-README.md` | Full documentation |

## Next Steps

1. **Webhook Setup** (if desired):
   ```bash
   export WEBHOOK_MONITOR_URL="your-url"
   ~/.openclaw/workspace/.cache/setup-claude-usage-cron.sh test-webhook
   ```

2. **Verify Cron is Running**:
   ```bash
   ~/.openclaw/workspace/.cache/setup-claude-usage-cron.sh status
   ```

3. **Monitor Logs**:
   ```bash
   tail -f ~/.openclaw/workspace/.cache/claude-usage-cron.log
   ```

## Key Features

✓ **Automatic tracking** - Runs hourly without intervention
✓ **Cost calculation** - Real-time budget tracking
✓ **Alert system** - Webhook on threshold breach
✓ **Daily/Monthly metrics** - Separate tracking per period
✓ **Easy management** - Status, logs, testing utilities
✓ **OpenClaw integration** - Native cron support

## Thresholds

| Metric | Budget | Alert Threshold | Alert Type |
|--------|--------|-----------------|------------|
| Daily | $5.00 | $3.75 (75%) | ALERT_DAILY |
| Monthly | $155.00 | $116.25 (75%) | ALERT_MONTHLY |

## Support

For issues or customization:
- Check `CLAUDE-USAGE-MONITOR-README.md`
- View logs: `tail ~/.openclaw/workspace/.cache/claude-usage-cron.log`
- Run status: `~/.openclaw/workspace/.cache/setup-claude-usage-cron.sh status`

---

System ready for production use.
