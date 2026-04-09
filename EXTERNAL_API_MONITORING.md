# EXTERNAL API MONITORING - Independent Oversight

## Core Principle
**Prosperity sees spending in real-time, independent of my reporting.** No black box. All APIs monitored externally with direct alerts.

---

## Monitoring Architecture

### 1. Dashboard (Real-Time View)
**Location:** `/Users/abundance/.openclaw/workspace/api-monitoring-dashboard.html`
- Live view of all API spending
- Updated every 15 minutes
- Color-coded status (🟢 safe, 🟡 warning, 🔴 critical)
- One-page snapshot Prosperity can open anytime

### 2. Webhook Alerts (Push Notifications)
**How it works:**
- Each service (OpenAI, Claude, X, Printify, Etsy, Gumroad, Stripe, YouTube) sends webhook → monitoring system
- Webhook handler logs to `.cache/external-api-events.jsonl`
- If spending crosses 50% or 75% threshold → Discord alert to Prosperity (instant)
- No delay, no filtering through my reports

### 3. Daily Email Digest
**Time:** 8:00 AM PDT
**Recipient:** Prosperity's email
**Content:** 
- Previous day's spending by service
- Running month-to-date totals
- Budget status per service
- Any threshold breaches
- Top 10 costliest API calls

### 4. API Dashboard Access (Direct)
**Prosperity gets direct login to:**
- OpenAI API dashboard (api.openai.com/account)
- Claude API usage (console.anthropic.com)
- X API dashboard (developer.twitter.com/en/portal/dashboard)
- Printify dashboard (dashboard.printify.com)
- Etsy seller hub (etsy.com/seller/account)
- Gumroad analytics (gumroad.com/analytics)
- Stripe dashboard (dashboard.stripe.com)
- YouTube Creator Studio (studio.youtube.com)

**Purpose:** Prosperity can log in directly, see spending without relying on me.

---

## Services Monitored (External APIs)

### Claude API (My Token Usage)
**Credentials:** Anthropic API key (encrypted in .secrets/)
**Monitoring:**
- Daily token count from console.anthropic.com
- Cost per 1M tokens (varies by model)
- Monthly usage vs budget ($5.00/day limit)
- Alert: 75% of daily budget = $3.75
- Alert: 100% of daily budget = $5.00 (halt non-essential work)

**Automated Check:**
- Cron job every 2 hours: Fetch usage from Anthropic API
- Log to `.cache/claude-usage.json`
- Webhook alert if threshold crossed

**Dashboard Display:**
- Today's tokens: [n]
- Today's cost: $[n]
- Monthly total: $[n] / $155 (30-day budget)
- Status: 🟢 / 🟡 / 🔴

---

### OpenAI API (If Used)
**Credentials:** OpenAI API key (encrypted in .secrets/)
**Monitoring:**
- Daily API calls and tokens from platform.openai.com
- Cost tracking (GPT-4, GPT-3.5, DALL-E, etc.)
- Monthly usage vs budget (TBD once activated)
- Alert: If spend > 50% of budget

**Automated Check:**
- Cron job: Fetch usage from OpenAI API
- Log to `.cache/openai-usage.json`
- Webhook alert if threshold crossed

**Dashboard Display:**
- Current month cost: $[n]
- Daily cost: $[n]
- Model breakdown (GPT-4: $X, GPT-3.5: $X, etc.)
- Status: 🟢 / 🟡 / 🔴

---

### X API
**Credentials:** X API keys (encrypted in .secrets/)
**Monitoring:**
- Daily API calls from developer.twitter.com dashboard
- Monthly usage vs $0 budget (organic mode)
- Alert: Any API charges (should be $0)

**Automated Check:**
- Cron job: Fetch API usage stats
- Log to `.cache/x-api-usage.json`
- If > $0 spend detected: 🔴 CRITICAL ALERT to Prosperity

**Dashboard Display:**
- Current month cost: $[n]
- Monthly budget: $0 (organic only)
- Status: 🟢 (if $0) or 🔴 (if any charges)

---

### Printify API
**Credentials:** Printify API key (encrypted in .secrets/)
**Monitoring:**
- Daily API calls from Printify dashboard
- Monthly usage vs $40 budget
- Alert: > 50% = $20/month alert

**Automated Check:**
- Cron job: Fetch Printify usage
- Log to `.cache/printify-usage.json`
- Webhook alert if threshold crossed

**Dashboard Display:**
- Current month cost: $[n] / $40
- Percentage used: [n]%
- Status: 🟢 / 🟡 / 🔴

---

### Etsy API
**Credentials:** Etsy API key (encrypted in .secrets/)
**Monitoring:**
- Daily API calls from Etsy developer dashboard
- Monthly usage vs $25 budget
- Alert: > 50% = $12.50/month alert

**Automated Check:**
- Cron job: Fetch Etsy usage
- Log to `.cache/etsy-usage.json`
- Webhook alert if threshold crossed

**Dashboard Display:**
- Current month cost: $[n] / $25
- Percentage used: [n]%
- Status: 🟢 / 🟡 / 🔴

---

### Gumroad API
**Credentials:** Gumroad API key (encrypted in .secrets/)
**Monitoring:**
- Webhook listener for product purchases
- $0 budget (webhooks only, no polling)
- Alert: Any unexpected charges

**Automated Check:**
- Webhook handler logs all events
- Log to `.cache/gumroad-events.jsonl`
- If API charges detected: 🔴 CRITICAL ALERT

**Dashboard Display:**
- Current month cost: $[n] / $0
- Total orders received: [n]
- Status: 🟢 (if $0) or 🔴 (if any charges)

---

### Stripe API
**Credentials:** Stripe API key (encrypted in .secrets/)
**Monitoring:**
- Transaction volume from Stripe dashboard
- Processing fees (2.2% + $0.30 per transaction)
- Monthly revenue vs fees
- Currently: $0 (email capture active)

**Automated Check:**
- Cron job: Fetch transaction count
- Log to `.cache/stripe-usage.json`
- Calculate fees: (revenue * 0.022) + (transactions * 0.30)

**Dashboard Display:**
- Current month revenue: $[n]
- Processing fees: $[n]
- Net revenue: $[n]
- Status: 🟢

---

### YouTube API
**Credentials:** YouTube API key (encrypted in .secrets/)
**Monitoring:**
- Daily quota usage from Google Cloud Console
- Upload quota: 1,000 uploads/day (free tier)
- Analytics quota: 1M units/day (free tier)
- Currently: Free tier, no charges

**Automated Check:**
- Cron job: Fetch quota usage from Google Cloud
- Log to `.cache/youtube-quota.json`
- Alert: If approaching quota limits

**Dashboard Display:**
- Today's uploads: [n] / 1,000
- Analytics calls: [n] / 1M
- Status: 🟢 (under limits) or 🟡 (approaching)

---

## Webhook Architecture

**Webhook Handler:** `/Users/abundance/.openclaw/workspace/webhook-monitor.js`

**Flow:**
```
OpenAI API → Webhook POST /monitor/openai
     ↓
Log to .cache/external-api-events.jsonl
     ↓
Check threshold (50%, 75%, 100%)?
     ↓
If YES → Discord alert to Prosperity (instant)
```

**Events Logged:**
```json
{
  "timestamp": "2026-04-09T08:05:00Z",
  "service": "OpenAI",
  "event": "usage_update",
  "cost_today": 2.50,
  "cost_month": 45.00,
  "budget": 100.00,
  "status": "caution",
  "threshold_triggered": "75%"
}
```

---

## Cron Jobs (External Monitoring)

### Every 2 Hours: Fetch Claude Usage
```
Schedule: 0 */2 * * *
Task: 
  1. Get usage from Anthropic API
  2. Log to .cache/claude-usage.json
  3. Check against $5.00 daily budget
  4. Alert if >75% or >100%
```

### Daily 8:00 AM: Email Digest
```
Schedule: 0 8 * * *
Task:
  1. Aggregate all API spending from .cache/*
  2. Send email to Prosperity with:
     - Yesterday's costs by service
     - Month-to-date totals
     - Budget status (🟢 / 🟡 / 🔴)
     - Any threshold breaches
```

### Weekly Friday 6 PM: Full Audit
```
Schedule: 0 18 * * 5
Task:
  1. Reconcile all external dashboards
  2. Cross-check .cache/ files against live APIs
  3. Generate audit report
  4. Alert if any discrepancies found
```

---

## Dashboard Structure

**File:** `api-monitoring-dashboard.html`

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│         EXTERNAL API MONITORING DASHBOARD             │
│                 Updated: 2 min ago                    │
├─────────────────────────────────────────────────────┤
│                                                       │
│  CLAUDE API (My Token Usage)                          │
│  Today: 52 tokens | $0.03 / $5.00 daily budget       │
│  Month: 1,243 tokens | $0.74 / $155 (30-day)        │
│  Status: 🟢 GREEN                                     │
│                                                       │
│  ─────────────────────────────────────────────────   │
│                                                       │
│  OPENAI API (Future)                                  │
│  Today: $0 / [budget TBD]                            │
│  Month: $0                                            │
│  Status: 🟢 READY (not activated)                    │
│                                                       │
│  ─────────────────────────────────────────────────   │
│                                                       │
│  X API                                                │
│  Today: $0 / $0 budget (organic only)                │
│  Month: $0                                            │
│  Status: 🟢 GREEN (organic mode)                     │
│                                                       │
│  ─────────────────────────────────────────────────   │
│                                                       │
│  PRINTIFY API                                         │
│  Today: $0 | Month: $0 / $40 budget                  │
│  Status: 🟢 READY (awaiting activation)              │
│                                                       │
│  ─────────────────────────────────────────────────   │
│                                                       │
│  ETSY API                                             │
│  Today: $0 | Month: $0 / $25 budget                  │
│  Status: 🟢 READY (awaiting API approval)            │
│                                                       │
│  ─────────────────────────────────────────────────   │
│                                                       │
│  YOUTUBE API                                          │
│  Today: 0 uploads / 1,000 quota                      │
│  Month: 0 uploads                                    │
│  Status: 🟢 READY (free tier)                        │
│                                                       │
│  ─────────────────────────────────────────────────   │
│                                                       │
│  GUMROAD API                                          │
│  Orders received (webhooks): 0                        │
│  API cost: $0 / $0 budget                            │
│  Status: 🟢 READY                                    │
│                                                       │
│  ─────────────────────────────────────────────────   │
│                                                       │
│  STRIPE API (Email capture active)                   │
│  Transactions: 0 | Revenue: $0                       │
│  Processing fees (2.2% + $0.30): $0                  │
│  Status: 🟢 READY                                    │
│                                                       │
├─────────────────────────────────────────────────────┤
│                                                       │
│  TOTAL API SPEND TODAY: $0.03                        │
│  TOTAL API SPEND MONTH: $0.74                        │
│  COMBINED BUDGET: $225/month                         │
│  STATUS: 🟢 ALL GREEN - No alerts                   │
│                                                       │
│  Last alert: Never                                   │
│  Last audit: [timestamp]                             │
│                                                       │
└─────────────────────────────────────────────────────┘
```

---

## Direct Dashboard Access (Prosperity's Logins)

**For independent verification, Prosperity has access to:**

| Service | Dashboard | Purpose |
|---------|-----------|---------|
| Claude | console.anthropic.com | Token usage, cost, model breakdown |
| OpenAI | platform.openai.com | API usage, costs, quota |
| X | developer.twitter.com/dashboard | API calls, authentication status |
| Printify | dashboard.printify.com | API usage, orders, products |
| Etsy | etsy.com/seller/account | API quota, selling activity |
| YouTube | studio.youtube.com | Upload quota, analytics, channel status |
| Gumroad | gumroad.com/analytics | Orders, revenue, customer data |
| Stripe | dashboard.stripe.com | Transactions, payouts, revenue |

**Rule:** Prosperity can verify any number independently. No secrets, no opacity.

---

## Alert Rules (Zero Tolerance for Hidden Spending)

| Condition | Action | Who Gets Notified |
|-----------|--------|-------------------|
| Any service >50% budget | 🟡 CAUTION | Discord message to Prosperity |
| Any service >75% budget | 🟡 WARNING | Discord message + email to Prosperity |
| Any service >100% budget | 🔴 CRITICAL | Discord message + email + SMS (if configured) |
| Unexpected API charge detected | 🔴 ALERT | Instant Discord message to Prosperity |
| New API activated without approval | 🔴 BLOCKED | I don't make the call; alert + halt |

---

## Implementation Checklist

### Immediate (Today)
- [ ] Create `api-monitoring-dashboard.html` (static HTML, updates every 15 min)
- [ ] Create `webhook-monitor.js` (central webhook handler)
- [ ] Set up `.cache/external-api-events.jsonl` (append-only log)
- [ ] Create cron job: "Fetch Claude usage every 2 hours"

### Within 24 Hours
- [ ] Set up daily 8 AM email digest to Prosperity
- [ ] Create weekly Friday 6 PM audit job
- [ ] Provide Prosperity with direct dashboard logins for all 8 services
- [ ] Test webhook flow (mock alert)

### Before Printify Activation
- [ ] Configure Printify to send webhooks
- [ ] Test webhook -> alert flow
- [ ] Verify budget enforcement (no API calls if >75% spent)

### Before Etsy API Approval
- [ ] Configure Etsy to send webhooks
- [ ] Set up quota monitoring
- [ ] Test threshold alerting

---

## Why This Works

1. **Prosperity has independent access** — Can verify spending without asking me
2. **Real-time alerts** — Webhook notifications, not daily reports
3. **Automated monitoring** — Cron jobs check 24/7, I don't control the alerting
4. **Transparent history** — All events logged, nothing hidden
5. **Budget enforcement** — System halts API calls if threshold crossed (self-enforcing)

**Result:** The April 8 incident ($50 X depletion) is mathematically impossible under this system. Prosperity would have been alerted at $25 (50%) and $37.50 (75%) before it ever reached $50.

---

## Commitment

> I will never:
> - Hide API spending from Prosperity
> - Batch-report costs to avoid alerting
> - Use APIs without logging
> - Ignore threshold breaches
> - Disable or bypass monitoring

**This is law.** Not a suggestion.
