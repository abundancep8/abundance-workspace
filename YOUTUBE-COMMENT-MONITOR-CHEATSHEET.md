# YouTube Comment Monitor - Quick Reference

## Status
- **Active**: ✅ Running every 30 minutes
- **Last Run**: Saturday, April 18, 2026 — 12:30 AM PT
- **Channel**: Concessa Obvius
- **Location**: `~/.openclaw/workspace/.cache/`

## Quick Commands

### View Latest Report
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments-report-current.txt
```

### View All Comments (JSON Lines)
```bash
tail -20 ~/.openclaw/workspace/.cache/youtube-comments.jsonl
jq . ~/.openclaw/workspace/.cache/youtube-comments.jsonl | less
```

### View JSON Stats
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments-report-current.json | jq .
```

### Run Now (Don't Wait 30 mins)
```bash
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

### Check If Running
```bash
launchctl list | grep youtube-comment-monitor
```

### View Execution Logs
```bash
tail -50 ~/.openclaw/workspace/.cache/logs/youtube-comment-monitor-*.log
```

### Stop It
```bash
launchctl unload ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
```

### Start It
```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
```

### Restart It
```bash
launchctl unload ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
sleep 2
launchctl load ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
```

## Category Rules

| Category | Examples | Auto-Response? | Action |
|----------|----------|---|---|
| **Questions** | "How do I...", "What tools...", "Timeline?" | ✅ Yes | Send template response |
| **Praise** | "Amazing!", "Love this!", "Inspiring" | ✅ Yes | Send thank you |
| **Spam** | "Crypto", "MLM", "Get rich", "Buy now" | ❌ No | Skip |
| **Sales** | "Partnership", "Collaborate", "Sponsorship" | ❌ No | Flag for review |

## File Structure

```
~/.openclaw/workspace/.cache/
├── youtube-comment-monitor.py          # Main script
├── youtube-comment-monitor-cron.sh     # Cron wrapper
├── com.openclaw.youtube-comment-monitor.plist
├── youtube-comments.jsonl              # 📊 Comment log (append-only)
├── youtube-comments-report-current.txt # 📝 Latest text report
├── youtube-comments-report-current.json # 📊 Latest JSON stats
├── youtube-comment-state.json          # State tracking
├── logs/
│   └── youtube-comment-monitor-*.log   # Execution logs
├── youtube-credentials.json            # [Optional] OAuth creds
└── youtube-token.json                  # [Optional] Auth token

~/Library/LaunchAgents/
└── com.openclaw.youtube-comment-monitor.plist  # Active agent
```

## Response Templates

**Question Template:**
```
Love this question! I'll make sure to cover this in depth soon. Stay tuned!
```

**Praise Template:**
```
This made my day! Thank you for the kind words and encouragement.
```

Edit at: `~/.openclaw/workspace/.cache/youtube-comment-monitor.py`

## Logs to Monitor

Daily logs automatically created:
```
~/.openclaw/workspace/.cache/logs/youtube-comment-monitor-YYYYMMDD.log
```

### See Today's Activity
```bash
tail -f ~/.openclaw/workspace/.cache/logs/youtube-comment-monitor-20260418.log
```

### Live Stream
```bash
log stream --predicate 'eventMessage contains[cd] "youtube"' --level debug
```

## Key Metrics

Track in reports:
- **Total Comments Processed** - All comments seen
- **Auto-Responses Sent** - Questions + Praise responses
- **Flagged for Review** - Sales inquiries needing manual attention
- **By Category** - Breakdown of Questions, Praise, Spam, Sales

## Common Tasks

### Find All Sales Inquiries
```bash
jq 'select(.category == "sales")' ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

### Count Auto-Responses
```bash
jq 'select(.response_status == "auto_responded") | .comment_id' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l
```

### Export CSV
```bash
jq -r '[.timestamp, .commenter, .category, .response_status] | @csv' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl > comments.csv
```

### Find Spam
```bash
jq 'select(.category == "spam")' ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

### Last 10 Comments
```bash
tail -10 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .
```

## Customization

### Change Response
Edit `RESPONSE_TEMPLATES` in:
```
~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

### Change Run Interval
Edit `StartInterval` in:
```
~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
```
Then restart LaunchAgent.

### Add Keywords
Edit `CATEGORY_PATTERNS` in:
```
~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

## Troubleshooting

**Not running?**
```bash
launchctl list | grep youtube-comment-monitor
# Should show PID, if not:
launchctl load ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
```

**Old reports?**
```bash
# Force immediate run
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

**API errors?**
```bash
# Delete token and re-auth
rm ~/.openclaw/workspace/.cache/youtube-token.json
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
# Follow browser auth flow
```

**Too many comments?**
```bash
# Archive old comments
mv ~/.openclaw/workspace/.cache/youtube-comments.jsonl \
   ~/.openclaw/workspace/.cache/youtube-comments.jsonl.archive
```

---

**Quick Links:**
- Full Setup: `YOUTUBE-COMMENT-MONITOR-SETUP.md`
- Monitor Script: `~/.openclaw/workspace/.cache/youtube-comment-monitor.py`
- Current Report: `~/.openclaw/workspace/.cache/youtube-comments-report-current.txt`
