# YouTube Comment Monitor Setup

## Overview
This monitors the Concessa Obvius YouTube channel for new comments, categorizes them, and sends auto-responses.

## Prerequisites

### 1. Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project: "YouTube Comment Monitor"
3. Enable the YouTube Data API v3
4. Create an API Key:
   - APIs & Services → Credentials
   - Create Credentials → API Key
   - Copy the API key

### 2. Set API Key

```bash
export YOUTUBE_API_KEY="your-api-key-here"
```

Or add to `~/.zshenv`:
```bash
export YOUTUBE_API_KEY="your-api-key-here"
```

### 3. Install Dependencies

```bash
python3 -m pip install python-dateutil
```

## Usage

### Manual Run
```bash
python3 .cache/youtube_monitor.py
```

### Cron Setup (Every 30 minutes)

Edit crontab:
```bash
crontab -e
```

Add:
```
*/30 * * * * cd /Users/abundance/.openclaw/workspace && YOUTUBE_API_KEY="your-api-key" python3 .cache/youtube_monitor.py >> .cache/youtube-monitor.log 2>&1
```

Or using OpenClaw cron:
```bash
openclaw cron add --schedule "*/30 * * * *" --command "cd /Users/abundance/.openclaw/workspace && python3 .cache/youtube_monitor.py"
```

## Output Files

- `.cache/youtube-comments.jsonl` - All comments (newline-delimited JSON)
- `.cache/youtube-monitor-stats.json` - Latest stats
- `.cache/youtube-last-check.json` - Last check timestamp
- `.cache/youtube-monitor.log` - Cron logs (if using crontab)

## Comment Categories

### 1. Questions
Patterns: "how do I", "what is", "cost", "tools", "timeline", "?"

**Auto-Response:** "Thank you for your question! We appreciate your interest. Here are some resources..."

### 2. Praise
Patterns: "amazing", "inspiring", "love this", "thank you", "❤️", "👏"

**Auto-Response:** "Thank you so much for the kind words! We're thrilled you found this valuable..."

### 3. Spam
Patterns: "crypto", "bitcoin", "MLM", "forex", "get rich fast"

**Action:** Ignored (no response)

### 4. Sales
Patterns: "partnership", "collaboration", "sponsor", "business opportunity"

**Action:** Flagged for manual review (you'll see in stats)

## Important Notes

⚠️ **OAuth Limitation**: Posting replies requires YouTube Data API OAuth 2.0 authentication. The current script detects eligible comments but needs manual configuration for auto-replies. See "Advanced Setup" below.

### What This Can Do (With API Key Only)
- ✅ Fetch comments from channel videos
- ✅ Categorize comments accurately
- ✅ Log all comments with metadata
- ✅ Flag sales inquiries for review
- ✅ Generate reports

### What Needs OAuth (Optional)
- 🔄 Auto-reply to comments directly
- 🔄 Like/pin comments

## Advanced Setup: Enable Auto-Replies

To enable auto-replies, you need OAuth 2.0:

1. Go back to Google Cloud Console
2. APIs & Services → Credentials → Create OAuth 2.0 Client ID
3. Set Redirect URI: `http://localhost:8080/callback`
4. Download the client secret JSON
5. Run the script once to authorize:
   ```bash
   python3 .cache/youtube_monitor.py --auth
   ```
6. Follow the browser prompt to grant permissions

This will save a refresh token for automatic authorization in future runs.

## Troubleshooting

### "Could not find channel"
- Check if the channel username is correct
- The script tries to auto-lookup; if it fails, get the channel ID from YouTube:
  1. Go to channel
  2. Click "About" tab
  3. Get the URL: `youtube.com/@ConcessaObvious` → ID is in the URL
  4. Set: `export YOUTUBE_CHANNEL_ID="UC..."`

### "API quota exceeded"
- YouTube API has quotas (10,000 units/day free tier)
- Each comment fetch uses ~1-3 units
- Reduce frequency or upgrade API quota in Google Cloud Console

### No comments being processed
- Check that the cron job is running:
  ```bash
  tail -f .cache/youtube-monitor.log
  ```
- Verify API key is set:
  ```bash
  echo $YOUTUBE_API_KEY
  ```
- Check log file for errors

## Monitoring

View latest stats:
```bash
cat .cache/youtube-monitor-stats.json
```

View all logged comments:
```bash
tail -20 .cache/youtube-comments.jsonl | jq .
```

View just flagged reviews:
```bash
grep '"response_status": "flagged_review"' .cache/youtube-comments.jsonl | jq .
```

## Reports

Get today's summary:
```bash
python3 << 'EOF'
import json
from pathlib import Path
from datetime import datetime

log_file = Path(".cache/youtube-comments.jsonl")
today = datetime.now().date()

if log_file.exists():
    comments = {}
    with open(log_file) as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                ts = datetime.fromisoformat(data["timestamp"]).date()
                if ts == today:
                    cat = data.get("category", "other")
                    comments[cat] = comments.get(cat, 0) + 1
    
    print(f"Comments Today ({today}):")
    for cat, count in sorted(comments.items()):
        print(f"  {cat}: {count}")
EOF
```

---

**Questions?** Check the logs or run: `python3 .cache/youtube_monitor.py --debug`
