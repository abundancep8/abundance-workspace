# YouTube Monitor - Quick Reference

## Quick Commands

### View Comments
```bash
# All comments
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .

# Last 5 comments
tail -5 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .

# Sales flagged for review
grep '"sales"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .

# By commenter
grep '"comment_author": "Name"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .
```

### Stats
```bash
# Total processed
wc -l ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Breakdown by category
echo "=== Comment Breakdown ===" && \
grep '"category"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | \
cut -d: -f2 | cut -d'"' -f2 | sort | uniq -c

# Auto-responses sent
grep '"sent"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l

# Flagged for review
grep '"flagged_for_review"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l
```

### Monitor Status
```bash
# Last run time
ls -lt ~/.openclaw/workspace/.cache/cron-logs/ | head -1

# Current run status
tail -20 ~/.openclaw/workspace/.cache/cron-logs/$(ls -t ~/.openclaw/workspace/.cache/cron-logs/ | head -1)

# All runs (past 24h)
ls -l ~/.openclaw/workspace/.cache/cron-logs/ | grep $(date +%Y-%m-%d)
```

### Configuration
```bash
# Edit monitor script
nano ~/.openclaw/workspace/.cache/youtube-comment-monitor.py

# Edit response templates (line ~40)
# - TEMPLATES["questions"]
# - TEMPLATES["praise"]

# Edit categorization (line ~140)
# - categorize_comment() function
```

## One-Time Setup Checklist

- [ ] Create YouTube API Service Account
- [ ] Download JSON credentials
- [ ] Place at `~/.openclaw/workspace/.secrets/youtube-credentials.json`
- [ ] Run: `pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client`
- [ ] Test: `python ~/.openclaw/workspace/.cache/youtube-comment-monitor.py`

## Typical Workflow

### Every Morning
```bash
# Check overnight activity
tail -20 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq -c '{author: .commenter, category: .category, text: .text[0:50]}'
```

### When Flagged Comments Arrive
```bash
# See what needs review
grep '"sales"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq '{commenter, text}'

# Respond manually or through YouTube
```

### Weekly Report
```bash
# Stats for past 7 days
echo "=== Weekly Stats ===" && \
echo "Total: $(wc -l < ~/.openclaw/workspace/.cache/youtube-comments.jsonl)" && \
echo "This week: $(find ~/.openclaw/workspace/.cache/cron-logs -mtime -7 | wc -l) runs" && \
echo "Flagged: $(grep '"sales"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l)" && \
echo "Auto-responses: $(grep '"sent"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l)"
```

## Common Issues & Fixes

**Monitor not running?**
```bash
# Check cron
openclaw cron list | grep youtube

# Check service
openclaw gateway status

# Manual run to debug
python ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

**No credentials error?**
```bash
# Verify file exists
ls ~/.openclaw/workspace/.secrets/youtube-credentials.json

# Verify is valid JSON
jq . ~/.openclaw/workspace/.secrets/youtube-credentials.json
```

**Need to reset?**
```bash
# Clear processed IDs (start fresh)
echo '{"last_processed": null, "processed_ids": []}' > ~/.openclaw/workspace/.cache/youtube-monitor-state.json

# Clear logs (keep JSONL data)
rm ~/.openclaw/workspace/.cache/cron-logs/youtube-monitor-*.log
```

## Data Format

Each line in `youtube-comments.jsonl` is:
```json
{
  "timestamp": "2026-04-15T23:00:00.000000",
  "comment_id": "Ugx...",
  "video_id": "a...",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "questions",
  "response_status": "sent",
  "likes": 0
}
```

- `timestamp` - UTC when logged
- `comment_id` - YouTube comment ID (unique)
- `video_id` - Which video the comment is on
- `commenter` - Display name
- `text` - Full comment text
- `category` - questions|praise|spam|sales|neutral
- `response_status` - none|sent|flagged_for_review
- `likes` - Like count on comment

## Full Documentation

See `YOUTUBE-MONITOR.md` for complete reference.
