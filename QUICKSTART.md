# Supabase + Mailgun Quick Start (10 Minutes)

## Checklist

### 1. Supabase Setup (2 min)
- [ ] Go to https://supabase.com → Sign Up
- [ ] Email: `abundancep@icloud.com`
- [ ] Create project `openclaw-agent` in region `us-west-1`
- [ ] Wait for database to initialize (30-60 seconds)
- [ ] Copy **PostgreSQL connection string** from Settings → Database → Connection String
- [ ] Go to **SQL Editor** → Run `supabase-schema.sql` (copy entire file)
- [ ] Get **Anon Key** from Settings → API → Copy anon public key
- [ ] Get **Service Role Key** from Settings → API → Copy service role key

**Save these credentials securely (not in git):**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_KEY=eyJ...
```

---

### 2. Mailgun Setup (2 min)
- [ ] Go to https://mailgun.com → Sign Up
- [ ] Email: `abundancep@icloud.com`
- [ ] Create account
- [ ] Go to Dashboard → Sending
- [ ] Copy **Sandbox Domain** (e.g., `sandboxXXXXXX.mailgun.org`)
- [ ] Go to Settings → API Keys
- [ ] Copy **API Key** (starts with `mg-`)

**Save these:**
```
MAILGUN_API_KEY=mg-xxxxx
MAILGUN_DOMAIN=sandboxXXXXXX.mailgun.org
```

---

### 3. Configure Environment (1 min)
- [ ] Copy `.env.local.example` to `.env.local`
- [ ] Fill in all 4 Supabase values (URL + 2 Keys)
- [ ] Fill in 2 Mailgun values (API Key + Domain)
- [ ] Set `ALERT_EMAIL=abundancep@icloud.com`
- [ ] Set `COST_THRESHOLD_DAILY=10.0`

**Your `.env.local` should look like:**
```
SUPABASE_URL=https://xyzabc.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
MAILGUN_API_KEY=mg-d1234567890abcdefghij
MAILGUN_DOMAIN=sandboxabc12345xyz.mailgun.org
ALERT_EMAIL=abundancep@icloud.com
COST_THRESHOLD_DAILY=10.0
```

---

### 4. Install Dependencies (1 min)
```bash
cd /Users/abundance/.openclaw/workspace
npm install @supabase/supabase-js form-data
```

---

### 5. Test Integration (2 min)
```bash
# Test Supabase sync
node supabase-sync.js

# Should output:
# 🔄 Starting Supabase sync...
# ✅ Sync completed successfully
```

---

### 6. Test Email (1 min)
```bash
node -e "
const { sendEmail } = require('./supabase-integration');
sendEmail({
  to: 'abundancep@icloud.com',
  subject: 'Test from Agent',
  html: '<h1>It works!</h1>'
}).then(() => console.log('Email sent!'));
"
```

Check inbox — email should arrive in 10 seconds.

---

### 7. Set Up Hourly Sync (1 min)

Add this line to your system cron:
```bash
crontab -e

# Add:
0 * * * * cd /Users/abundance/.openclaw/workspace && node supabase-sync.js >> /tmp/supabase-sync.log 2>&1
```

Or add to OpenClaw `HEARTBEAT.md`:
```markdown
## Supabase Sync (Hourly)
Run `/Users/abundance/.openclaw/workspace/supabase-sync.js` every hour.
```

---

### 8. View Dashboard (1 min)

Option A: **Local File**
- Open `live-dashboard.html` in your browser
- Bookmark it

Option B: **Web-Deployed**
- Deploy `live-dashboard.html` to Vercel/Netlify
- Update Supabase URL in dashboard code (line 211)
- Enable CORS in Supabase Settings

---

## Done! ✅

Your agent is now ready to:
- Log every task (model, tokens, cost, duration)
- Store memories (decisions, patterns, insights)
- Calculate metrics in real-time
- Send cost alerts
- Display live dashboard

---

## Files Created

| File | Purpose |
|------|---------|
| `supabase-setup-guide.md` | Step-by-step Supabase signup |
| `mailgun-setup-guide.md` | Step-by-step Mailgun signup |
| `SUPABASE_MAILGUN_INTEGRATION.md` | Complete integration guide |
| `supabase-schema.sql` | Database tables & indexes |
| `supabase-integration.js` | Node.js client library |
| `supabase-sync.js` | Hourly sync script |
| `live-dashboard.html` | Real-time metrics dashboard |
| `.env.local.example` | Environment variable template |
| `QUICKSTART.md` | This file |

---

## What's Next?

1. **Agent Integration:** Update main agent to call:
   ```javascript
   const { logTask, sendEmail } = require('./supabase-integration');
   ```

2. **Memory Sync:** Automatically sync `memory/` to Supabase hourly

3. **Weekly Reports:** Send performance summaries via Mailgun

4. **Cost Optimization:** Use dashboard to find cheapest models

5. **Automation:** Set up alerts for budget, error rate, slowdowns

---

## Troubleshooting

**Can't connect to Supabase?**
```bash
# Verify URL is correct
curl https://your-project.supabase.co/rest/v1/

# Should return empty JSON array
```

**Mailgun email not sending?**
- Check API key is correct
- Check email format (must be valid)
- If sandbox: add recipient to authorized list
- Check spam folder

**Sync script fails?**
```bash
# Check Node.js
node --version  # Should be 14+

# Check dependencies
npm list @supabase/supabase-js

# Check .env.local has all values
grep -v '^#' .env.local | grep -v '^$'
```

---

## Pricing

| Service | Free Tier | Cost |
|---------|-----------|------|
| Supabase | 500MB storage, 2GB bandwidth/mo | $0-25/mo |
| Mailgun | 5,000 emails/mo | $0.50 per 1K emails after |
| **Total** | Up to 5K emails/mo | **$0-50/mo** |

---

## Questions?

See full documentation in:
- `SUPABASE_MAILGUN_INTEGRATION.md` (comprehensive guide)
- Code comments in `supabase-integration.js`
- Supabase docs: https://supabase.com/docs
- Mailgun docs: https://documentation.mailgun.com
