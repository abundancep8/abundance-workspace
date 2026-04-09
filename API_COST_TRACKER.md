# API Cost Tracker — External Paid Services

**Purpose:** Track spending on all paid external APIs (X, Printify, Etsy, Stripe, Gumroad, etc.) separately from OpenClaw token costs.

**Alert Thresholds:** 50%, 75%, 100% of budget per service.

---

## Current Accounts

### Twitter/X API
- **Service:** X API v2 (organic posting)
- **Status:** ⏸️ DEPLETED (Apr 8, 11:16 AM)
- **Monthly Limit:** $50 (est. 300K organic posts @ $0.05/post)
- **Spent:** $50.00 (100% ❌)
- **Reset Date:** TBD (awaiting recharge or credit decision)
- **Last Charge:** Unknown date
- **Posts Made:** ~18 posts (Apr 6-8)
- **Cost per Post:** ~$2.70 avg (expensive rate — likely overuse)

**Action:** User must either:
1. Add credits to X API account ($15-100)
2. Switch to organic/manual posting
3. Use X native scheduler (free)

---

### Printify API
- **Service:** Printify Premium + API access
- **Status:** ⏳ PENDING ACTIVATION (email sent ~Apr 7)
- **Monthly Cost:** ~$10-40/month (TBD by tier)
- **Activation:** Awaiting confirmation email after payment
- **Used By:** TikTok Shop inventory sync + Etsy integration
- **Critical For:** $3K-10K/month revenue (TikTok Shop)

**Action:** User to check email for Printify activation. Once activated, API cost tracking begins.

---

### Gumroad API
- **Service:** Gumroad product hosting + affiliate/resale
- **Status:** ✅ READY (no monthly fee, 10% transaction fee)
- **Transaction Fee:** 10% of product sales
- **Spent:** $0 (no sales yet; Apr 8-9)
- **Products:** 3 products loaded (waiting manual publish or automation)

**Tracking:** Monitor monthly transaction costs as revenue builds.

---

### Etsy API / Shop
- **Service:** Etsy Shop + API (if applicable)
- **Status:** ⏳ PENDING (email sent for API approval)
- **Monthly Cost:** ~$19.95 shop fee + payment processing
- **Spent:** $0 (not yet activated)

**Tracking:** Once activated, track $19.95/month + transaction fees.

---

### Stripe (Payment Processing)
- **Service:** Stripe payment processor (landing page checkout)
- **Status:** ⏳ INTEGRATED (Vercel landing page checkout active)
- **Transaction Fee:** 2.9% + $0.30 per transaction
- **Spent:** $0 (no transactions yet; Apr 8-9)

**Tracking:** Monitor per transaction as revenue builds.

---

### YouTube Partner / AdSense
- **Service:** YouTube monetization (Super Chat, ads)
- **Status:** ⏳ PENDING CHANNEL FIX (channel empty, no videos)
- **Revenue Share:** 55% YouTube keeps, 45% creator
- **Spent:** $0 (no content uploaded yet)
- **Blocker:** Blotato authentication not completed

**Tracking:** Once 50+ shorts uploaded, monitor weekly revenue.

---

## Monthly Budget Allocation

| Service | Monthly Budget | Alert @ 50% | Alert @ 75% | Current % Used |
|---------|---|---|---|---|
| X API | $50 | $25 | $37.50 | **100% ❌** |
| Printify | $40 | $20 | $30 | TBD |
| Etsy | $25 | $12.50 | $18.75 | 0% |
| Stripe | ∞ | N/A | N/A | 0% |
| Gumroad | ∞ | N/A | N/A | 0% |
| **TOTAL** | **$115** | | | |

---

## Hourly Monitoring Rules

**During cron token checks (hourly), ALSO:**

1. Log any new external API charges since last check
2. Calculate % spent on each service
3. If ANY service > 50%, post **yellow alert** 🟡
4. If ANY service > 75%, post **red alert** 🔴
5. If ANY service = 100%, post **critical alert** 🚨 (block further API calls)

**Example Alert Message:**
```
🔴 API COST ALERT (2:00 AM check)
X API: $50.00 / $50.00 (100% — DEPLETED)
Stripe: $0.00 / unlimited
Action needed: Recharge X API or switch to organic posting
```

---

## Logging Template

When implementing hourly alerts, add to daily memory:

```markdown
### HH:MM - Hourly API Cost Check
- X API: $X.XX / $50.00 (Y%)
- Printify: $X.XX / $40.00 (Y%)
- Etsy: $X.XX / $25.00 (Y%)
- Stripe: $X.XX / unlimited
- Status: [🟢 OK | 🟡 CAUTION (50-75%) | 🔴 WARNING (75-100%) | 🚨 CRITICAL (100%)]
```

---

## Fix Applied

**2026-04-09 02:00 AM:**
- Created API_COST_TRACKER.md
- Documented all paid services + budget allocation
- Set hourly monitoring rules + alert thresholds
- Prevents future surprise depletion like Apr 8 X API incident

**Why:** Tokens (OpenClaw inference) ≠ API Credits (X, Printify, Etsy, etc.). Separate tracking required.
