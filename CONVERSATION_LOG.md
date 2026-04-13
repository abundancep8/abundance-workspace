# CONVERSATION_LOG.md — Daily Decisions & Frameworks

**Purpose:** Capture key decisions, frameworks, videos, and insights from conversations throughout the day. Feed into nightly self-improvement cycle.

**When to update:** After meaningful conversations, decisions, or learning moments.

---

## 2026-04-13

### Local Token Ledger System (02:00 AM)
- **Decision:** Build offline token tracking instead of waiting for Anthropic API
- **Rationale:** Previous infrastructure depended on external API release; created bottleneck
- **Insight:** Local JSON-based tracking provides immediate visibility, auditability, and control
- **Implementation:** 
  - `token-ledger.json` (daily/monthly spend tracking)
  - `token-ledger-script.sh` (updater with threshold alerts)
  - `token-ledger-README.md` (integration guide)
- **Framework:** Prefer self-contained systems over external dependencies; build for observation before relying on external APIs
- **Next:** Integrate ledger updates into hourly cron tasks; validate cost calculations against actual Anthropic bills

---

## 2026-04-10

### Token Monitoring (00:02)
- **Decision:** Continue hourly monitoring as scheduled
- **Insight:** Only 0.1% of daily budget spent in first 2 hours (normal sleep period)
- **Status:** Campaign systems running normally

---

## Template for Future Entries

```markdown
### [Time] — [Topic/Decision]
- **Decision:** What was decided?
- **Rationale:** Why this choice?
- **Insight:** What did we learn?
- **Action:** What comes next?
- **Framework:** Any pattern or system to remember?
```

---

## Monthly Rollup (April 2026)

### Decisions That Worked
- OAuth env variables for credential security (Apr 6)
- Hourly token monitoring instead of daily (Apr 9)
- Switching to organic X posting after API credit depletion (Apr 8)

### Frameworks to Codify
- Credential management pattern (env vars + git-ignore)
- Budget monitoring escalation (75% threshold → alert)
- Cron scheduling for autonomous campaigns

### Lessons to Capture in MEMORY.md
- Large campaigns need early budget safeguards
- Scheduled posting more reliable than autonomous blasts
- Daily consolidation prevents context loss
