# MEMORY.md — Long-Term Learning Log

## Current Projects

### Campaign 1: X Marketing + Landing Page
- **Status:** Infrastructure deployed (April 6)
- **Setup:** OAuth credentials secure (env vars), cron scheduler active, landing page on Vercel
- **Next:** Monitor cron execution, daily metrics reports starting April 7 morning
- **Key Decision:** Use environment variables for credentials, not prompts. Vercel auto-deploy from git branch.
- **Expected:** 10-day campaign, 2-3 posts/day, revenue tracking $2,860–$11,600

## Patterns & Systems

### Daily Workflow
- Hourly token monitoring via cron (catches budget drift early)
- Heartbeat polls available but not configured yet
- Daily logs at memory/YYYY-MM-DD.md (raw notes)
- Weekly consolidation into MEMORY.md (distilled learnings)

### Credential Management
- Store all secrets in `.secrets/` or environment variables
- Never paste credentials in prompts
- Use `.env` files loaded at runtime (git-ignored)
- OAuth tokens regenerated before expiry

### Git & Deployment
- One commit per major milestone
- Clean branches for production (e.g., `vercel-clean`)
- Vercel auto-deploys on push to specified branch

## Lessons Learned

1. **Large Files:** >100MB files need git-lfs or exclusion from `.gitignore` to avoid bloat
2. **Secure Workflow:** Environment variables > hardcoded secrets
3. **Scheduled Posting:** Cron jobs more reliable than autonomous blasts for content campaigns
4. **Token Budget:** Daily $5.00 budget with 75% alert threshold. Monitor hourly.

## Improvements Implemented

**2026-04-07:** Created MEMORY.md as central long-term memory hub. Established pattern for daily learning capture and weekly consolidation.

**2026-04-09:** Created API_COST_TRACKER.md to separate external API costs (X, Printify, Etsy, Stripe, Gumroad) from OpenClaw token costs. Integrated hourly monitoring rules. Prevents repeat of Apr 8 X API credit depletion ($50 spent without warning).

---

## APRIL 8 STATUS (11:28 AM PDT)

**Campaign Live:**
- X Post #1: 2041569702602735636 (Apr 7, 10:31 AM)
- X Post #2: 2041944361529683972 (Apr 8, 11:20 AM)
- YouTube: 50+ shorts deployed (auto-uploading continues)
- Landing page: LIVE (abundance-workspace.vercel.app)

**Critical Fix:**
- X API credits depleted ($50 spent, no warning) → Switched to organic posting
- Hourly token tracking now active
- Agent blocking removed (execution mode)

**New Agent Mandates:**
- Research X algorithm daily
- Optimize posts for landing page traffic
- Up to 3x/day posting for testing
- Self-correct based on performance data
- Assertive + proactive growth actions

**Tonight's Schedule:**
- 8:00 PM: Post #3 deploy
- Hourly token checks
- 2:00 AM: Nightly cycle
- 2:30 AM: Git backup

**Token Budget:** Now with hourly monitoring, tight optimization. No surprises.
