# YouTube Comment Monitor - Quick Start

## Status ✅

The YouTube comment monitoring system is **ready to deploy**. Everything is configured:

- ✅ Dependencies installed (google-auth, YouTube API v3)
- ✅ Credentials set up (`.secrets/youtube-credentials.json`)
- ✅ Token saved (`.cache/youtube_token.json`)
- ✅ Monitor script ready (`.cron/youtube-comment-monitor.py`)
- ✅ Report generator ready (`.cron/youtube-report.py`)

## What It Does

**Every 30 minutes**, the monitor:

1. Fetches new comments from the Concessa Obvius YouTube channel
2. Categorizes each comment:
   - **Questions** (how-to, tools, cost, timeline) → Auto-responds
   - **Praise** (amazing, inspiring) → Auto-responds with gratitude
   - **Spam** (crypto, MLM, scams) → Logged and flagged
   - **Sales** (partnerships, collabs) → Flagged for manual review
3. Logs everything to `.cache/youtube-comments.jsonl`
4. Generates reports on demand

## How to Use

### Start the Monitor

```bash
# One-time test run
python3 .cron/youtube-comment-monitor.py

# Schedule with cron (every 30 minutes)
crontab -e
# Add:  */30 * * * * cd /Users/abundance/.openclaw/workspace && python3 .cron/youtube-comment-monitor.py >> .cache/youtube-monitor.log 2>&1
```

### View Reports

```bash
# Summary report
python3 .cron/youtube-report.py

# Tail recent activity
tail -20 .cache/youtube-comments.jsonl | jq .

# Find flagged comments
cat .cache/youtube-comments.jsonl | jq 'select(.response_status == "flagged")'

# Count by category
cat .cache/youtube-comments.jsonl | jq -s 'group_by(.category) | map({category: .[0].category, count: length})'
```

## Configuration

### Customize Auto-Responses

Edit `.cron/youtube-comment-monitor.py`:

```python
RESPONSE_TEMPLATES = {
    "questions": [
        "Your question response here...",
        "Alternative response...",
    ],
    "praise": [
        "Your thank-you response here...",
        "Alternative response...",
    ]
}
```

### Change Categorization Keywords

Edit the `categorize_comment()` function:

```python
def categorize_comment(text: str) -> CommentCategory:
    # Add/remove keywords for your needs
    sales_keywords = ["partnership", "your-keyword-here", ...]
    # ...
```

### Monitor Different Channel

Edit `youtube-comment-monitor.py`:

```python
CHANNEL_HANDLE = "ConcessaObvius"  # Change to your channel
```

## Logging

**All activity is logged to:** `.cache/youtube-comments.jsonl`

Each line contains:
```json
{
  "comment_id": "unique-id",
  "timestamp": "2026-04-17T19:30:00+00:00",
  "commenter": "User Name",
  "text": "Comment text...",
  "category": "questions|praise|spam|sales",
  "response_status": "sent|pending|flagged"
}
```

**Monitor logs:** `.cache/youtube-monitor.log`
- Stdout/stderr from each run
- Errors logged here

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Channel not found" | Verify `CHANNEL_HANDLE` in the script matches the channel |
| Token expired | Delete `.cache/youtube_token.json` and rerun; you'll be prompted to authorize |
| Replies not posting | Make sure you're logged in as the channel owner |
| No comments found | Channel may not have new comments or they may be disabled |
| Script hangs | Check network connection; add debug prints to trace |

## Next Steps

1. **Deploy to cron:** Add the crontab entry above
2. **Monitor logs:** Check `.cache/youtube-monitor.log` for any issues
3. **Review flagged:** Periodically run the report and review flagged comments
4. **Tweak templates:** Customize responses to match your voice
5. **Watch it work:** Comments will be categorized and logged automatically!

---

**Questions?** Check the detailed guides:
- `YOUTUBE_SETUP.md` - Full setup instructions
- `YOUTUBE_MONITORING.md` - Advanced configuration
