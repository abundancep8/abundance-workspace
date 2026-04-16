# YouTube Comment Monitor - Complete Setup

**Cron Job ID:** `114e5c6d-ac8b-47ca-a695-79ac31b5c076`  
**Channel:** Concessa Obvius  
**Interval:** Every 30 minutes  
**Status:** Ready to activate

## System Overview

Monitors YouTube comments on Concessa Obvius channel, auto-responds to questions and praise, flags sales inquiries, and logs everything to `.cache/youtube-comments.jsonl`.

### Comment Categories

| Category | Pattern | Action |
|----------|---------|--------|
| **Questions** | How to, what, where, tools, cost, timeline | Auto-respond with template |
| **Praise** | Amazing, inspiring, love, thanks, great | Auto-respond with appreciation |
| **Spam** | Crypto, MLM, suspicious links | Log only (no response) |
| **Sales** | Partnership, collaboration, sponsorship | Flag for human review |

## Files

- **Script:** `.cache/youtube-comment-monitor.py` (main logic)
- **Wrapper:** `.cache/youtube-monitor-cron.sh` (cron entry point)
- **Log:** `.cache/youtube-comments.jsonl` (comment database)
- **State:** `.cache/youtube-monitor-state.json` (last-processed tracking)
- **Cron logs:** `.cache/cron-logs/youtube-monitor-*.log` (run history)
- **Setup guide:** `.cache/YOUTUBE-SETUP.md` (detailed instructions)

## Setup (One-Time)

### Step 1: Get YouTube API Credentials

1. Go to https://console.cloud.google.com/
2. Create project or select existing
3. Enable "YouTube Data API v3"
4. Create Service Account with Editor role
5. Generate JSON key file
6. Save to: `~/.openclaw/workspace/.secrets/youtube-credentials.json`

Create the `.secrets` directory first:
```bash
mkdir -p ~/.openclaw/workspace/.secrets
chmod 700 ~/.openclaw/workspace/.secrets
```

### Step 2: Install Python Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 3: Test

```bash
python ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

Expected output:
```
[2026-04-15...] Starting YouTube Comment Monitor
Monitoring channel: Concessa Obvius (UC...)
No new comments found.
============================================================
YOUTUBE COMMENT MONITOR REPORT
============================================================
...
```

## Operations

### View Recent Comments

```bash
# Raw JSONL
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Pretty-printed
jq . ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Recent 10 comments
tail -10 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .

# Filter by category (e.g., sales)
grep '"category": "sales"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .
```

### View Cron Runs

```bash
# List all runs
ls -lh ~/.openclaw/workspace/.cache/cron-logs/

# Watch latest run
tail -f ~/.openclaw/workspace/.cache/cron-logs/youtube-monitor-*.log

# Last 50 lines
tail -50 ~/.openclaw/workspace/.cache/cron-logs/$(ls -t ~/.openclaw/workspace/.cache/cron-logs/ | head -1)
```

### Check Monitor Status

```bash
# See when last run was
ls -lt ~/.openclaw/workspace/.cache/cron-logs/ | head -3

# Check how many comments logged
wc -l ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Get stats
echo "Total comments: $(wc -l < ~/.openclaw/workspace/.cache/youtube-comments.jsonl)"
echo "Flagged for review: $(grep '"category": "sales"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l)"
echo "Auto-responses sent: $(grep '"response_status": "sent"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l)"
```

## Customization

Edit `.cache/youtube-comment-monitor.py` to modify:

### Response Templates

Find `TEMPLATES` dict:
```python
TEMPLATES = {
    "questions": [
        # Add your custom question responses here
    ],
    "praise": [
        # Add your custom praise responses here
    ]
}
```

### Category Patterns

Find `categorize_comment()` function and update regex patterns:
- `spam_patterns` - Add more spam indicators
- `sales_patterns` - Add partnership keywords
- `question_patterns` - Add question triggers
- `praise_patterns` - Add praise keywords

### Channel/API Settings

At top of file:
```python
CHANNEL_NAME = "Concessa Obvius"  # Change to monitor different channel
CREDENTIALS_FILE = Path(...)  # Change credential path if needed
```

## Troubleshooting

### "Credentials not found"
- Verify file exists: `ls ~/.openclaw/workspace/.secrets/youtube-credentials.json`
- Check file is valid JSON: `jq . ~/.openclaw/workspace/.secrets/youtube-credentials.json`

### "Channel not found"
- Verify exact channel name (case-sensitive display name)
- Test: `echo "Concessa Obvius" | grep -i "concessa"` should match

### No comments fetched
- Channel may have comments disabled
- API quota may be exceeded (check Cloud Console)
- Channel may have no recent uploads

### Cron not running
- Verify cron job is registered: `openclaw cron list | grep 114e5c6d`
- Check OpenClaw daemon: `openclaw gateway status`
- View logs: `openclaw cron logs 114e5c6d-ac8b-47ca-a695-79ac31b5c076`

## Reports

Every 30 minutes, monitor prints report to cron log:

```
============================================================
YOUTUBE COMMENT MONITOR REPORT
============================================================
Timestamp: 2026-04-15 16:00:00 PDT
Channel: Concessa Obvius
Total comments processed: 3
Auto-responses sent: 2
Flagged for review: 1
============================================================
```

Access reports:
```bash
# Find all reports in cron logs
grep -h "YOUTUBE COMMENT MONITOR REPORT" ~/.openclaw/workspace/.cache/cron-logs/*.log

# Get latest report
tail ~/.openclaw/workspace/.cache/cron-logs/$(ls -t ~/.openclaw/workspace/.cache/cron-logs/ | head -1) | grep -A 10 "REPORT"
```

## Monitoring Dashboard

To create a live dashboard, periodically check:

```bash
#!/bin/bash
# watch-youtube-monitor.sh

watch -n 60 'echo "=== Latest 5 Comments ==="; tail -5 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq -c "{author: .commenter, category: .category, text: .text[0:50]}"; echo ""; echo "=== Stats ==="; echo "Total: $(wc -l < ~/.openclaw/workspace/.cache/youtube-comments.jsonl)"; echo "Flagged: $(grep "\"category\": \"sales\"" ~/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l)"'
```

## Notes

- Monitor runs **every 30 minutes** automatically
- Auto-responses currently **logged only** (not yet posted to YouTube)
- To implement actual YouTube replies, update `youtube.commentThreads().insert()` call
- All processed comment IDs are tracked to prevent duplicates
- JSONL format allows easy streaming and analysis

## Next Actions

1. ✅ Script created and configured
2. ⏳ Get YouTube API credentials (see Step 1 above)
3. ⏳ Install Python dependencies (see Step 2)
4. ⏳ Test manually (see Step 3)
5. ✅ Cron job registered and will start running in 30 minutes
6. ⏳ Implement actual YouTube reply posting (if desired)

---

Once credentials are in place, the monitor will run automatically every 30 minutes. Check logs regularly for flagged sales inquiries and monitor statistics.
