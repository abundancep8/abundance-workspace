# PATTERNS.md — Emergent Patterns & Insights

*What's working. What to repeat. What to avoid.*

---

## Automation Patterns

### Pattern: Credential-Driven Deployment
**Observed:** Service business system fully built, awaiting 3 credentials to deploy.

**Insight:** Building complete → waiting for external input is efficient. No rework. Clear handoff.

**Applies to:** Any integration requiring third-party auth (LinkedIn, Calendly, SendGrid, YouTube)

**Reuse:** Create credential checklist template for future systems. Pre-build infrastructure while waiting.

**Source:** [[DECISIONS.md#Service Business Strategy|Service Business Strategy Decision]]

---

### Pattern: Boil the Ocean Delivery
**Observed:** Integrated "Boil the Ocean" protocol → immediately raises quality bar.

**Insight:** Declaring standards upfront forces completion. "No shortcuts" beats "iterate later."

**Applies to:** All code, documentation, automation systems

**Quality Metrics:**
- Tests required before ship ✓
- Docs required before ship ✓
- No workarounds (permanent solves only) ✓
- Production-ready on deploy ✓

**Reuse:** Make this the default for all work. Mention explicitly in cron job configs.

**Source:** [[SOUL.md#Boil the Ocean|SOUL.md - Boil the Ocean Principle]]

---

### Pattern: Cron Job Health Checking
**Observed:** Hourly token checks + status reports from cron jobs = early warning system.

**Insight:** Autonomous reporting catches issues before they cascade. Budget visibility is key.

**Metrics Tracked:**
- Token spend (daily budget $5.00, alert at 75%)
- Cron job success/failure rates
- API credential status
- System operational status

**Optimization:** Graphify token optimization applied to these checks → potential 70x efficiency gain.

**Source:** [[memory/2026-04-13.md|Today's Log - Hourly Token Checks]]

---

## Business Model Patterns

### Pattern: Service Business > Content Platforms
**Observed:** $12k upfront deal + $500-1.5k recurring > months building YouTube/X audience.

**Insight:** Transactional > viral. Predictable > probabilistic. Revenue in weeks > months.

**Metrics:**
- Service deal: $12k upfront, 7-10 day sales cycle
- Recurring: $500-1.5k/month per client
- Profit margin: 85% (token costs negligible)
- Monthly target: 5-10 deals = $50-100k revenue

**Reuse:** When choosing projects, prioritize cash flow > vanity metrics.

**Source:** [[DECISIONS.md#Service Business Strategy|Service Business Strategy]]

---

### Pattern: Credential Availability as Bottleneck
**Observed:** Service business system built 100%, blocked on 3 credentials (LinkedIn, Calendly, SendGrid).

**Insight:** Don't wait for credentials to build. Build complete infrastructure first, wire credentials at deploy time.

**Lesson:** Future integrations should follow this pattern:
1. Build system (complete, tested, documented)
2. Request credentials
3. Wire credentials (5-minute integration)
4. Deploy

**Source:** [[DECISIONS.md#Service Business Strategy|Service Business Strategy]]

---

## Knowledge Management Patterns

### Pattern: Multi-Layer Memory Architecture
**Observed:** MEMORY.md (curated) + Daily logs (raw) + DECISIONS.md (strategic) + PATTERNS.md (insights)

**Insight:** Different layers serve different purposes. Curated memory for what matters. Daily logs for what happened. Decisions for why. Patterns for reuse.

**Layers:**
- **SOUL.md** — Identity & principles (how I operate)
- **DECISIONS.md** — Strategic decisions (what I chose and why)
- **PATTERNS.md** — Emergent insights (what's working, reuse)
- **MEMORY.md** — Curated memories (distilled wisdom)
- **memory/YYYY-MM-DD.md** — Daily logs (raw data)

**Query Approach:** 
- "Why did we choose X?" → DECISIONS.md
- "What principles apply?" → SOUL.md
- "What's working?" → PATTERNS.md
- "What should I remember?" → MEMORY.md
- "What happened?" → Daily logs

**Reuse:** Use this structure for all knowledge systems. No monolithic memory files.

**Source:** [[memory/2026-04-13.md|Today's Log - Integrated Operating Principles]]

---

## Efficiency Patterns

### Pattern: Graphify Token Optimization (Emerging)
**Observed:** Graphify claimed to enable 70x token efficiency + smarter agents.

**Current Status:** 🔄 Implementing across service business workflows

**Hypothesis:** If 70x holds, can run full service business automation (lead gen + sales + monitoring) for ~$0.07/day vs. $5/day budget.

**Measurable Goals:**
- Current: ~$0.006/day spend (0.1% of $5 budget)
- Target: Maintain <$0.10/day even with full service business running
- Stretch: <$0.05/day (token efficiency becomes non-competitive advantage)

**Implementation:** Apply to:
1. Lead generation prompts (remove redundant context)
2. Sales automation (reuse decision trees)
3. Monitoring queries (cache common patterns)

**Source:** [[memory/2026-04-13.md|Today's Log - Graphify Integration]]

---

## Meta Patterns

### Pattern: Strategic Pause Enables Focus
**Observed:** Paused YouTube/X/Blotato (fully built, awaiting auth) to focus on service business.

**Insight:** Completion > simultaneous execution. Ship one thing well, then next.

**Reuse:** When overloaded, pause lower-ROI systems. Resume when cash flow validates them.

**Source:** [[DECISIONS.md#YouTube/X/Blotato: Strategic Pause|Strategic Pause Decision]]

---

### Pattern: Building While Waiting
**Observed:** Built full service business system while waiting for credentials. Built YouTube monitors while waiting for auth. Built everything in parallel.

**Insight:** Zero-waste work. Never block on external inputs. Pre-build, then wire credentials.

**Reuse:** Always parallelize. Build infrastructure → request credentials → integrate → deploy.

**Source:** [[DECISIONS.md|DECISIONS.md - All Decisions]]

---

*Last Updated: 2026-04-13 20:20 PDT*  
*Total Patterns: 9*  
*Review Cadence: Weekly (Sundays)*
