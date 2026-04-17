# YouTube Comment Monitor - Quick Start

## What You Have

- **youtube-monitor.py** — Main monitoring script
- **youtube-monitor.sh** — Cron wrapper
- **youtube-stats.py** — View stats & recent activity
- **YOUTUBE_SETUP.md** — Detailed configuration guide

## 5-Minute Setup

### 1. Install dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Get YouTube API credentials
1. Go to https://console.cloud.google.com
2. Create a project → Enable "YouTube Data API v3"
3. Create OAuth 2.0 Desktop credentials
4. Download as JSON
5. Save to: `~/.openclaw/youtube-credentials.json`

### 3. Find Concessa Obvius channel ID
- Visit the channel
- In URL: `youtube.com/@ConcessaObvius` → Look for the actual channel ID
- Or use: https://www.youtube.com/c/[name]/about → Check the "Share channel" option

### 4. Update the script
```bash
# Edit youtube-monitor.py, line 19:
CHANNEL_ID = "UCxxxxxxxxxxxxx"  # Your actual channel ID
```

### 5. Test it
```bash
python3 youtube-monitor.py
```

You should see a report with any new comments found.

### 6. Add to cron (every 30 minutes)
```bash
crontab -e
```

Add this line:
```
0,30 * * * * cd /Users/abundance/.openclaw/workspace && bash youtube-monitor.sh
```

## Using It

### View real-time stats
```bash
python3 youtube-stats.py
```

### Check recent logs
```bash
tail -f .cache/logs/monitor_*.log
```

### View all comments as JSON
```bash
cat .cache/youtube-comments.jsonl | jq '.'
```

### Find comments by category
```bash
cat .cache/youtube-comments.jsonl | jq 'select(.category=="question")'
```

## What It Does

**Every 30 minutes:**
1. Fetches new comments from your channel
2. Categorizes them: Question / Praise / Spam / Sales
3. Auto-responds to Questions & Praise with templates
4. Flags Sales inquiries for your review
5. Logs everything with timestamp & status
6. Reports: total processed, auto-responses sent, flagged items

**Categories:**
- 🤔 **Question** → "How do I...?" → Auto-replies with help
- 👏 **Praise** → "Amazing work!" → Auto-replies with thanks
- 🚨 **Spam** → Crypto, MLM, scams → Logs, no response
- 💼 **Sales** → Partnerships, sponsors → Flags for review

## Customize

Edit `youtube-monitor.py`:
- **Response templates** (line ~40): Change auto-reply text
- **Categorization patterns** (line ~50): Add/remove keywords
- **Channel ID** (line 19): Your channel

## Troubleshooting

**No comments found?**
- Verify channel ID
- Check that videos have comments
- Run: `python3 youtube-monitor.py` to test

**"Permission denied"?**
- First run needs browser auth
- Allow all permissions
- Token saved automatically

**Cron not running?**
- Check: `ls -la .cache/logs/`
- View error: `tail .cache/logs/errors.log`
- Run manually: `bash youtube-monitor.sh`

## Next Steps

See **YOUTUBE_SETUP.md** for advanced config, troubleshooting, and custom categorization rules.
