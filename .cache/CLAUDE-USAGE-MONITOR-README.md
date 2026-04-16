# Claude API Usage Monitor

Automated monitoring of Claude API usage with cost tracking and webhook alerts.

## Overview

The system tracks Claude API token usage and costs in real-time, logging data to `.cache/claude-usage.json` and triggering webhook alerts when usage exceeds configurable thresholds.

### Key Features

- **Hourly Usage Logging**: Automatic tracking every hour
- **Cost Calculation**: Real-time cost computation based on current Haiku pricing
  - Input: $0.4 per 1M tokens
  - Output: $1.2 per 1M tokens
- **Budget Alerts**: 
  - Daily budget: $5.00 (alert at 75% = $3.75)
  - Monthly budget: $155.00 (alert at 75% = $116.25)
- **Webhook Integration**: Automatic POST to webhook on threshold breach
- **Daily/Monthly Tracking**: Separate metrics for day and month usage

## Configuration

### 1. Set Webhook URL (Optional)

To enable webhook alerts:

```bash
export WEBHOOK_MONITOR_URL="https://your-webhook.com/api/usage-alerts"
```

Add to `~/.zshrc` or `~/.bash_profile` for persistence.

### 2. Install Cron Job

#### Option A: OpenClaw Native (Recommended)

OpenClaw will automatically detect the cron config at:
```
~/.openclaw/workspace/.openclaw/crons/fetch-claude-api-usage.yaml
```

#### Option B: System Crontab

```bash
~/.openclaw/workspace/.cache/setup-claude-usage-cron.sh install
```

#### Option C: Manual

Add to crontab:
```bash
0 * * * * cd $HOME/.openclaw/workspace && python3 .cache/fetch-claude-usage-enhanced.py >> .cache/claude-usage-cron.log 2>&1
```

## Usage

### Run Manually

```bash
python3 ~/.openclaw/workspace/.cache/fetch-claude-usage-enhanced.py
```

### View Current Usage

```bash
cat ~/.openclaw/workspace/.cache/claude-usage.json | jq
```

### View Logs

```bash
tail -f ~/.openclaw/workspace/.cache/claude-usage-cron.log
```

### Check Status

```bash
~/.openclaw/workspace/.cache/setup-claude-usage-cron.sh status
```

### Test Webhook

```bash
WEBHOOK_MONITOR_URL="https://your-url" \
  ~/.openclaw/workspace/.cache/setup-claude-usage-cron.sh test-webhook
```

## Output Format

The `.cache/claude-usage.json` file contains:

```json
{
  "timestamp": "2026-04-16T09:05:30.471484+00:00Z",
  "date": "2026-04-16",
  "tokens_today": 1000,
  "tokens_today_input": 600,
  "tokens_today_output": 400,
  "cost_today": 0.7,
  "tokens_month": 50000,
  "cost_month": 35.5,
  "budget_daily": 5.0,
  "budget_monthly": 155.0,
  "alert_threshold_daily": 3.75,
  "alert_threshold_monthly": 116.25,
  "percent_daily": 14.0,
  "percent_monthly": 22.9,
  "status": "OK",
  "rates": {
    "input_per_million": 0.4,
    "output_per_million": 1.2
  }
}
```

### Status Values

- **OK**: Usage below 75% of budget
- **WARNING**: Usage between 75-100% of budget
- **ALERT_DAILY**: Daily cost exceeded $3.75
- **ALERT_MONTHLY**: Monthly cost exceeded $116.25

## Webhook Alert Format

When threshold is breached, a POST is sent to the webhook URL:

```json
{
  "alert_type": "claude_usage",
  "status": "ALERT_DAILY",
  "cost_today": 4.20,
  "cost_month": 85.50,
  "percent_daily": 84.0,
  "percent_monthly": 55.2,
  "timestamp": "2026-04-16T09:05:30.471484+00:00Z"
}
```

## Data Sources

The system tracks usage from multiple sources:

1. **API Call Logs** (`api-call-log.jsonl`): Direct API usage tracking
2. **Session History**: Historical usage patterns
3. **Previous Cache**: Incremental daily/monthly accumulation

## Budget Management

### Daily Budget: $5.00
- Recommended for keeping costs predictable
- Resets at 00:00 UTC each day
- Alert triggers at $3.75 (75%)

### Monthly Budget: $155.00
- For total monthly cost control
- Running total through calendar month
- Alert triggers at $116.25 (75%)

To adjust budgets, edit the Python script:
```python
BUDGET_DAILY = 5.00
BUDGET_MONTHLY = 155.00
```

## Troubleshooting

### No Usage Data

The system accumulates very small amounts of data until significant usage occurs. Expected first meaningful readings:
- Requires multiple hourly runs
- Or manual API testing with higher token counts

### Webhook Not Firing

1. Check `WEBHOOK_MONITOR_URL` is set:
   ```bash
   echo $WEBHOOK_MONITOR_URL
   ```

2. Test webhook:
   ```bash
   ~/.openclaw/workspace/.cache/setup-claude-usage-cron.sh test-webhook
   ```

3. Check logs:
   ```bash
   tail ~/.openclaw/workspace/.cache/claude-usage-cron.log
   ```

### Cron Not Running

1. Check if installed:
   ```bash
   crontab -l | grep fetch-claude
   ```

2. Verify permissions:
   ```bash
   ls -la ~/.openclaw/workspace/.cache/fetch-claude-usage-enhanced.py
   ```

3. Check system cron logs (macOS):
   ```bash
   log show --predicate 'process == "cron"' --last 1h
   ```

## Files

| File | Purpose |
|------|---------|
| `fetch-claude-usage-enhanced.py` | Main monitoring script |
| `setup-claude-usage-cron.sh` | Cron installation/management |
| `claude-usage.json` | Current usage log |
| `claude-usage-cron.log` | Execution logs |
| `.openclaw/crons/fetch-claude-api-usage.yaml` | OpenClaw cron config |

## Integration with OpenClaw

OpenClaw can automatically detect and run the cron configuration. The system will:
- Execute on schedule
- Post alerts to webhook
- Log all activity
- Handle failures gracefully

To verify OpenClaw integration:
```bash
openclaw cron list
openclaw cron status fetch-claude-api-usage
```

## Security

- ✓ No credentials stored in files
- ✓ Uses environment variables for secrets
- ✓ Webhook URL from `WEBHOOK_MONITOR_URL` only
- ✓ No token data exported outside workspace
- ✓ Logs contain only usage metrics, not keys

## Future Enhancements

- [ ] Multi-account support
- [ ] Custom budget tiers
- [ ] Email notifications
- [ ] Historical usage charts
- [ ] Budget forecasting
- [ ] Per-model cost breakdown
