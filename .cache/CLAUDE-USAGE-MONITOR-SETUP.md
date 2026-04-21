# Claude API Usage Monitor – Complete Setup Guide

**Status:** ✅ Ready to deploy  
**Last Updated:** April 21, 2026  
**Current Date/Time:** Tuesday, April 21st, 2026 — 12:04 AM (America/Los_Angeles)

---

## Overview

This automated system monitors your Claude API usage in real-time and alerts you when you approach budget limits.

### Key Features
- ✅ **Hourly monitoring** (configurable via cron)
- ✅ **Cost calculation** using current Haiku rates ($0.4/1M input + $1.2/1M output)
- ✅ **JSON logging** to `.cache/claude-usage.json`
- ✅ **Webhook alerts** when thresholds exceeded
- ✅ **75% threshold warnings** (daily + monthly budgets)
- ✅ **No API key required** (manual data input or browser automation)

### Budget Thresholds
- **Daily Budget:** $5.00
  - **Alert Threshold:** $3.75 (75%)
- **Monthly Budget:** $155.00
  - **Alert Threshold:** $116.25 (75%)

---

## Installation

### Step 1: Files Are Ready
All scripts are already in place:
```
~/.openclaw/workspace/.cache/
├── fetch-claude-usage-complete.py      (main script)
├── claude-usage-monitor-cron.sh        (cron wrapper)
├── claude-usage.json                   (output log)
└── claude-usage-monitor.log            (execution log)
```

### Step 2: Set Up Data Sources

#### Option A: Environment Variables (Simplest)
Before running the monitor, set these environment variables:

```bash
export ANTHROPIC_USAGE_INPUT_TOKENS_TODAY=2500000
export ANTHROPIC_USAGE_OUTPUT_TOKENS_TODAY=800000
export ANTHROPIC_USAGE_INPUT_TOKENS_MONTH=45000000
export ANTHROPIC_USAGE_OUTPUT_TOKENS_MONTH=12000000
```

Then run:
```bash
python3 ~/.openclaw/workspace/.cache/fetch-claude-usage-complete.py
```

#### Option B: Manual Update Script
Create a helper to update these values daily from the Anthropic console:

```bash
#!/bin/bash
# Manual update: Copy your usage numbers from https://console.anthropic.com/dashboard
# Then run this with the numbers:

TOKENS_IN_TODAY=$1
TOKENS_OUT_TODAY=$2
TOKENS_IN_MONTH=$3
TOKENS_OUT_MONTH=$4

export ANTHROPIC_USAGE_INPUT_TOKENS_TODAY=$TOKENS_IN_TODAY
export ANTHROPIC_USAGE_OUTPUT_TOKENS_TODAY=$TOKENS_OUT_TODAY
export ANTHROPIC_USAGE_INPUT_TOKENS_MONTH=$TOKENS_IN_MONTH
export ANTHROPIC_USAGE_OUTPUT_TOKENS_MONTH=$TOKENS_OUT_MONTH

python3 ~/.openclaw/workspace/.cache/fetch-claude-usage-complete.py
```

Usage:
```bash
./update-usage.sh 2500000 800000 45000000 12000000
```

#### Option C: Webhook Configuration
To receive alerts, set the webhook URL:

```bash
export WEBHOOK_MONITOR_URL="https://your-webhook-endpoint.com/alerts"
```

---

## Cron Setup

### Hourly Monitoring (Recommended)
Add to your crontab:

```bash
crontab -e
```

Then add:
```cron
# Run every hour
0 * * * * /Users/abundance/.openclaw/workspace/.cache/claude-usage-monitor-cron.sh >> /tmp/claude-monitor.log 2>&1

# Or run twice daily (morning + evening)
0 8,20 * * * /Users/abundance/.openclaw/workspace/.cache/claude-usage-monitor-cron.sh >> /tmp/claude-monitor.log 2>&1
```

### Verify Cron Installation
```bash
crontab -l
```

---

## Output Format

### Success Response (`claude-usage.json`)
```json
{
  "timestamp": "2026-04-21T07:05:14Z",
  "status": "success",
  "budget_daily": 5.0,
  "budget_monthly": 155.0,
  "tokens_today": 3300000,
  "tokens_month": 57000000,
  "cost_today": 1.96,
  "cost_month": 32.4,
  "input_tokens_today": 2500000,
  "output_tokens_today": 800000,
  "input_tokens_month": 45000000,
  "output_tokens_month": 12000000,
  "rates": {
    "haiku_input_per_1m": 0.4,
    "haiku_output_per_1m": 1.2
  }
}
```

### Alert Response (Threshold Exceeded)
```json
{
  "timestamp": "2026-04-21T07:05:14Z",
  "status": "success",
  "alert": true,
  "alert_reasons": [
    "Daily cost $6.20 exceeds 75% threshold ($3.75)",
    "Monthly cost $140.00 exceeds 75% threshold ($116.25)"
  ],
  "cost_today": 6.2,
  "cost_month": 140.0,
  ...
}
```

### Webhook Alert Format
When alert is triggered, POST to `WEBHOOK_MONITOR_URL`:

```json
{
  "timestamp": "2026-04-21T07:05:14Z",
  "type": "claude_usage_alert",
  "severity": "warning",
  "reasons": [
    "Daily cost $6.20 exceeds 75% threshold ($3.75)"
  ],
  "usage": {
    "cost_today": 6.2,
    "cost_month": 140.0,
    "tokens_today": 10500000,
    "tokens_month": 250000000
  },
  "budgets": {
    "daily": 5.0,
    "monthly": 155.0
  }
}
```

---

## Quick Start Examples

### Example 1: Basic Test Run
```bash
cd ~/.openclaw/workspace/.cache

# Set sample data
export ANTHROPIC_USAGE_INPUT_TOKENS_TODAY=2500000
export ANTHROPIC_USAGE_OUTPUT_TOKENS_TODAY=800000
export ANTHROPIC_USAGE_INPUT_TOKENS_MONTH=45000000
export ANTHROPIC_USAGE_OUTPUT_TOKENS_MONTH=12000000

# Run
python3 fetch-claude-usage-complete.py

# Check output
cat claude-usage.json | jq .
```

### Example 2: Trigger Alert Test
```bash
# Use high token counts to trigger alert
export ANTHROPIC_USAGE_INPUT_TOKENS_TODAY=8000000
export ANTHROPIC_USAGE_OUTPUT_TOKENS_TODAY=2500000
export ANTHROPIC_USAGE_INPUT_TOKENS_MONTH=200000000
export ANTHROPIC_USAGE_OUTPUT_TOKENS_MONTH=50000000

python3 fetch-claude-usage-complete.py
```

### Example 3: Check Current Usage
```bash
# View formatted output
jq . ~/.openclaw/workspace/.cache/claude-usage.json

# Get just the costs
jq '.cost_today, .cost_month' ~/.openclaw/workspace/.cache/claude-usage.json

# Check if alert is active
jq '.alert' ~/.openclaw/workspace/.cache/claude-usage.json
```

---

## Configuration

### Edit Budget Thresholds
Edit `fetch-claude-usage-complete.py` and modify:

```python
# Budget constants (customize as needed)
DAILY_BUDGET = 5.00
MONTHLY_BUDGET = 155.00
DAILY_ALERT_THRESHOLD = DAILY_BUDGET * 0.75  # 75%
MONTHLY_ALERT_THRESHOLD = MONTHLY_BUDGET * 0.75  # 75%
```

### Change Alert Webhook
```bash
export WEBHOOK_MONITOR_URL="https://your-endpoint/api/alerts"
```

### Change Output Location
Modify `OUTPUT_FILE` in the script or use symlink:
```bash
ln -s /custom/path/usage.json ~/.openclaw/workspace/.cache/claude-usage.json
```

---

## Getting Token Counts

### Automatic (Future)
When Anthropic releases a usage API, we can switch to:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Script will automatically fetch from API
```

### Manual (Current)
1. Go to https://console.anthropic.com/dashboard
2. Look for "Usage" or "Billing" section
3. Note the token counts:
   - **Today:** Input + Output tokens
   - **This Month:** Input + Output tokens

### Via OpenClaw Browser
```bash
openclaw browser open https://console.anthropic.com/dashboard
# Then manually read and input the numbers
```

---

## Troubleshooting

### Script Not Running in Cron
Check the log file:
```bash
tail -f ~/.openclaw/workspace/.cache/claude-usage-monitor.log
```

Common issues:
- Python path incorrect → Use full path: `/usr/local/bin/python3`
- Environment variables not set → Add to crontab:
  ```cron
  0 * * * * export ANTHROPIC_USAGE_INPUT_TOKENS_TODAY=... && /path/to/script.sh
  ```
- Permissions → Make executable: `chmod +x script.sh`

### No Data in claude-usage.json
```bash
# Test if environment variables are set
echo $ANTHROPIC_USAGE_INPUT_TOKENS_TODAY

# If empty, set them:
export ANTHROPIC_USAGE_INPUT_TOKENS_TODAY=0
python3 fetch-claude-usage-complete.py
```

### Webhook Not Triggering
1. Verify URL is valid: `curl $WEBHOOK_MONITOR_URL`
2. Check status in output: `jq '.status' claude-usage.json`
3. Verify alert threshold was exceeded: `jq '.alert' claude-usage.json`

---

## Advanced: Integration with OpenClaw Cron

To run via OpenClaw's cron system:

```bash
openclaw config set claude-usage.enabled true
openclaw config set claude-usage.cron "0 * * * *"  # Every hour
```

Then use the `[cron:...]` tag in messages to trigger this fetch.

---

## Next Steps

1. **Set up data input method** (env vars or manual)
2. **Install cron job** (optional but recommended)
3. **Configure webhook** (if you want alerts)
4. **Test with sample data** (verify output format)
5. **Update daily** with real token counts from console

---

## Support

- Check logs: `tail -f ~/.openclaw/workspace/.cache/claude-usage-monitor.log`
- Test manually: `python3 fetch-claude-usage-complete.py`
- View output: `jq . ~/.openclaw/workspace/.cache/claude-usage.json`
- Verify env: `env | grep ANTHROPIC_USAGE`

---

**Questions?** See the Python script comments for detailed implementation notes.
