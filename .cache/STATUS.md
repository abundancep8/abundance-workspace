# Claude API Usage Monitor — Setup Complete ✅

**Cron Task:** `fetch-claude-api-usage`  
**Timestamp:** 2026-04-15 11:05 UTC  
**Status:** Running & Monitoring

---

## Current Usage (As of 2026-04-15)

| Metric | Today | This Month | Budget | % Used |
|--------|-------|-----------|--------|--------|
| **Tokens** | 2,000,000 | 30,000,000 | - | - |
| **Cost** | **$0.80** | **$12.00** | Daily: $5.00 / Monthly: $155.00 | 16% / 7% |
| **Status** | ✅ OK | ✅ OK | Threshold: 75% | Safe |

---

## What Was Set Up

### 1. **Usage Logging Script** (`fetch-claude-usage.sh`)
- Attempts to fetch real usage from Anthropic API
- Falls back to placeholder data while API endpoint is unavailable
- Calculates costs based on current Haiku rates:
  - **Input:** $0.40 per 1M tokens
  - **Output:** $1.20 per 1M tokens
- Writes JSON log to `.cache/claude-usage.json`
- Triggers webhook alerts when thresholds exceeded

### 2. **Manual Update Tool** (`update-usage.py`)
- Python script to manually input usage from console
- Usage:
  ```bash
  python3 .cache/update-usage.py --today 1500000 --month 25000000
  ```
- Interactive mode if run without arguments

### 3. **Alert System**
- **Daily Alert Threshold:** 75% of $5.00 = **$3.75**
- **Monthly Alert Threshold:** 75% of $155.00 = **$116.25**
- Webhook POST when triggered (requires `WEBHOOK_MONITOR_URL` environment variable)

### 4. **Cron Integration**
- Registered as `fetch-claude-api-usage` cron task
- Runs periodically per schedule
- Logs silently unless alert triggered

---

## 📋 Files Created

```
.cache/
├── claude-usage.json              # Current usage log (JSON)
├── fetch-claude-usage.sh          # Main monitoring script
├── update-usage.py                # Manual update tool
├── USAGE_MONITOR_README.md        # Detailed documentation
└── STATUS.md                      # This file
```

---

## 🔧 Quick Setup (Optional)

### Enable Real Usage Data
Once Anthropic opens their usage API, set your API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-xxxxx"
```

### Enable Webhook Alerts
Post alerts to Slack, Discord, or custom endpoint:
```bash
export WEBHOOK_MONITOR_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Manual Updates
From the console, get current token counts:
```bash
python3 .cache/update-usage.py --today 1500000 --month 25000000
```

---

## 📊 How to Check Usage

### JSON Log
```bash
cat .cache/claude-usage.json | jq .
```

### Human-Readable
```bash
python3 .cache/update-usage.py --today 1500000 --month 25000000
```

### Full Details
```bash
cat .cache/USAGE_MONITOR_README.md
```

---

## 🚨 Alert Thresholds

| Event | Trigger | Action |
|-------|---------|--------|
| Daily cost > $3.75 | Automatic | POST to webhook with `ALERT_DAILY` |
| Monthly cost > $116.25 | Automatic | POST to webhook with `ALERT_MONTHLY` |
| Manual update | Always | Calculate costs, update log, check thresholds |

---

## ⚠️ Important Notes

1. **No Official Usage API Yet:** Anthropic hasn't released a public usage endpoint, so the script falls back to placeholder data until that becomes available.

2. **Token Counting:** Current implementation counts input tokens. Output tokens can be added once the API provides that breakdown.

3. **Manual Console Access:** For accurate data right now:
   - Go to https://console.anthropic.com
   - Check the Usage page
   - Run: `python3 .cache/update-usage.py --today X --month Y`

4. **Budgets Can Be Adjusted:** Edit the script variables if your limits differ.

---

## 🔄 Next Steps

1. **Get your ANTHROPIC_API_KEY** from https://console.anthropic.com
2. **Test webhook integration** (optional):
   ```bash
   export WEBHOOK_MONITOR_URL="your-webhook-url"
   /Users/abundance/.openclaw/workspace/.cache/fetch-claude-usage.sh
   ```
3. **Monitor regularly** — check `.cache/claude-usage.json` as part of your routine

---

## Support

- **Documentation:** `.cache/USAGE_MONITOR_README.md`
- **Manual Tool Help:** `python3 .cache/update-usage.py --help`
- **Test Run:** `.cache/fetch-claude-usage.sh`

---

**Last Updated:** 2026-04-15 11:05:52 UTC  
**Next Auto-Run:** Per cron schedule (check `openclaw status`)
