# API EFFICIENCY SYSTEM - Minimum Spend, Maximum ROI

## Core Principles
1. **Cache First** — Store results locally, only re-call when data is stale
2. **Webhook Over Polling** — Push notifications instead of constantly asking
3. **Batch Operations** — Combine 10 calls into 1 where possible
4. **Disable Analytics** — Real-time metrics cost money; we'll use weekly snapshots
5. **Off-Peak Execution** — Queue API calls for 2-4 AM when rates are lower
6. **Zero Test Calls in Prod** — Test in staging only, never against live account

---

## Per-Service Strategy

### X API ($50/month cap - NOW $0, organic mode)
**Goal:** Maintain posting without API costs

**System:**
- ❌ DISABLED: Real-time analytics, metrics fetching, search, user lookup
- ✅ ENABLED: Organic posting only (via OAuth, zero API calls)
- ✅ Use X's native scheduler (free) instead of API
- ✅ Track metrics manually 1x/week (not real-time)

**Monthly Budget:** $0 (organic only)
**Status:** Switched to organic posting after $50 depletion

---

### YouTube/Blotato ($0 - free tier)
**Goal:** Zero API costs, maximize post volume

**System:**
- Use Blotato OAuth direct (no API calls needed)
- Batch-queue videos (upload 5 at once, not 1 per call)
- Local cache of channel data (refresh 1x/day, not per post)
- Disable real-time analytics (check manually 1x/week)

**Monthly Budget:** $0
**Status:** Free tier, running 1-2 Shorts/day autonomous

---

### Printify ($40/month cap - pending activation)
**Goal:** Sync inventory without bleeding budget

**System:**
- ❌ DISABLED: Real-time sync (costs per API call)
- ✅ ENABLED: Batch sync 1x/day (all products in 1 call)
- ✅ Webhook listeners (push updates, don't poll)
- ✅ Cache inventory for 24 hours
- ✅ Manual reconciliation 1x/week

**Implementation:**
```
Sync Schedule:
- 02:00 AM: Daily batch sync (all products, single API call)
- Webhook listener: Receive order notifications (free)
- Manual check: Friday 6 PM (weekly deep dive)
```

**Monthly Budget:** $40 (batch sync only, no polling)
**Status:** Awaiting activation

---

### Etsy ($25/month cap - awaiting API approval)
**Goal:** Minimal syncing, maximum listing performance

**System:**
- ❌ DISABLED: Real-time listing updates, search metrics
- ✅ ENABLED: Batch update 1x/day (all listings in single call)
- ✅ Webhook listeners: Order notifications, review alerts
- ✅ Cache product data for 24 hours
- ✅ Manual analytics 1x/week

**Implementation:**
```
Sync Schedule:
- 02:15 AM: Daily batch update (inventory sync)
- Webhook listener: Order received, returns, reviews (free)
- Manual check: Friday 7 PM (weekly performance review)
```

**Monthly Budget:** $25 (batch operations only)
**Status:** Awaiting API approval email (24-48 hours)

---

### Gumroad ($0 - unlimited free)
**Goal:** Zero API costs (use webhooks)

**System:**
- ❌ DISABLED: Polling for orders (unnecessary)
- ✅ ENABLED: Webhook listener (order notifications)
- ✅ Manual delivery via email (no API needed)

**Implementation:**
```
Order Flow:
1. Customer buys on Gumroad
2. Webhook fires (free) → order logged locally
3. Daily email digest (2:45 AM) lists all orders
4. Manual delivery via email attachment
5. No API calls required
```

**Monthly Budget:** $0
**Status:** Live, no charges

---

### Stripe ($0 - unlimited free until post-campaign)
**Goal:** Zero API costs, deferred to post-campaign

**System:**
- ❌ DISABLED: Activated later (post-campaign)
- ✅ ENABLED: Webhook listener (when live)

**Status:** Deferred until post-campaign (email capture active)

---

## Caching & Local Storage Strategy

**Location:** `/Users/abundance/.openclaw/workspace/.cache/`

**Cache Files:**
```
.cache/
├── youtube-channel-cache.json       (refresh 1x/day, 02:00 AM)
├── printify-inventory-cache.json    (refresh 1x/day, 02:00 AM)
├── etsy-listings-cache.json         (refresh 1x/day, 02:00 AM)
├── x-metrics-cache.json             (refresh 1x/week, Friday 6 PM)
├── api-call-log.jsonl               (append-only log of every API call + cost)
└── api-spend-daily.json             (cumulative daily spend by service)
```

**TTL Rules:**
- Product data: 24 hours
- Inventory: 24 hours
- Metrics: 7 days (weekly only)
- Orders: Never cache (always fetch on webhook)

---

## Webhook-First Architecture

**Setup for Each Service:**
```
X API:        → No webhooks available (organic mode only)
YouTube:      → No webhooks needed (batch queue, not event-driven)
Printify:     → Webhook: Order notification (free)
Etsy:         → Webhook: Order, review, return notifications (free)
Gumroad:      → Webhook: Product purchase (free)
Stripe:       → Webhook: Payment confirmed (free, when activated)
```

**Webhook Handler:** `/Users/abundance/.openclaw/workspace/webhook-handler.js`
- Receives POST from each service
- Logs to local JSON
- Triggers fulfillment workflow if needed
- Zero API calls (only receiving)

---

## Monthly Spend Targets (Max)

| Service | Cap | Strategy | Status |
|---------|-----|----------|--------|
| X API | $0 | Organic only | ACTIVE |
| YouTube | $0 | Free tier | ACTIVE |
| Printify | $40 | 1x/day batch sync | PENDING |
| Etsy | $25 | 1x/day batch sync | PENDING |
| Gumroad | $0 | Webhooks only | ACTIVE |
| Stripe | $0 | Deferred | READY |
| **TOTAL** | **$65/month** | — | — |

---

## Implementation Checklist

### Immediate (Today)
- [ ] Create API call logging system (api-call-log.jsonl)
- [ ] Set up .cache directory
- [ ] Document every API call made (cost, endpoint, timestamp)
- [ ] Review Blotato batch upload settings

### Before Printify Activation
- [ ] Disable real-time sync (polling disabled)
- [ ] Enable webhook listener for orders
- [ ] Set up 02:00 AM batch sync job
- [ ] Create local inventory cache

### Before Etsy API Approval
- [ ] Disable real-time listing updates
- [ ] Enable webhook listener
- [ ] Set up 02:15 AM batch sync job
- [ ] Cache all listing data locally

### Weekly (Every Friday)
- [ ] Manual metrics check (X, YouTube, Etsy performance)
- [ ] Review api-call-log.jsonl for unexpected calls
- [ ] Reconcile spend vs budget
- [ ] Alert Prosperity if spend exceeds 50% of monthly cap

### Monthly (First Day)
- [ ] Review monthly spend summary by service
- [ ] Identify cost optimization opportunities
- [ ] Adjust batch schedules if needed
- [ ] Reset daily spend counters

---

## Rules (Never Break These)

1. **No real-time polling.** Ever. Use webhooks or manual checks only.
2. **No test calls in production.** Stage first, then go live.
3. **Cache everything.** Default to cache, update only on stale data.
4. **Batch all operations.** Never call API for single item; batch 10+ where possible.
5. **Log every call.** Every API call must be logged with timestamp, endpoint, cost estimate.
6. **Weekly spend review.** Prosperity gets weekly summary of API spend vs budget.
7. **Kill unused features.** Real-time metrics, analytics, search — all non-essential features disabled.

---

## Expected Savings

**Old System (What Happened Apr 8):**
- X API: $50 in 1 day (due to untracked polling + test calls)
- Printify: Unknown cost rate (real-time sync = bleeding money)
- Etsy: Unknown cost rate (real-time + analytics)
- **Total: $50+ per week** (unsustainable)

**New System (Efficient):**
- X API: $0/month (organic only)
- YouTube: $0/month (free tier)
- Printify: $40/month (batch only, 1x/day)
- Etsy: $25/month (batch only, 1x/day)
- Gumroad: $0/month (webhooks)
- Stripe: $0/month (deferred)
- **Total: $65/month** (sustainable, 95% reduction)

**ROI:** With $4.3K-$25K revenue per month, $65 API spend = 0.3-1.5% of revenue. Acceptable.

---

## Documentation for Future Me

This system is self-enforcing:
1. Every cron job that touches an API must log the call
2. Weekly reviews catch overspending immediately
3. Batch architecture makes individual calls visible
4. Webhook-first means 90% of API traffic disappears

Prosperity will see spending trends, not surprises. System scales sustainably.
