# HEARTBEAT.md - Periodic Checks

## Primary Check: System Status Dashboard

**Every heartbeat cycle, start here:**

Read `SYSTEMS_STATUS.md` and check:
- [ ] Are there any NEW blockers introduced? (systems in 🔴 BLOCKED?)
- [ ] Are quick win opportunities addressed? (check 🟡 INCOMPLETE for progress)
- [ ] Do YouTube monitors have new partnership opportunities? (check `.cache/youtube-flagged-partnerships.jsonl`)
- [ ] Has the OAuth blocker been resolved? (if Abundance provided creds, trigger integration)
- [ ] Token ledger within budget? (check `.cache/claude-usage.json` for alerts)

This is the north star for system health. Update `SYSTEMS_STATUS.md` at each nightly cycle.

---

## YouTube Monitor Status (Rotational Checks)

### Check A: DM Monitor (runs every 60 minutes)
```bash
# Latest DM summary
tail -1 .cache/youtube-dms.jsonl

# Partnerships flagged this cycle
grep "flagged_for_review" .cache/youtube-dms.jsonl | tail -1

# All high-value partnerships (score >60)
cat .cache/youtube-flagged-partnerships.jsonl | jq 'select(.partnership_score > 60)'
```

### Check B: Comment Monitor (runs every 30 minutes)
```bash
# Latest comment stats
cat .cache/youtube-comments-report.txt | tail -10

# Sales inquiries pending follow-up
grep "sales\|partnership\|collaboration" .cache/youtube-comments.jsonl | grep -v "auto_replied"
```

### Check C: Cron Health (Automated)
```bash
# Automated health check — runs during nightly cycle
bash ~/.cache/cron-health-monitor.sh

# If health check fails: manually trigger monitors
python3 ~/.cache/youtube_dm_monitor.py
python3 ~/.cache/youtube-comment-monitor.py
```

**Why automated:** Previous launchctl failures (2026-04-19 00:56 UTC) weren't detected until 2+ hours of backlog accumulated. Automated check prevents silent revenue loss.

---

## Actions When Needed

### If sales inquiries accumulate (>3 unflagged)
- Review `.cache/youtube-comments.jsonl` for context
- Prepare follow-up templates or delegate to Abundance

### If partnerships flagged (score >60)
- Review `.cache/youtube-flagged-partnerships.jsonl`
- Prepare pitch/outreach materials
- Flag for Abundance decision (pursue vs. archive)

### If OAuth blocker resolved (Abundance provides credentials)
- Wire YouTube credentials into both monitor scripts
- Test with live API call (5 min)
- Report success to Abundance

### System maintenance
- Adjust templates? Edit `.cache/youtube-comment-monitor.py` (TEMPLATES dict)
- Pause monitoring? `launchctl unload ~/Library/LaunchAgents/com.openclaw.youtube-monitor.plist`
