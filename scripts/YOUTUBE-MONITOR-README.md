# YouTube Comment Monitor

**Concessa Obvius Channel - Automated Comment Management**

Runs every 30 minutes to monitor, categorize, auto-respond, and log YouTube comments.

## Files

| File | Purpose |
|------|---------|
| `youtube-comment-monitor.py` | Main monitoring script |
| `youtube-monitor-cron.sh` | Cron wrapper (handles env vars) |
| `youtube-monitor-setup.md` | Detailed setup instructions |

## Quick Start

### 1. Install Dependencies
```bash
cd /Users/abundance/.openclaw/workspace
pip install google-auth-oauthlib google-api-python-client
```

### 2. Get Credentials
- YouTube API Key: https://console.cloud.google.com/
- Channel ID: Find in your YouTube channel URL

### 3. Set Environment
```bash
export YOUTUBE_API_KEY="your-key"
export YOUTUBE_CHANNEL_ID="UCxxxxxxxxxx"
```

Or create `.env` file in workspace root:
```
YOUTUBE_API_KEY=your-key
YOUTUBE_CHANNEL_ID=UCxxxxxxxxxx
```

### 4. Test Run
```bash
python scripts/youtube-comment-monitor.py
```

### 5. Schedule with Cron
```bash
# Edit crontab
crontab -e

# Add this line (runs every 30 minutes)
*/30 * * * * /Users/abundance/.openclaw/workspace/scripts/youtube-monitor-cron.sh
```

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│ Every 30 minutes: Monitor runs                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│ 1. FETCH: Get new comments from channel videos           │
│    └─> Uses YouTube Data API v3                         │
│                                                           │
│ 2. CATEGORIZE: Analyze each comment                      │
│    ├─ Category 1: Questions (how, start, cost, etc.)    │
│    ├─ Category 2: Praise (amazing, inspiring, etc.)     │
│    ├─ Category 3: Spam (crypto, MLM, forex, etc.)       │
│    └─ Category 4: Sales (partnership, collab, etc.)     │
│                                                           │
│ 3. AUTO-RESPOND:                                         │
│    ├─ Q's → "Thanks for the question! [template]"       │
│    ├─ Praise → "Thank you so much! 💙"                  │
│    └─ Sales/Spam → Log only (no reply)                  │
│                                                           │
│ 4. LOG: Write to youtube-comments.jsonl                  │
│    └─ timestamp, commenter, text, category, response    │
│                                                           │
│ 5. FLAG: Sales/partnerships go to youtube-review.txt    │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Output Files

### `.cache/youtube-comments.jsonl`
One JSON object per line. Each entry:
```json
{
  "timestamp": "2026-04-20T06:00:00.123456",
  "comment_id": "UgwJ_abcdef123",
  "video_id": "dQw4w9WgXcQ",
  "author": "John Doe",
  "text": "This is amazing! How did you get started?",
  "published_at": "2026-04-20T05:30:00Z",
  "category": 1,
  "category_name": "Questions",
  "response_sent": true,
  "reply_count": 3
}
```

### `.cache/youtube-review.txt`
Manual review queue (human-readable):
```
--- 2026-04-20T06:00:00 ---
Author: Marketing Agency XYZ
Video: dQw4w9WgXcQ
Category: Sales/Partnerships
Text: Hey, we'd love to partner with you. Check out our portfolio...
Comment ID: UgwJ_xyz789

--- 2026-04-20T06:30:00 ---
...
```

### `.cache/youtube-monitor.json`
Internal state (tracks processed comments):
```json
{
  "last_checked": "2026-04-20T06:00:00.123456",
  "processed_comments": [
    "UgwJ_abcdef123",
    "UgwJ_xyz789",
    "..."
  ]
}
```

### `.cache/monitor.log`
Cron execution log (created by `youtube-monitor-cron.sh`):
```
==========================================
Monitor run: Sun Apr 20 06:00:00 PDT 2026
...INFO - Found 5 total comments
...INFO - Processed: 3, Auto-responses: 2, Flagged: 1
==========================================

==========================================
Monitor run: Sun Apr 20 06:30:00 PDT 2026
...
```

## Statistics

After each run, see:
- **Total Comments Processed** - New comments found
- **Auto-Responses Sent** - Q's and praise auto-replied
- **Flagged for Review** - Sales/partnerships
- **Spam Filtered** - Crypto/MLM blocked

Example output:
```
============================================================
YOUTUBE COMMENT MONITOR REPORT
============================================================
Timestamp: 2026-04-20T06:00:00.123456
Channel: UCyourChannelIdHere

Comments Processed: 7
  - Questions: 3
  - Praise: 2
  - Spam (filtered): 1
  - Sales/Partnerships: 1
  - Uncategorized: 0

Auto-Responses Sent: 5
Flagged for Review: 1
Log File: .cache/youtube-comments.jsonl
Review File: .cache/youtube-review.txt
============================================================
```

## Customization

### Edit Response Templates
In `youtube-comment-monitor.py`, find `CATEGORIES` dict:

```python
1: {  # Questions
    "template": "Thanks for the question! [Your custom reply]"
},
2: {  # Praise
    "template": "Thank you so much! [Your custom reply]"
}
```

### Add/Change Keywords
Modify the `"keywords"` lists in `CATEGORIES`:

```python
1: {
    "keywords": ["how", "where", "cost", "timeline", "your keywords here"],
    ...
}
```

### Disable Auto-Reply
Comment out the `auto_respond()` call if you only want logging:
```python
# response_sent = auto_respond(service, comment_id, comment["text"], category)
response_sent = False
```

## Monitoring

### View Recent Comments
```bash
tail -5 .cache/youtube-comments.jsonl | jq .
```

### View Flagged Comments (Pending Review)
```bash
cat .cache/youtube-review.txt
```

### Check Cron Log
```bash
tail -50 .cache/monitor.log
```

### Count by Category
```bash
jq -r '.category_name' .cache/youtube-comments.jsonl | sort | uniq -c
```

### Find Responded Comments
```bash
jq 'select(.response_sent==true)' .cache/youtube-comments.jsonl
```

## Troubleshooting

### Script doesn't run from cron
1. Check cron log: `tail .cache/monitor.log`
2. Verify API key is accessible to cron user
3. Run manually: `bash scripts/youtube-monitor-cron.sh`

### "Permission denied" when replying
- API Key is read-only (doesn't support replies)
- Switch to OAuth 2.0 for write permissions
- Or disable auto-reply (comment monitoring only)

### Rate limited (429 error)
- YouTube API quota exhausted
- Wait 24 hours or upgrade quota in Google Cloud Console
- Script will retry on next run

### No comments found
- Channel has no new comments in monitoring window
- Verify `YOUTUBE_CHANNEL_ID` is correct and public

## API Limits

- **10,000 requests/day** default quota (usually enough)
- Each comment fetch = ~1-2 requests
- Each auto-reply = ~1 request
- Scale to 500+ channels/day with quotas upgrade

## Security

- **API Key**: Keep secret, don't commit to git
- **Use `.env`** file (add to `.gitignore`)
- **Log files**: May contain user comments (keep private)
- **Review file**: Human reads before responding

## Next Steps

1. ✅ Install dependencies
2. ✅ Get API credentials
3. ✅ Test manually
4. ✅ Set up cron job
5. ✅ Monitor `.cache/youtube-review.txt` daily
6. ✅ Customize templates as needed
