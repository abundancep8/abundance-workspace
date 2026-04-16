# Supabase + Mailgun Integration Guide

## Overview

This guide walks you through setting up Supabase (database) + Mailgun (email) for your OpenClaw agent. Once complete, your agent will:

- ✅ Log every task execution (model, tokens, cost, duration)
- ✅ Store memories (decisions, patterns, insights) automatically
- ✅ Calculate performance metrics in real-time
- ✅ Send cost alerts if thresholds are exceeded
- ✅ Display live dashboard showing all metrics
- ✅ Send weekly/daily summary emails

**Total setup time: ~10 minutes**

---

## Part 1: Supabase Setup (2 minutes)

### Step 1: Sign Up at Supabase.com

1. Go to: **https://supabase.com**
2. Click **"Sign Up"**
3. Use email: **abundancep@icloud.com**
4. Verify email (check inbox, click link)

### Step 2: Create a Free Project

1. Click **"New Project"**
2. Fill in:
   - **Project Name:** `openclaw-agent`
   - **Database Password:** Save this securely (you'll need it)
   - **Region:** `us-west-1` (closest to West Coast)
3. Click **"Create"** and wait 30-60 seconds for initialization

### Step 3: Get Your Connection String

Once the project loads:

1. Go to **Settings → Database → Connection String**
2. Copy the **PostgreSQL** connection string (looks like):
   ```
   postgresql://[user]:[password]@[host]/postgres
   ```
3. **Save this securely** — you'll need it next

### Step 4: Run the Schema

1. Go to **SQL Editor** (in left sidebar)
2. Click **"New Query"**
3. Copy all text from `supabase-schema.sql` (in this workspace)
4. Paste into the query editor
5. Click **▶ Run** and wait for confirmation ✅

### Step 5: Send Your Credentials (Encrypted)

Format your connection string like this:

```
CREDENTIALS_ENCRYPTED_v1:supabase_connection_string|postgresql://user:password@db.supabase.co:5432/postgres
```

**Send this to the agent** (encrypted, never in plain text).

---

## Part 2: Mailgun Setup (2 minutes)

### Step 1: Sign Up at Mailgun.com

1. Go to: **https://www.mailgun.com**
2. Click **"Sign Up"**
3. Use email: **abundancep@icloud.com**
4. Fill in company info (any name is fine)
5. Verify email (check inbox, click link)

### Step 2: Choose Your Domain (Sandbox or Custom)

#### Option A: Sandbox (Recommended for Testing - Immediate)

1. Once logged in, go to **Dashboard → Sending**
2. You'll see a **Sandbox Domain** auto-created (e.g., `sandbox-xxxxxx.mailgun.org`)
3. Copy this domain and your API key (also on this page)

**Send to agent (encrypted):**
```
CREDENTIALS_ENCRYPTED_v1:mailgun_api_key|mg-xxxxxxxxxxxxx
CREDENTIALS_ENCRYPTED_v1:mailgun_domain|sandboxxxxxxx.mailgun.org
```

**Note:** Sandbox only emails addresses you authorize. Great for testing.

#### Option B: Custom Domain (Production-Ready)

1. Go to **Sending → Domains**
2. Click **"Add New Domain"**
3. Enter your business domain (e.g., `mail.mybusiness.com`)
4. Follow DNS verification steps (Mailgun will provide DNS records to add)
5. Once verified, use that domain

**Send to agent (encrypted):**
```
CREDENTIALS_ENCRYPTED_v1:mailgun_api_key|mg-xxxxxxxxxxxxx
CREDENTIALS_ENCRYPTED_v1:mailgun_domain|mail.mybusiness.com
```

**Timeline:** Custom domain takes 5-15 minutes to verify.

---

## Part 3: Configure Environment Variables

Once you have both credentials, create `.env.local` in your workspace:

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_KEY=your-service-role-key-here

# Mailgun
MAILGUN_API_KEY=mg-xxxxxxxxxxxxx
MAILGUN_DOMAIN=sandboxxxxxxx.mailgun.org

# Config
ALERT_EMAIL=abundancep@icloud.com
COST_THRESHOLD_DAILY=10.0
```

**Get these from:**
- Supabase: Settings → API → Keys
- Mailgun: Settings → API Keys

---

## Part 4: Test the Integration

### Run the Sync Script

```bash
cd /Users/abundance/.openclaw/workspace
node supabase-sync.js
```

You should see:
```
🔄 Starting Supabase sync...
✅ Metrics calculated:
   - Tasks: 0
   - Tokens: 0
   - Cost: $0.0000
   - Success Rate: 0.00%
   - Avg Duration: 0ms
✅ Sync completed successfully
```

### Test Email Sending

Run this in Node.js REPL:

```javascript
const { sendEmail } = require('./supabase-integration');

sendEmail({
  to: 'abundancep@icloud.com',
  subject: 'Test Email from Agent',
  html: '<h1>Hello!</h1><p>If you see this, Mailgun is working.</p>'
});
```

Check your inbox — you should receive the email in 10 seconds.

---

## Part 5: Set Up Automatic Syncing (Hourly)

### Using OpenClaw Cron

Add to `HEARTBEAT.md`:

```markdown
## Hourly Supabase Sync

Run supabase-sync.js every hour to:
- Sync daily memories from memory/ to Supabase
- Calculate and store performance metrics
- Send cost alerts if threshold exceeded

**Command:**
```bash
cd /Users/abundance/.openclaw/workspace && node supabase-sync.js
```

**Schedule:** Every hour (0 * * * *)
```

### Using System Cron (macOS/Linux)

```bash
crontab -e

# Add this line:
0 * * * * cd /Users/abundance/.openclaw/workspace && node supabase-sync.js >> supabase-sync.log 2>&1
```

---

## Part 6: View the Live Dashboard

### Option A: Local File
Open `live-dashboard.html` in your browser (works offline with cached data).

### Option B: Expose as Web Service

If you want the dashboard accessible online:

1. Deploy `live-dashboard.html` to:
   - Vercel: `vercel deploy live-dashboard.html`
   - Netlify: Drag & drop the file
   - GitHub Pages: Push to `docs/` folder

2. Update credentials in dashboard (lines 211-212):
   ```javascript
   const SUPABASE_URL = 'YOUR_SUPABASE_URL';
   const SUPABASE_KEY = 'YOUR_SUPABASE_ANON_KEY';
   ```

3. Enable CORS in Supabase: Settings → API → CORS Allowed Origins → Add your domain

---

## Part 7: Integration with Agent

Once everything is set up, the agent will automatically:

### On Every Task Completion
```javascript
const { logTask } = require('./supabase-integration');

await logTask({
  task_name: 'send-email',
  model_used: 'claude-haiku',
  tokens_used: 2500,
  cost: 0.05,
  duration_ms: 3500,
  status: 'success'
});
```

### On Important Decisions
```javascript
const { saveMemory } = require('./supabase-integration');

await saveMemory('session-123', 'decision', 
  'Chose Kimi for batch jobs due to 40% cost savings'
);
```

### Every Hour (via cron)
```bash
node supabase-sync.js
```

This:
- Syncs memories from `memory/` to Supabase
- Calculates 24h metrics
- Updates dashboard
- Sends cost alerts if needed

---

## Part 8: Monitor & Optimize

### View Metrics

**Dashboard:**
- Open `live-dashboard.html`
- See tasks, tokens, costs, success rate, duration

**Database:**
- Supabase → Table Editor → `task_log`
- Filter by model, status, cost, date range

**Export Data:**
```javascript
const { exportDashboardData } = require('./supabase-integration');
const data = await exportDashboardData();
console.log(JSON.stringify(data, null, 2));
```

### Optimization Checklist

- [ ] Track which model is cheapest (usually Kimi for batch work)
- [ ] Identify slow tasks (look at `duration_ms`)
- [ ] Set cost alerts that make sense for your budget
- [ ] Review weekly summaries to find patterns
- [ ] Cache frequent operations to reduce tokens

---

## Troubleshooting

### "Cannot connect to Supabase"

1. Check `.env.local` has correct URL and keys
2. Verify Supabase project is active (not paused)
3. Check network connectivity
4. Try: `curl https://your-project.supabase.co/rest/v1/`

### "Mailgun email not sending"

1. Verify API key is correct
2. If using sandbox, add recipient to authorized list (Settings → Sandbox Domain)
3. Check email format (must be valid email)
4. Check spam folder
5. View Mailgun logs: Dashboard → Logs

### "Dashboard shows no data"

1. Run `node supabase-sync.js` manually to trigger sync
2. Check `task_log` table is not empty (Supabase → Table Editor)
3. Verify CORS is enabled if using web-deployed dashboard
4. Check browser console for JS errors

### "Sync script fails"

1. Check Node.js is installed: `node --version`
2. Install dependencies: `npm install @supabase/supabase-js form-data`
3. Verify `.env.local` exists and has all required variables
4. Check file permissions: `chmod +x supabase-sync.js`

---

## Pricing & Costs

### Supabase
- **Free Tier:** 500MB storage, 2GB bandwidth/month
- **Cost:** $0 (generous free tier)
- **Upgrade:** $25/month for 8GB storage

### Mailgun
- **Free Tier:** 5,000 emails/month
- **Cost:** $0.50 per 1,000 emails after free tier
- **Example:** 100k emails/month = ~$50/month

### Total Monthly Cost
- **Minimal use:** $0-5/month
- **Heavy use (1M emails):** ~$500/month

---

## What Gets Stored

### In Supabase
- `task_log`: Every task execution (model, tokens, cost, duration, status)
- `agent_memory`: Important decisions, patterns, insights
- `learning_cycles`: Daily synthesis of improvements
- `performance_metrics`: Aggregated metrics for dashboard
- `dashboard_config`: Configuration settings

### In Mailgun
- Sent emails (logs only, no content stored long-term)
- Bounces & unsubscribes
- Delivery reports

---

## Next Steps

1. ✅ Sign up Supabase + Mailgun
2. ✅ Run schema SQL in Supabase
3. ✅ Create `.env.local` with credentials
4. ✅ Test sync script: `node supabase-sync.js`
5. ✅ Test email: `sendEmail({...})`
6. ✅ Set up hourly cron: `0 * * * *`
7. ✅ Open `live-dashboard.html` and bookmark
8. ✅ Start using agent — everything logs automatically

---

## Questions?

Refer to official docs:
- **Supabase:** https://supabase.com/docs
- **Mailgun:** https://documentation.mailgun.com
- **Node.js:** https://nodejs.org/docs

Or check the code comments in:
- `supabase-integration.js` — Client library
- `supabase-sync.js` — Sync script
- `live-dashboard.html` — Dashboard code
