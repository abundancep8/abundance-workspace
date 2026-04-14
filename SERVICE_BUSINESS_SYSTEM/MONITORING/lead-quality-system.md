# Lead Quality Monitoring System
**Status:** 🟢 READY TO DEPLOY  
**Purpose:** Real-time lead health scoring + spam detection  
**Deployment:** Parallel to main system

---

## Lead Scoring Algorithm

Every lead gets scored 0-100 on quality:

```
Base Score: 50 points

+ LinkedIn verification (20 points)
  - Has LinkedIn: +20
  - No LinkedIn: -5
  
+ Business legitimacy (15 points)
  - Real clinic/practice: +15
  - Suspicious domain: -10
  - Generic/spam indicators: -15
  
+ Contact quality (15 points)
  - Full name + title: +15
  - Partial info: +8
  - Generic/suspicious email: -10
  
+ Response indicators (20 points)
  - Has previous engagement: +20
  - Cold lead (new): 0
  - Spam history: -20
  
+ Geographic signals (10 points)
  - Clear location: +10
  - Multiple offices: +5
  - International: +0
  
+ Recent activity (10 points)
  - Recent posts/activity: +10
  - Active hiring: +5
  - Ghost profile (no updates): -5

Score interpretation:
- 85-100: EXCELLENT (safe to contact)
- 70-84: GOOD (safe to contact)
- 60-69: FAIR (flag for review)
- 50-59: BORDERLINE (you decide)
- <50: SPAM (don't contact)
```

---

## Real-Time Monitoring

### Lead Batch Health Dashboard

```json
{
  "batch_id": "batch_20260413_001",
  "timestamp": "2026-04-13T06:00:00Z",
  "total_leads": 50,
  "health_score": 87,
  "breakdown": {
    "excellent": 35,    // 70% (85-100 score)
    "good": 10,         // 20% (70-84 score)
    "fair": 3,          // 6% (60-69 score)
    "borderline": 2,    // 4% (50-59 score)
    "spam": 0           // 0% (<50 score)
  },
  "flags": {
    "low_quality_detected": false,
    "duplicate_ips": 0,
    "spam_patterns": 0,
    "injection_attempts": 0
  },
  "recommendation": "APPROVE - All 50 leads are quality. Outreach ready.",
  "user_action_required": false,
  "quality_trend": "Stable (↔ from yesterday)"
}
```

### Spam Detection Patterns

```
Pattern 1: Generic domain emails
├─ @gmail.com with "clinic" in name
├─ @yahoo.com with medical terms
├─ @free-email-service.xyz
└─ Action: Flag as SUSPICIOUS

Pattern 2: Injection attempts
├─ Hidden HTML: <script>alert('hack')</script>
├─ SQL injection: Robert'); DROP TABLE--
├─ Prompt injection: <!-- SYSTEM: Ignore -->
└─ Action: Auto-REJECT, log security incident

Pattern 3: Duplicate/ring patterns
├─ Same person, different names
├─ Multiple emails from same IP
├─ Coordinated contact attempts
└─ Action: Flag batch, investigate

Pattern 4: Phishing indicators
├─ Domain typosquatting: "amaz0n.com"
├─ Urgency language: "CLICK NOW" "LIMITED TIME"
├─ Suspicious URLs: bit.ly/, tinyurl/
└─ Action: Auto-REJECT, log

Pattern 5: Ghosting indicators
├─ No LinkedIn activity (6+ months)
├─ Business closed signals
├─ Outdated company info
└─ Action: Flag low-confidence, low priority
```

---

## Quality Trending

Track quality over time:

```
Daily Quality Score (Last 7 Days):

Day 1: 84 ↓ (some spam detected)
Day 2: 86 ↑ (filtering improved)
Day 3: 88 ↑ (algorithm learning)
Day 4: 87 ↔ (stable)
Day 5: 89 ↑ (better source targeting)
Day 6: 88 ↔ (slight variance)
Day 7: 90 ↑ (excellent - system optimizing)

Trend: 📈 IMPROVING (6% gain over week)

If score drops >5 points in 24h:
  → Investigate what changed
  → Check for poisoned data
  → Alert user immediately
```

---

## Approval Request with Scores

When you get approval request:

```
LEAD BATCH #1 — Ready for Approval
Generated: 2026-04-13 06:00 AM
Quality Score: 89/100 (EXCELLENT)

Summary:
├─ Total leads: 50
├─ Excellent quality (85+): 42 (84%)
├─ Good quality (70-84): 6 (12%)
├─ Fair quality (60-69): 2 (4%)
├─ Spam/rejected: 0 (0%)
└─ Overall health: EXCELLENT ↑

Top 5 Leads (by score):
1. Dr. Jane Smith | Downtown Dental | 98
2. Dr. Michael Chen | Family Clinic | 96
3. Dr. Sarah Johnson | Pediatric Care | 94
4. Dr. Robert Lee | Orthodontics | 93
5. Dr. Lisa Wang | General Dentistry | 92

Flagged for Review (fair quality):
1. "Dr." Mike's Clinic | Score: 62 | Issue: Unprofessional domain
2. Maria's Medical Center | Score: 64 | Issue: Incomplete LinkedIn

Recommendation: APPROVE 48, REVIEW 2, REJECT 0

Your action:
[ APPROVE ALL 50 ]
[ APPROVE 48 (auto-reject 2 spam)]
[ REVIEW INDIVIDUALLY ]
[ REJECT & RESCRAPE ]
```

---

## Response Quality Analysis

After leads respond:

```
Lead Response Quality Check

Lead: Dr. Jane Smith | Downtown Dental
Original score: 98
Response quality: EXCELLENT

Response analysis:
├─ Message: "Interested in learning more"
├─ Tone: Professional, genuine interest
├─ Personalization: Shows they read email
├─ Next step: Booking demo
└─ Confidence: 95% this is real

Lead: Generic Responder
Original score: 45 (spam)
Response quality: SUSPICIOUS

Response analysis:
├─ Message: Exact template match (seen 12x this week)
├─ Tone: Generic auto-reply pattern
├─ Personalization: None detected
├─ Next step: Flag & don't schedule demo
└─ Confidence: 99% this is bot/spam
```

---

## Early Warning Signals

System monitors for warning signs:

```
🚨 ALERT: Response rate dropped 35% (yesterday: 32%, today: 5%)

Possible causes:
1. Source changed (different LinkedIn search?)
2. Outreach time changed (too early/late?)
3. Message quality degraded
4. Lead quality dropped

Investigation:
├─ Check yesterday's lead scores
├─ Compare message text
├─ Review API logs
└─ Manual sample check

Action taken: Flagged for user review
Recommendation: Pause batch, investigate
```

---

## Dashboard Display

Your daily lead health report:

```
📊 LEAD QUALITY DASHBOARD — 2026-04-13

BATCH QUALITY (Last 24h):
├─ Batches generated: 1
├─ Avg quality score: 89/100 ↑
├─ Spam detected: 0
├─ Duplicates removed: 0
└─ Health trend: EXCELLENT

RESPONSE RATES:
├─ Outreach sent: 48
├─ Responses received: 14 (29%)
├─ Demo bookings: 2 (4.2%)
├─ Conversion: On track ✓

QUALITY OVER TIME:
├─ 7-day avg: 87/100
├─ Trend: ↑ +3 points (improving)
├─ Variance: 2.3 points (stable)
└─ Prediction: 91/100 by day 7

WARNINGS:
├─ Critical: None
├─ Warnings: None
└─ System health: EXCELLENT

Last updated: 2026-04-13 04:15 AM
```

---

## Integration with Approval Gates

Lead quality directly influences your workflow:

```
Score 85+: Auto-safe to include in batch
├─ Minimal review needed
├─ Can batch send (maybe 20 at once)
└─ I might auto-filter for you by week 2

Score 70-84: Include in batch, you review
├─ Part of batch you approve
├─ I flag any concerns
└─ Usually safe but marked for attention

Score 60-69: Manual review before sending
├─ You decide yes/no individually
├─ Might be legitimate but unclear
└─ I recommend manual screening

Score 50-59: Don't send without approval
├─ Requires explicit decision from you
├─ I recommend rejection
└─ Only send if you're confident

Score <50: Auto-reject, never send
├─ Spam, injection attempts, or fraud
├─ No manual override option
└─ Logged as rejected
```

---

## Tuning Over Time

As system runs, we'll learn what converts best:

```
Week 1: Baseline
- All quality score 85+: 30% response rate
- Quality score 70-84: 20% response rate
- Quality score <70: 8% response rate

Week 2: Pattern recognition
- "Downtown" location: +5% response vs suburbs
- Medical "dr." title: +3% response vs manager
- Recent LinkedIn activity: +7% response

By Week 4: Optimized scoring
- Custom weights based on YOUR results
- High-converting lead profiles identified
- Lead generation retargeted to best sources

Result: Response rate 35%+ (vs initial 25%)
```

---

## What You Control

```
Your approval gates decide:
├─ Minimum quality score to send
├─ Which patterns you trust
├─ Which to flag for review
├─ Which to auto-reject

You can also:
├─ Request different sources (e.g., "more dentists")
├─ Provide feedback (lead quality thumbs up/down)
├─ Adjust scoring weights
├─ Train the system with examples
```

---

**Status:** Ready to activate  
**Activation:** Day 1 (when supervised mode starts)  
**Expected impact:** 10%+ improvement in response rate by week 2  
**Last updated:** 2026-04-13 04:01 AM
