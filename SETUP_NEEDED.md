# Claude API Usage Monitor — Setup Required

## Current Status
The cron job `fetch-claude-api-usage` is configured but **cannot run automatically** without authentication.

**Date:** 2026-04-15T05:06:00Z  
**Issue:** Anthropic Console requires interactive login; no stored credentials available.

---

## Options to Fix This

### Option 1: Browser Session (Simplest)
1. You log in to https://console.anthropic.com once in your browser
2. Keep the session alive
3. The cron job accesses the console via your authenticated browser session

**Pros:** Works immediately, requires no secret management  
**Cons:** Session can expire if browser is closed

**Steps:**
- Run: `openclaw browser status` to check your browser profile
- Visit https://console.anthropic.com/account/usage and log in
- The cron job will then be able to scrape the page

---

### Option 2: Anthropic API (Recommended for Production)
Anthropic doesn't currently expose a public API endpoint for usage data, but you can:

1. Check if Anthropic has added a usage API endpoint (they may have added one)
2. Use your API key to make authenticated requests to check billing info if available

**Setup:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."  # Your Anthropic API key
```

The cron job can then use this key to fetch usage (pending API availability).

---

### Option 3: Manual Scraping with Stored Session
If you have a way to store a session token or use browser automation:

1. Store your session cookie securely (in a keychain, not plain text)
2. Pass it to the cron job
3. Job scrapes the console with the session

**Setup:** More complex; requires secure credential storage.

---

## What You Need to Do

Choose **Option 1** (easiest now) or **Option 2** (better for automation):

### For Option 1:
- [ ] Log into https://console.anthropic.com in your browser
- [ ] Keep browser session active (or set a long timeout)
- [ ] Re-run cron job

### For Option 2:
- [ ] Verify Anthropic has a usage API (check docs: https://docs.anthropic.com/)
- [ ] Provide your `ANTHROPIC_API_KEY` via environment variable or config file
- [ ] Update the cron script to use API calls instead of scraping

---

## What the Cron Job Will Do (Once Authenticated)

Once you set up auth, the job will:

1. **Fetch usage data** from Anthropic Console (daily tokens + this month)
2. **Calculate costs** using Haiku rates:
   - Input: $0.4/1M tokens
   - Output: $1.2/1M tokens
3. **Log to** `~/.cache/claude-usage.json`:
   ```json
   {
     "timestamp": "ISO-8601",
     "tokens_today": 12345,
     "cost_today": 0.50,
     "tokens_month": 456789,
     "cost_month": 18.75,
     "budget_daily": 5.00,
     "budget_monthly": 155.00,
     "status": "ok" or "warning" or "alert"
   }
   ```
4. **Alert via webhook** if:
   - Daily cost > $3.75 (75% of $5.00 budget)
   - Monthly cost > $116.25 (75% of $155.00 budget)

---

## Next Steps

1. Pick your auth option above
2. Set it up
3. Let me know, and I'll update the cron job to use it
4. Job will then run silently, logging usage every time it runs

---

**Questions?** Ask — I can walk you through any of these options.
