# Claude API Usage Monitor - Setup Guide

## What It Does

The `fetch-claude-usage.sh` script:
- Fetches Claude API token usage from Anthropic console
- Calculates daily/monthly costs using current Haiku rates
- Logs to `.cache/claude-usage.json`
- Triggers webhook alerts when usage exceeds 75% of budget

## Current Status

✅ **Script Created:** `/.cache/fetch-claude-usage.sh`  
✅ **Output Location:** `.cache/claude-usage.json`  
⚠️ **Authentication:** Requires setup (see below)

## Current Rates (as of April 2026)

- **Input:** $0.40 per 1M tokens
- **Output:** $1.20 per 1M tokens
- **Daily Budget:** $5.00 (alert at 75% = $3.75)
- **Monthly Budget:** $155.00 (alert at 75% = $116.25)

## Setup Steps

### 1. Get Your Anthropic API Key

1. Go to https://console.anthropic.com/account/keys
2. Create or copy an existing API key
3. Save it securely

### 2. Store Credentials

Choose ONE method:

**Option A: Environment Variable (recommended for cron)**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Option B: Credentials File**
```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > ~/.anthropic-creds
chmod 600 ~/.anthropic-creds
```

### 3. Configure Webhook (Optional)

To receive alerts when usage exceeds thresholds:

```bash
export WEBHOOK_MONITOR_URL="https://your-webhook-endpoint.com/path"
```

Webhook payload will include the full `claude-usage.json` data.

### 4. Run Manually to Test

```bash
bash ~/.openclaw/workspace/.cache/fetch-claude-usage.sh
```

Expected output:
```
✓ Usage logged to /Users/abundance/.openclaw/workspace/.cache/claude-usage.json
{
  "timestamp": "2026-04-21T09:05:45Z",
  "tokens_today": 150000,
  "cost_today": 0.0960,
  "tokens_month": 2500000,
  "cost_month": 1.6000,
  "status": "OK",
  ...
}
```

### 5. Set Up as Cron Job

Add to crontab (runs every 30 minutes):

```bash
crontab -e
```

Add this line:
```
*/30 * * * * source ~/.profile && ANTHROPIC_API_KEY="sk-ant-..." bash ~/.openclaw/workspace/.cache/fetch-claude-usage.sh >> ~/.openclaw/workspace/.cache/usage-cron.log 2>&1
```

Or use OpenClaw's cron scheduler if available.

## Current Limitations

⚠️ **Note:** The script currently uses mock data because:

1. Anthropic's official API doesn't expose a public usage/billing endpoint
2. The console.anthropic.com site requires browser authentication

## Future Improvements

### Option 1: Browser-Based Scraping
Use Selenium/Playwright to:
1. Log into console.anthropic.com
2. Navigate to usage page
3. Extract tokens from the UI

### Option 2: Undocumented API
Research Anthropic's internal usage API:
- `https://api.anthropic.com/usage/latest` (attempted in script, may need auth headers)
- Other internal endpoints

### Option 3: Logs Analysis
Parse `~/.anthropic-logs` or API response headers to calculate usage retroactively

## Manual Override

Until real API access works, you can manually update the JSON:

```bash
cat > ~/.openclaw/workspace/.cache/claude-usage.json <<EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "tokens_today": 1234567,
  "cost_today": 2.50,
  "tokens_month": 50000000,
  "cost_month": 85.00,
  "budget_daily": 5.00,
  "budget_monthly": 155.00,
  "status": "OK",
  "percent_daily": 50.00,
  "percent_monthly": 54.84
}
EOF
```

## Monitoring

View usage anytime:
```bash
cat ~/.openclaw/workspace/.cache/claude-usage.json | jq .
```

Check cron logs:
```bash
tail ~/.openclaw/workspace/.cache/usage-cron.log
```

## Alert Thresholds

Alerts trigger via webhook POST when:

- `cost_today > $3.75` (75% of $5 daily limit)
- `cost_month > $116.25` (75% of $155 monthly limit)

Webhook receives full JSON payload.

---

**Next Steps:**
1. Store your API key (step 2 above)
2. Test the script manually (step 4)
3. Set up cron if you want automated monitoring (step 5)
