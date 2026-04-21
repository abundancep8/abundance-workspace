# 📊 Claude API Usage Monitor - Cron Task

**Status:** ✅ Ready to Deploy  
**Last Run:** 2026-04-20 at 11:05 UTC  
**Current Spend:** $0.01 / $5.00 daily (0.2%)

---

## What This Does

The `fetch-claude-usage` cron task automatically:

1. ✅ **Fetches token usage** from OpenClaw session logs every hour
2. ✅ **Calculates costs** using current Anthropic rates:
   - Input: $0.4 per 1M tokens
   - Output: $1.2 per 1M tokens
3. ✅ **Logs usage** to `~/.openclaw/workspace/.cache/claude-usage.json`
4. ✅ **Monitors budgets** with 75% threshold alerts:
   - Daily: $3.75 threshold (budget: $5.00)
   - Monthly: $116.25 threshold (budget: $155.00)
5. ✅ **Triggers webhook alerts** when thresholds are exceeded

---

## Quick Start

### View Current Usage
```bash
~/.openclaw/workspace/.cache/monitor-claude-usage.sh
```

Output:
```
📊 Claude API Usage Monitor
──────────────────────────────────────
📅 Date: 2026-04-20
🕒 Updated: 2026-04-20T11:05:45Z

💰 Daily Budget
   Cost: $0.01   / $5.00 ✅ (0.2%)

📈 Monthly Budget
   Cost: $0.23   / $155.00 ✅ (0.1%)

🧮 Token Usage
   Input:  14,361 tokens
   Output: 4,787 tokens
```

### Run Manually
```bash
python3 ~/.openclaw/workspace/.cache/fetch-claude-usage.py
```

### View Raw Data
```bash
cat ~/.openclaw/workspace/.cache/claude-usage.json | jq .
```

---

## Install as Cron Job

### For Hourly Monitoring (Recommended)

1. **Open your crontab:**
   ```bash
   crontab -e
   ```

2. **Add this line:**
   ```cron
   0 * * * * python3 ~/.openclaw/workspace/.cache/fetch-claude-usage.py >> ~/.openclaw/workspace/.cache/logs/claude-usage-cron.log 2>&1
   ```

3. **Optional: Set webhook URL for alerts**
   ```bash
   export WEBHOOK_MONITOR_URL="https://webhook-receiver.example.com/alerts"
   ```

### Verify Installation
```bash
crontab -l | grep fetch-claude-usage
```

You should see the cron entry listed.

---

## Budget Configuration

Edit these values in the script to customize:

```python
# Daily budget (alerts at 75% = $3.75)
BUDGET_DAILY = 5.00

# Monthly budget (alerts at 75% = $116.25)
BUDGET_MONTHLY = 155.00

# Alert threshold (when to trigger)
ALERT_THRESHOLD = 0.75  # 75%
```

---

## Webhook Alerts

When budget thresholds are exceeded, the system POSTs this payload:

```json
{
  "alert_type": "ALERT_DAILY",
  "timestamp": "2026-04-20T11:05:45Z",
  "cost_today": 3.75,
  "budget_daily": 5.00,
  "daily_percent": 75.0,
  "cost_month": 116.25,
  "budget_monthly": 155.00,
  "monthly_percent": 75.0
}
```

**Configure webhook:**
```bash
export WEBHOOK_MONITOR_URL="https://your-server.com/webhook"
```

Or add to your crontab environment:
```cron
WEBHOOK_MONITOR_URL=https://your-server.com/webhook
0 * * * * python3 ~/.openclaw/workspace/.cache/fetch-claude-usage.py
```

---

## Pricing & Rates

Current Anthropic rates (April 2026) for Claude 3 Haiku:

| Model | Input | Output |
|-------|-------|--------|
| Haiku | $0.4/1M | $1.2/1M |

*Actual rates at: https://www.anthropic.com/pricing/claude*

---

## Important Notes

### ⚠️ Estimated vs Official Usage

This monitor shows **estimated** costs based on OpenClaw's local session logs.

**For official usage**, check the Anthropic console:
→ https://console.anthropic.com/account/usage

**Why the difference?**
- Anthropic doesn't expose a public usage API
- Prompt caching can reduce actual costs (cached tokens cost less)
- OpenClaw tracks tokens locally; Anthropic tracks actual API charges
- This is an approximation for budget tracking

### How It Works

1. **Scans logs** in `~/.openclaw/workspace/.cache/logs/` from the last 24 hours
2. **Extracts token counts** using regex pattern matching:
   - Looks for: `🧮 Tokens: 99 in / 2.4k out`
3. **Calculates costs** using current Anthropic rates
4. **Estimates monthly** as 20x the daily average (business days)
5. **Triggers alerts** if thresholds are exceeded
6. **Posts webhooks** if configured

---

## Files

| File | Purpose |
|------|---------|
| `fetch-claude-usage.py` | Main script (executable) |
| `monitor-claude-usage.sh` | Quick status viewer |
| `claude-usage.json` | Usage log (updated hourly) |
| `claude-usage-cron.log` | Cron execution logs |
| `CLAUDE-USAGE-README.md` | This file |
| `CLAUDE-USAGE-CRON-SETUP.txt` | Setup instructions |

---

## Troubleshooting

### Script Not Running
```bash
# Check cron status
sudo log stream --predicate 'process == "cron"' --level debug

# Test manual run
python3 ~/.openclaw/workspace/.cache/fetch-claude-usage.py

# Check logs
tail -f ~/.openclaw/workspace/.cache/logs/claude-usage-cron.log
```

### No Token Data
- Ensure OpenClaw logs exist in `~/.openclaw/workspace/.cache/logs/`
- Run some commands to generate session logs
- Re-run the script

### Webhook Not Firing
```bash
# Check webhook URL is set
echo $WEBHOOK_MONITOR_URL

# Test webhook manually
curl -X POST "$WEBHOOK_MONITOR_URL" \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

---

## Commands Reference

```bash
# View current usage
~/.openclaw/workspace/.cache/monitor-claude-usage.sh

# Run manually
python3 ~/.openclaw/workspace/.cache/fetch-claude-usage.py

# View JSON
cat ~/.openclaw/workspace/.cache/claude-usage.json | jq .

# View just the status
cat ~/.openclaw/workspace/.cache/claude-usage.json | jq '.status'

# Watch in real-time
watch -n 60 '~/.openclaw/workspace/.cache/monitor-claude-usage.sh'

# Check cron logs
tail -f ~/.openclaw/workspace/.cache/logs/claude-usage-cron.log

# Install cron job
crontab -e
# Then add: 0 * * * * python3 ~/.openclaw/workspace/.cache/fetch-claude-usage.py >> ~/.openclaw/workspace/.cache/logs/claude-usage-cron.log 2>&1
```

---

## Next Steps

1. ✅ **Install cron job** (see Install section above)
2. ✅ **Set webhook URL** if you want alerts (optional)
3. ✅ **Monitor dashboard** using `monitor-claude-usage.sh`
4. ⚠️ **Verify official usage** at https://console.anthropic.com/account/usage

---

**Deployed:** 2026-04-20  
**Task ID:** `d6012c39-c139-42c0-b31b-90fe88869b67`
