# Claude API Usage Monitoring Setup

## Current Status
✅ **Logging structure created** at `.cache/claude-usage.json`  
✅ **Helper script created** at `.cache/fetch-claude-usage.sh`  
⏳ **Awaiting authentication** — Real usage data not yet available

---

## The Problem

Anthropic doesn't currently offer a public API endpoint for usage metrics. The only way to access usage data is through the web console at:
- https://console.anthropic.com/account/usage

This requires browser-based authentication, which creates challenges for automated cron jobs.

---

## Solutions (in order of practicality)

### 1. **Monitor for Anthropic Usage API (Recommended)**
**Status:** Future-facing  
**Effort:** None (wait for Anthropic)

Once Anthropic releases a usage API, this cron job will automatically work with an authenticated API key:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# Script will auto-detect and use the API
```

**Check for updates:**
- https://docs.anthropic.com/en/api/overview (look for Usage endpoint)
- https://github.com/anthropics/anthropic-sdk-python (releases)

---

### 2. **Browser-Based Automated Session (Current Best)**
**Status:** Implementable now  
**Effort:** Medium

Use OpenClaw's browser tool with stored session cookies:

**Setup:**
1. Manually log in to https://console.anthropic.com once
2. Extract session cookies (DevTools → Application → Cookies)
3. Store in environment or file: `~/.anthropic-session.json`
4. Update `fetch-claude-usage.sh` to use stored session

**Modified script snippet:**
```bash
if [ -f ~/.anthropic-session.json ]; then
  # Extract session data and use browser tool to fetch usage page
  # Parse the rendered HTML to extract tokens_today, tokens_month, etc.
fi
```

**Why this works:**
- OpenClaw's browser tool can handle authenticated sessions
- Can parse rendered usage dashboard
- Runs automatically on schedule

---

### 3. **Manual CSV Export (Simple, Reliable)**
**Status:** Available now  
**Effort:** Low (monthly manual step)

1. Visit https://console.anthropic.com/account/usage monthly
2. Export usage CSV
3. Parse and update `.cache/claude-usage.json`

**Script to parse CSV:**
```bash
# After downloading usage.csv from console:
python3 << 'PYTHON'
import json, csv, datetime

with open('usage.csv') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
today_rows = [r for r in rows if r['date'] == datetime.date.today().isoformat()]
month_rows = [r for r in rows if r['date'].startswith(datetime.date.today().strftime('%Y-%m'))]

tokens_today = sum(int(r.get('tokens', 0)) for r in today_rows)
cost_today = sum(float(r.get('cost_usd', 0)) for r in today_rows)

# Write to json...
PYTHON
```

---

## Configuration

### Daily Budget Threshold (Alert at 75%)
```json
{
  "budget_daily": 5.00,
  "alert_threshold_daily": 3.75
}
```

### Monthly Budget Threshold (Alert at 75%)
```json
{
  "budget_monthly": 155.00,
  "alert_threshold_monthly": 116.25
}
```

### Webhook Alert
Set environment variable for alert webhook:
```bash
export WEBHOOK_MONITOR_URL="https://your-webhook.example.com/alerts"
```

When cost exceeds threshold:
```json
POST $WEBHOOK_MONITOR_URL
{
  "event": "claude_usage_alert",
  "severity": "warning",
  "timestamp": "2026-04-13T05:04:00Z",
  "message": "Claude API usage at 76% of daily budget",
  "current_cost": 3.80,
  "daily_budget": 5.00,
  "tokens_today": 12500
}
```

---

## Next Steps

### Immediate (This Week)
- [ ] Decide which solution fits your workflow
- [ ] If CSV export: download and parse monthly usage
- [ ] If browser session: set up session cookie storage

### Medium-term (Next Month)
- [ ] Monitor Anthropic docs for usage API announcement
- [ ] Watch this repository for cron job improvements

### Long-term (2026+)
- [ ] Migrate to official Anthropic Usage API when available
- [ ] Full automation with no manual steps

---

## Files Created

| File | Purpose |
|------|---------|
| `.cache/claude-usage.json` | Usage metrics log (schema + placeholder data) |
| `.cache/fetch-claude-usage.sh` | Cron job script (extensible for 3 methods above) |
| `.cache/CLAUDE_USAGE_SETUP.md` | This document |

---

## Testing

Check current cached status:
```bash
jq . ~/.openclaw/workspace/.cache/claude-usage.json
```

Run the fetch script manually:
```bash
~/.openclaw/workspace/.cache/fetch-claude-usage.sh
```

---

## FAQ

**Q: Why not just parse the web page?**  
A: Anthropic's console is a React SPA with dynamically rendered content. Parsing requires either JavaScript execution (browser) or session-aware requests with proper auth cookies.

**Q: Can OpenClaw do this automatically?**  
A: Once you store session cookies, yes. See Solution #2 above.

**Q: What if my usage is higher than expected?**  
A: Check:
- Model used (Haiku: cheapest, Opus: expensive)
- Token counts (input/output prices differ)
- Batch jobs or long context windows
- Whether you're running tests repeatedly

**Q: How often does the cron job run?**  
A: Configure in your OpenClaw cron settings. Recommend: 2-4 times per day.

---

Last updated: 2026-04-13
