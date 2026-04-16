# 🚀 Supabase + Mailgun Integration for OpenClaw Agent

Complete end-to-end setup for logging, monitoring, and optimizing your AI agent using Supabase (database) and Mailgun (email).

## What This Does

```
Your Agent
    ↓
[Task Execution]
    ↓
LogTask() → Supabase ← SaveMemory()
    ↓                       ↓
[task_log table]      [agent_memory table]
    ↓                       ↓
    └─→ Hourly Sync ←─────┘
          (supabase-sync.js)
            ↓
    [learning_cycles table]
    [performance_metrics table]
            ↓
    [Live Dashboard] ← Email Alerts
```

### Key Features

✅ **Task Logging** - Every execution tracked (model, tokens, cost, duration, status)
✅ **Memory Storage** - Store decisions, patterns, insights, errors
✅ **Real-Time Metrics** - Dashboard updates every 5 seconds
✅ **Cost Tracking** - Know exactly what each task costs
✅ **Model Comparison** - See which models are cheapest/fastest
✅ **Automated Alerts** - Email you if costs exceed threshold
✅ **Weekly Summaries** - Learn from weekly synthesis reports
✅ **Data Export** - Pull all data as JSON for analysis

---

## File Structure

```
/Users/abundance/.openclaw/workspace/
├── QUICKSTART.md                          ← Start here! (10 min setup)
├── SUPABASE_MAILGUN_INTEGRATION.md        ← Complete guide
├── SUPABASE_SETUP_README.md               ← This file
├── supabase-setup-guide.md                ← Supabase signup instructions
├── mailgun-setup-guide.md                 ← Mailgun signup instructions
│
├── supabase-schema.sql                    ← Database schema (run once)
├── supabase-integration.js                ← Main client library
├── supabase-sync.js                       ← Hourly sync script
├── live-dashboard.html                    ← Real-time metrics UI
│
├── package.json                           ← NPM dependencies
├── .env.local.example                     ← Template for credentials
└── .env.local                             ← Your actual credentials (git-ignored)
```

---

## Quick Start (10 Minutes)

### 1️⃣ Supabase Setup (2 min)

```bash
# Go to https://supabase.com → Sign Up
# Create project "openclaw-agent" in region us-west-1
# Wait for initialization (30-60 seconds)
# Go to SQL Editor → Run supabase-schema.sql
# Get credentials from Settings → API
```

**Copy these values:**
- `SUPABASE_URL` (Settings → API → URL)
- `SUPABASE_ANON_KEY` (Settings → API → anon/public key)
- `SUPABASE_KEY` (Settings → API → service_role key)

### 2️⃣ Mailgun Setup (2 min)

```bash
# Go to https://mailgun.com → Sign Up
# Go to Dashboard → Sending → Copy Sandbox Domain
# Go to Settings → API Keys → Copy API Key
```

**Copy these values:**
- `MAILGUN_API_KEY` (starts with `mg-`)
- `MAILGUN_DOMAIN` (sandbox-xxxxx.mailgun.org)

### 3️⃣ Configure `.env.local` (1 min)

```bash
cp .env.local.example .env.local
# Edit .env.local and fill in all values
```

### 4️⃣ Install Dependencies (1 min)

```bash
npm install
```

### 5️⃣ Test Integration (2 min)

```bash
# Test Supabase
node supabase-sync.js

# Test Mailgun
node -e "const {sendEmail} = require('./supabase-integration'); sendEmail({to:'abundancep@icloud.com', subject:'Test', html:'<h1>Works!</h1>'})"
```

### 6️⃣ Set Up Hourly Sync (1 min)

Add to system cron:
```bash
crontab -e
# Add: 0 * * * * cd /Users/abundance/.openclaw/workspace && node supabase-sync.js
```

### 7️⃣ Open Dashboard (1 min)

```bash
# Open in browser
open live-dashboard.html
# Or deploy to Vercel/Netlify for web access
```

---

## How to Use

### In Your Agent Code

#### Log a Task

```javascript
const { logTask } = require('./supabase-integration');

// When a task completes:
await logTask({
  task_name: 'send-email-campaign',
  model_used: 'kimi-k2-5',
  tokens_used: 2500,
  cost: 0.015,
  duration_ms: 3500,
  status: 'success'
});
```

#### Save a Memory

```javascript
const { saveMemory } = require('./supabase-integration');

// When you make an important decision:
await saveMemory('session-123', 'decision', 
  'Switching to Kimi for batch jobs (40% cheaper than Claude)'
);

// Or store a pattern you discovered:
await saveMemory('session-123', 'pattern',
  'Tasks with >5000 tokens slow down by 2x. Consider chunking.'
);
```

#### Send an Email

```javascript
const { sendEmail } = require('./supabase-integration');

await sendEmail({
  to: 'abundancep@icloud.com',
  subject: '📊 Daily Summary',
  html: '<h1>Your agent completed 42 tasks today!</h1>'
});
```

#### Get Metrics

```javascript
const { calculateMetrics } = require('./supabase-integration');

const metrics = await calculateMetrics();
console.log(metrics);
// {
//   totalTasks: 42,
//   totalTokens: 125000,
//   totalCost: 2.50,
//   successRate: 95.24,
//   avgDuration: 3200,
//   modelBreakdown: { ... }
// }
```

---

## Database Schema

### task_log
Stores every task execution.

```sql
task_log (
  id, task_name, model_used, tokens_used, cost, 
  duration_ms, status, error_message, metadata, created_at
)
```

**Example:**
```json
{
  "id": 1,
  "task_name": "send-email",
  "model_used": "claude-haiku",
  "tokens_used": 2500,
  "cost": 0.05,
  "duration_ms": 3500,
  "status": "success",
  "metadata": { "recipients": 100 },
  "created_at": "2024-01-15T10:30:00Z"
}
```

### agent_memory
Stores important learnings.

```sql
agent_memory (
  id, session_id, memory_type, content, metadata, created_at
)
```

**memory_type:** `decision`, `pattern`, `insight`, `error`, `optimization`

### learning_cycles
Daily synthesis of improvements.

```sql
learning_cycles (
  id, cycle_date, total_tasks, total_cost, 
  improvements, token_savings, created_at
)
```

### performance_metrics
Aggregated metrics for dashboard.

```sql
performance_metrics (
  id, metric_type, metric_value, period, created_at
)
```

---

## Dashboard

### Live Metrics Shown

| Metric | Description |
|--------|-------------|
| **Tasks (24h)** | Number of tasks completed, successful tasks |
| **Tokens Used** | Total tokens, average per task |
| **Total Cost** | USD cost in last 24 hours |
| **Success Rate** | % of tasks that completed successfully |
| **Avg Duration** | Average milliseconds per task |
| **Kimi Savings** | Cost savings vs Claude baseline |

### Model Comparison

Shows side-by-side:
- Number of tasks per model
- Total tokens per model
- Total cost per model
- Cost per token (efficiency)

### Recent Tasks Table

Shows last 20 tasks with:
- Task name
- Model used (color-coded)
- Tokens consumed
- Cost in USD
- Duration
- Status (success/error)

### Alerts

Automatically shows:
- ⚠️ Cost threshold exceeded
- ⚠️ Success rate below 80%

---

## Hourly Sync Script

`supabase-sync.js` runs every hour (via cron) and:

1. **Syncs Memories** - Extracts memories from `memory/YYYY-MM-DD.md` → Supabase
2. **Calculates Metrics** - Aggregates last 24h data
3. **Updates Dashboard** - Stores metrics for UI
4. **Sends Alerts** - Email if cost exceeds threshold
5. **Cleans Up** - Deletes records older than 90 days

### Manual Run

```bash
node supabase-sync.js
```

### Cron Setup

```bash
# Run every hour at :00
0 * * * * cd /Users/abundance/.openclaw/workspace && node supabase-sync.js

# Run every 6 hours
0 */6 * * * cd /Users/abundance/.openclaw/workspace && node supabase-sync.js

# Run at 8 AM daily
0 8 * * * cd /Users/abundance/.openclaw/workspace && node supabase-sync.js
```

---

## Configuration

### `.env.local`

Required variables:

```
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Mailgun
MAILGUN_API_KEY=mg-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MAILGUN_DOMAIN=sandboxxxxxxxxx.mailgun.org

# Alerts
ALERT_EMAIL=abundancep@icloud.com
COST_THRESHOLD_DAILY=10.0
```

### Dashboard Config (in Supabase)

Edit the `dashboard_config` table:

```
dashboard_title          → "Agent Performance Dashboard"
refresh_interval_ms      → 5000 (5 seconds)
show_kimi_savings        → true
cost_threshold_alert     → 10.0
```

---

## Cost Analysis

### Pricing Breakdown

| Service | Free Tier | After Free Tier |
|---------|-----------|-----------------|
| **Supabase** | 500MB storage, 2GB/mo bandwidth | $25/mo for 8GB |
| **Mailgun** | 5,000 emails/mo | $0.50 per 1,000 emails |

### Monthly Cost Examples

| Usage | Supabase | Mailgun | Total |
|-------|----------|---------|-------|
| 100 tasks, 1K emails | Free | Free | **$0** |
| 1K tasks, 10K emails | Free | Free | **$0** |
| 10K tasks, 100K emails | Free | $50 | **$50/mo** |
| 100K tasks, 1M emails | $25 | $500 | **$525/mo** |

---

## Troubleshooting

### "Cannot connect to Supabase"

```bash
# Check URL is correct
curl https://your-project.supabase.co/rest/v1/

# Verify keys in .env.local
grep SUPABASE .env.local

# Test with Node
node -e "const s = require('@supabase/supabase-js'); console.log('OK')"
```

### "Mailgun email not sending"

1. Check API key is correct: `grep MAILGUN .env.local`
2. If sandbox domain: add recipient to authorized list in Mailgun dashboard
3. Check email format: must be valid email address
4. Check spam folder
5. View Mailgun logs: Dashboard → Logs

### "Sync script fails"

```bash
# Run with verbose output
DEBUG=* node supabase-sync.js

# Check file permissions
chmod +x supabase-sync.js

# Check Node version
node --version  # Should be 14+

# Check dependencies installed
npm list @supabase/supabase-js
```

### "Dashboard shows no data"

1. Ensure at least one task has been logged
2. Run sync manually: `node supabase-sync.js`
3. Check Supabase table: Dashboard → Table Editor → task_log
4. Verify CORS if web-deployed: Supabase → Settings → API → CORS

---

## Integration Examples

### Example 1: Log API Call

```javascript
const { logTask } = require('./supabase-integration');

async function callAPI(endpoint) {
  const start = Date.now();
  try {
    const response = await fetch(endpoint);
    const duration = Date.now() - start;
    
    await logTask({
      task_name: `api:${endpoint}`,
      model_used: 'direct-api',
      tokens_used: 0,
      cost: 0.01,
      duration_ms: duration,
      status: response.ok ? 'success' : 'error',
      error_message: response.ok ? null : `HTTP ${response.status}`
    });
    
    return response;
  } catch (err) {
    await logTask({
      task_name: `api:${endpoint}`,
      model_used: 'direct-api',
      tokens_used: 0,
      cost: 0,
      duration_ms: Date.now() - start,
      status: 'error',
      error_message: err.message
    });
    throw err;
  }
}
```

### Example 2: Daily Summary Email

```javascript
const { calculateMetrics, sendEmail } = require('./supabase-integration');

async function sendDailySummary() {
  const metrics = await calculateMetrics();
  
  const html = `
    <h2>📊 Daily Agent Summary</h2>
    <ul>
      <li>Tasks: ${metrics.totalTasks}</li>
      <li>Tokens: ${metrics.totalTokens.toLocaleString()}</li>
      <li>Cost: $${metrics.totalCost.toFixed(4)}</li>
      <li>Success Rate: ${metrics.successRate}%</li>
    </ul>
  `;
  
  await sendEmail({
    to: 'abundancep@icloud.com',
    subject: `📊 Daily Summary - ${new Date().toLocaleDateString()}`,
    html
  });
}

// Run at 9 AM daily
// 0 9 * * * node -e "require('./supabase-integration').sendDailySummary()"
```

### Example 3: Track Model Performance

```javascript
const { logTask, getRecentTasks } = require('./supabase-integration');

async function compareModels() {
  const tasks = await getRecentTasks(1000);
  
  const models = {};
  tasks.forEach(t => {
    if (!models[t.model_used]) {
      models[t.model_used] = {
        count: 0,
        tokens: 0,
        cost: 0,
        errors: 0
      };
    }
    models[t.model_used].count++;
    models[t.model_used].tokens += t.tokens_used;
    models[t.model_used].cost += t.cost;
    if (t.status !== 'success') models[t.model_used].errors++;
  });
  
  // Calculate efficiency (tokens per dollar)
  const efficiency = {};
  Object.entries(models).forEach(([model, data]) => {
    efficiency[model] = (data.tokens / data.cost).toFixed(2);
  });
  
  return efficiency;
}
```

---

## Advanced Features

### Custom Metrics

Store custom metrics in `performance_metrics`:

```javascript
const { supabase } = require('./supabase-integration');

await supabase.from('performance_metrics').insert([
  {
    metric_type: 'custom_metric_name',
    metric_value: 42.5,
    period: 'last_hour',
    details: { foo: 'bar' }
  }
]);
```

### Export Data for Analysis

```bash
npm run export
# Outputs all task logs + metrics as JSON
```

### Real-Time Subscriptions

Use Supabase real-time:

```javascript
const { supabase } = require('./supabase-integration');

supabase
  .from('task_log')
  .on('INSERT', payload => {
    console.log('New task logged:', payload.new);
  })
  .subscribe();
```

### Custom Dashboard

Modify `live-dashboard.html` to:
- Add your own metrics
- Change color scheme
- Add custom charts
- Integrate with other systems

---

## Next Steps

1. ✅ Complete QUICKSTART.md (10 min)
2. ✅ Integrate with agent code (5 min)
3. ✅ Monitor dashboard daily (2 min)
4. ✅ Review weekly summaries (10 min)
5. ✅ Optimize based on metrics (ongoing)

---

## Support & Documentation

- **Quick Start:** `QUICKSTART.md`
- **Full Guide:** `SUPABASE_MAILGUN_INTEGRATION.md`
- **API Reference:** Comments in `supabase-integration.js`
- **Supabase Docs:** https://supabase.com/docs
- **Mailgun Docs:** https://documentation.mailgun.com
- **OpenClaw Docs:** https://docs.openclaw.ai

---

## License

MIT

---

**Last Updated:** 2024-01-15
**Status:** ✅ Production Ready
