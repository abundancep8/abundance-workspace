# YouTube Monitor - Quick Reference

## Status: ⚠️ Setup Required

**Before first run, complete:**

1. [ ] Get YouTube API service account credentials
2. [ ] Save JSON key to `~/.openclaw/youtube-credentials.json`
3. [ ] Update `CHANNEL_ID` in `scripts/youtube-comment-monitor.py`
4. [ ] Test: `python3 scripts/youtube-comment-monitor.py`
5. [ ] Add cron job: `crontab -e` → add entry from setup guide
6. [ ] Create logs directory: `mkdir -p logs`

## What It Does

Every 30 minutes:

1. **Fetches** new comments from Concessa Obvius YouTube channel
2. **Categorizes** each comment:
   - **Questions** (how-to, tools, cost, timeline) → Auto-reply
   - **Praise** (amazing, inspiring, great) → Auto-reply
   - **Spam** (crypto, MLM, gambling) → Filtered
   - **Sales** (partnership, collaboration, sponsor) → Flagged for manual review
3. **Logs** all activity to `.cache/youtube-comments.jsonl`
4. **Reports** stats (total processed, auto-responses sent, flagged)

## Key Files

- `scripts/youtube-comment-monitor.py` — Main monitoring script
- `scripts/youtube-monitor-setup.md` — Full setup guide
- `.cron/youtube-monitor.cron` — OpenClaw cron config
- `.cache/youtube-comments.jsonl` — Log file (auto-created)
- `.cache/youtube-monitor-state.json` — Tracks processed comments (auto-created)
- `logs/youtube-monitor.log` — Cron execution log (create logs/ dir first)

## Quick Commands

### Test the script

```bash
cd ~/.openclaw/workspace
python3 scripts/youtube-comment-monitor.py
```

### View recent comments

```bash
tail -20 .cache/youtube-comments.jsonl | jq '.'
```

### Filter by category

```bash
# All questions
cat .cache/youtube-comments.jsonl | jq 'select(.category=="questions")'

# All flagged for review
cat .cache/youtube-comments.jsonl | jq 'select(.response_status=="flagged_for_review")'

# Recent 10 entries
tail -10 .cache/youtube-comments.jsonl | jq '.'
```

### Check cron logs

```bash
tail -f logs/youtube-monitor.log
```

### Manual sync (force immediate run)

```bash
python3 scripts/youtube-comment-monitor.py
```

## Editing Templates

Edit responses in `scripts/youtube-comment-monitor.py`:

```python
TEMPLATES = {
    "question": "Thanks for asking! [Your response here]",
    "praise": "Thank you so much! [Your response here]",
}
```

Changes take effect on next run.

## Category Examples

### Questions ❓
- "How do I get started?"
- "What tools do you use?"
- "How long does this take?"
- "Where can I find the docs?"

**→ Auto-reply with question template**

### Praise 👏
- "This is amazing!"
- "So inspiring, thank you!"
- "You're the best!"
- "Thanks for sharing!"

**→ Auto-reply with praise template**

### Sales 🤝
- "Would love to partner!"
- "Collaboration opportunity?"
- "Can we sponsor this?"
- "Interested in affiliate?"

**→ Flag for manual review (check daily)**

### Spam 🚫
- "Get rich with crypto!"
- "Join our MLM"
- "Free Bitcoin! Click here"
- "Casino gambling now!"

**→ Auto-filtered (no reply)**

## Monitoring Dashboard

To create a live dashboard of recent activity:

```bash
# Watch comments in real-time (new entries every 30 min)
watch -n 5 'tail -5 .cache/youtube-comments.jsonl | jq .'

# Category breakdown
echo "=== CATEGORY BREAKDOWN ===" && \
cat .cache/youtube-comments.jsonl | jq -r '.category' | sort | uniq -c

# Response status breakdown
echo "=== RESPONSE STATUS ===" && \
cat .cache/youtube-comments.jsonl | jq -r '.response_status' | sort | uniq -c

# Total count
echo "Total comments logged:" && \
wc -l .cache/youtube-comments.jsonl
```

## Troubleshooting

### No credentials error
→ Save YouTube API JSON to `~/.openclaw/youtube-credentials.json`

### Comments not fetching
→ Check CHANNEL_ID is correct (should start with UC)

### Cron not running
→ Check crontab: `crontab -l`
→ Check logs: `tail logs/youtube-monitor.log`

### Want to pause monitoring
→ Comment out the cron line: `# */30 * * * * ...`

## Report Format (Every 30 Min)

```
[2026-04-17 14:30:00] YouTube Comment Monitor started

{
  "timestamp": "2026-04-17T14:30:00.000000Z",
  "stats": {
    "total_processed": 12,
    "auto_responses_sent": 8,
    "flagged_for_review": 1,
    "errors": 0
  },
  "log_entries": {
    "total": 1248,
    "by_category": {
      "questions": 450,
      "praise": 380,
      "sales": 25,
      "spam": 320,
      "other": 73
    },
    "by_status": {
      "sent": 830,
      "spam_filtered": 320,
      "flagged_for_review": 25,
      "pending": 73
    }
  }
}
```

---

**Next step:** Follow `scripts/youtube-monitor-setup.md` to configure credentials and test.
