# Claude API Usage Monitor

Cron task: `d6012c39-c139-42c0-b31b-90fe88869b67`

Monitors Claude API usage against daily ($5.00) and monthly ($155.00) budgets. Alerts when usage exceeds 75% of budget.

## Files

- **claude-usage-monitor.sh** - Main monitoring script (cron target)
- **update-usage-manual.sh** - Helper to manually log token usage
- **claude-usage.json** - Current usage log (JSON)
- **usage-manual.json** - Manual override data

## Configuration

### Option 1: Manual Updates (Easiest)

Since Anthropic doesn't yet expose a public usage API, you can manually log usage from the console:

1. Go to https://console.anthropic.com/account/usage
2. Read **Input Tokens Today** and **Output Tokens Today** (or this month)
3. Run the update script:

```bash
./.cache/update-usage-manual.sh \
  --today-input 45000 \
  --today-output 23000 \
  --month-input 750000 \
  --month-output 380000
```

Then the monitor script will use that data.

### Option 2: Environment Variable Setup

If Anthropic adds a usage API in the future, set:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

The monitor will attempt to fetch usage from the API.

### Option 3: Browser Automation (Future)

For fully automated fetching without manual updates, you can integrate browser automation:
- Use `openclaw browser` to navigate to console.anthropic.com
- Scrape usage numbers
- Pass to update script

## Webhook Alerts

To receive alerts when budget thresholds are exceeded:

```bash
export WEBHOOK_URL="https://webhook-monitor/api/alerts"
```

Alerts trigger when:
- **Daily cost > $3.75** (75% of $5.00)
- **Monthly cost > $116.25** (75% of $155.00)

Alert payload includes:
```json
{
  "timestamp": "2026-04-13T11:05:00Z",
  "alert_type": "claude_budget_threshold",
  "status": "warning",
  "daily": {
    "cost": 3.80,
    "limit": 3.75,
    "budget": 5.00,
    "exceeded": 1,
    "percent": "76.0"
  },
  "monthly": { ... },
  "tokens": { ... }
}
```

## Usage Log Format

**claude-usage.json** contains:

```json
{
  "timestamp": "2026-04-13T11:05:00Z",
  "tokens_today": 68000,
  "cost_today": "0.38",
  "cost_today_usd": 0.38,
  "tokens_month": 1130000,
  "cost_month": "1.13",
  "cost_month_usd": 1.13,
  "budget_daily": "5.00",
  "budget_monthly": "155.00",
  "status": "ok"
}
```

## Pricing

Current Anthropic Haiku rates:
- **Input:** $0.4 per 1M tokens
- **Output:** $1.2 per 1M tokens

(Update the script if rates change)

## How It Works

1. **Read source:** Checks API (if key set) or manual override
2. **Calculate:** Multiplies tokens × rates
3. **Log:** Saves to `claude-usage.json`
4. **Alert:** POSTs to webhook if thresholds exceeded

## Cron Schedule

The monitor runs on a recurring schedule (configured in OpenClaw):

```
Cron ID: d6012c39-c139-42c0-b31b-90fe88869b67
Script: /Users/abundance/.openclaw/workspace/.cache/claude-usage-monitor.sh
Workspace: /Users/abundance/.openclaw/workspace
```

To check status:
```bash
cat .cache/claude-usage.json | jq .
```

To manually run:
```bash
./.cache/claude-usage-monitor.sh /Users/abundance/.openclaw/workspace
```

## Troubleshooting

**No data in claude-usage.json?**
- Check that manual data was updated with `update-usage-manual.sh`
- Verify `usage-manual.json` exists and has correct values
- Run: `cat .cache/usage-manual.json | jq .`

**Webhook alerts not sending?**
- Set `WEBHOOK_URL` environment variable
- Check webhook endpoint is accessible: `curl -X POST $WEBHOOK_URL -d "{}"`

**Costs seem wrong?**
- Verify Haiku rates are correct ($0.4/$1.2)
- Check that input/output tokens are accurate from console
- Manual updates use: 1M = 1,000,000 tokens
