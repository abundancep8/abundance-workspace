# Claude API Usage Monitor - Quick Start

**Status:** ✓ Deployed and Ready
**Last Updated:** April 16, 2026 09:05 UTC

## Check Current Usage (Right Now)

```bash
cat ~/.openclaw/workspace/.cache/claude-usage.json | jq '{date, cost_today, cost_month, percent_daily, percent_monthly, status}'
```

Output:
```json
{
  "date": "2026-04-16",
  "cost_today": 0.0,
  "cost_month": 0.012192,
  "percent_daily": 0.0,
  "percent_monthly": 0.0,
  "status": "OK"
}
```

## Get Full Details

```bash
cat ~/.openclaw/workspace/.cache/claude-usage.json | jq
```

## Run Monitoring Manually

```bash
python3 ~/.openclaw/workspace/.cache/fetch-claude-usage-enhanced.py
```

## View Execution Logs

```bash
tail -f ~/.openclaw/workspace/.cache/claude-usage-cron.log
```

## System Status

```bash
~/.openclaw/workspace/.cache/setup-claude-usage-cron.sh status
```

## Enable Webhook Alerts (Optional)

```bash
# Set webhook URL
export WEBHOOK_MONITOR_URL="https://your-webhook.com/alerts"

# Test it
~/.openclaw/workspace/.cache/setup-claude-usage-cron.sh test-webhook

# Make persistent (add to ~/.zshrc)
echo 'export WEBHOOK_MONITOR_URL="https://your-webhook.com/alerts"' >> ~/.zshrc
```

## Key Numbers

| Metric | Budget | Alert Threshold |
|--------|--------|-----------------|
| Daily Cost | $5.00 | $3.75 (at 75%) |
| Monthly Cost | $155.00 | $116.25 (at 75%) |
| Input Price | - | $0.4 per 1M |
| Output Price | - | $1.2 per 1M |

## Status Values

- **OK**: All costs below 75% of budget ✓
- **WARNING**: Cost between 75-100% of budget ⚠️
- **ALERT_DAILY**: Daily cost exceeded threshold 🚨
- **ALERT_MONTHLY**: Monthly cost exceeded threshold 🚨

## Automatic Operation

The system runs **every hour automatically** via OpenClaw's cron system:
- Fetches current usage
- Calculates costs
- Logs to `claude-usage.json`
- Sends webhook alert if threshold exceeded
- No manual intervention needed

## Full Documentation

For detailed setup, troubleshooting, and customization:

```bash
cat ~/.openclaw/workspace/.cache/CLAUDE-USAGE-MONITOR-README.md
```

## Files

```
~/.openclaw/workspace/.cache/
├── fetch-claude-usage-enhanced.py          (Main script)
├── setup-claude-usage-cron.sh             (Management)
├── claude-usage.json                       (Current usage log)
├── claude-usage-cron.log                   (Execution history)
└── .openclaw/crons/
    └── fetch-claude-api-usage.yaml         (OpenClaw config)
```

---

**Need help?** Check `CLAUDE-USAGE-MONITOR-README.md` for full documentation.
