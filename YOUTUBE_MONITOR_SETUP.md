# YouTube Comment Monitor Setup

## What This Does

Monitors your Concessa Obvius YouTube channel every 30 minutes to:

- **Categorize comments** into: Questions, Praise, Spam, Sales
- **Auto-respond** to Questions & Praise with template responses  
- **Flag Sales inquiries** for manual review
- **Log all activity** to `.cache/youtube-comments.jsonl` with timestamp, author, category, response status
- **Generate reports** with stats (total processed, auto-responses sent, flagged for review)

## Setup Steps

### 1. **Get Your YouTube Channel ID**

Visit your channel:
- URL format: `https://www.youtube.com/channel/YOUR_CHANNEL_ID`
- Or in YouTube Studio → Settings → Basic Info → Channel ID

### 2. **Set Up YouTube API Credentials**

This requires OAuth2 authentication:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **YouTube Data API v3**
4. Create OAuth 2.0 credentials (Desktop app / "OAuth client ID")
5. Download the credentials JSON file
6. Place it in your workspace root as `youtube-credentials.json`

### 3. **Install Dependencies**

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 4. **Configure the Monitor**

Edit `.cache/youtube-monitor-config.json`:

```json
{
  "channel": {
    "name": "Concessa Obvius",
    "id": "YOUR_CHANNEL_ID_HERE"
  }
}
```

### 5. **Test the Monitor**

```bash
# Dry-run mode (no API calls)
python3 .cache/youtube-monitor.py --channel-id YOUR_CHANNEL_ID --dry-run

# Test with API (will prompt for OAuth on first run)
python3 .cache/youtube-monitor.py --channel-id YOUR_CHANNEL_ID

# Enable auto-replies (will compose replies but not post until verified)
python3 .cache/youtube-monitor.py --channel-id YOUR_CHANNEL_ID --auto-reply
```

### 6. **Set Up Cron Job (Every 30 Minutes)**

**Option A: OpenClaw Cron (Recommended)**

This job is already configured in your cron scheduler. It runs every 30 minutes.

**Option B: System Cron**

```bash
# Edit crontab
crontab -e

# Add this line (runs every 30 minutes)
*/30 * * * * cd /Users/abundance/.openclaw/workspace && python3 .cache/youtube-monitor.py --channel-id YOUR_CHANNEL_ID --auto-reply >> .cache/youtube-monitor.log 2>&1
```

## Configuration

### Category Keywords

You can customize what counts as a question, praise, spam, or sales inquiry in `youtube-monitor-config.json`:

```json
{
  "categories": {
    "questions": {
      "keywords": ["how do i", "how to", "tools", "cost", "price", ...]
    }
  }
}
```

### Auto-Response Templates

Edit the templates in `youtube-monitor.py` or config file:

```python
TEMPLATES = {
    "questions": "Your custom response template...",
    "praise": "Your appreciation message..."
}
```

## Output & Logging

### Live Report (after each run)

```
============================================================
📈 YOUTUBE COMMENT MONITOR REPORT
============================================================
Total comments processed:     23
Auto-responses sent:          8
Flagged for review:           2

Breakdown by category:
  • questions: 8
  • praise: 10
  • spam: 3
  • sales: 2
============================================================
```

### Comment Log

All comments are saved to `.cache/youtube-comments.jsonl` (one JSON per line):

```json
{
  "logged_at": "2026-04-17T01:15:00.123456",
  "comment_id": "Ugw...",
  "video_id": "dQw4w9WgXcQ",
  "timestamp": "2026-04-17T00:45:30Z",
  "author": "John Doe",
  "text": "How do I get started with this?",
  "category": "questions",
  "response_status": "auto_replied",
  "likes": 5
}
```

## Troubleshooting

### "YouTube API libraries not installed"

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### "Missing youtube-credentials.json"

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials (Desktop app)
3. Download JSON and save as `youtube-credentials.json` in workspace root

### "Channel not found"

- Verify your `YOUTUBE_CHANNEL_ID` is correct
- Channel must be public or you must be the owner
- Check YouTube Studio → Settings → Basic Info → Channel ID

### Auto-replies not posting

The script currently prepares replies but doesn't post without explicit verification. To enable auto-posting:

Edit `.cache/youtube-monitor.py` and uncomment the reply posting code (search for "POST REPLY HERE").

## Security Notes

- **credentials.json** contains OAuth tokens — don't commit to git
- **youtube-token.json** is generated automatically — also keep private
- Consider using `.gitignore` to exclude these files

## Monitoring This Cron Job

Check recent runs:

```bash
# View recent logs
tail -f .cache/youtube-monitor.log

# Check if comments are being logged
tail -20 .cache/youtube-comments.jsonl
```

## Next Steps

1. ✅ Set `YOUTUBE_CHANNEL_ID` environment variable
2. ✅ Download and place `youtube-credentials.json`
3. ✅ Run test: `python3 .cache/youtube-monitor.py --channel-id YOUR_ID --dry-run`
4. ✅ Verify reports in `.cache/youtube-comments.jsonl`
5. ✅ Enable auto-replies when ready

---

Questions? Check the script comments or review the Google YouTube Data API docs: https://developers.google.com/youtube/v3
