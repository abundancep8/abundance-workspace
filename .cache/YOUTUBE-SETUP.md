# YouTube Comment Monitor Setup

## Overview
Monitors the Concessa Obvius YouTube channel for new comments every 30 minutes. Automatically categorizes and responds to questions/praise, flags sales inquiries for review, and logs all activity.

## Prerequisites

### 1. Install Dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Get YouTube API Credentials

#### Option A: API Key (Read-Only)
Easiest for just fetching comments.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **YouTube Data API v3**
4. Go to Credentials → Create API Key
5. Copy the key to `youtube-monitor-config.json` under `api_key`

#### Option B: OAuth 2.0 (Read + Write)
Required if you want auto-replies posted to YouTube.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **YouTube Data API v3**
4. Go to Credentials → Create OAuth 2.0 Client ID (select "Desktop application")
5. Download JSON credentials file
6. Set `YOUTUBE_CREDENTIALS_FILE` environment variable or update config file

#### Option C: Service Account (Headless Automation)
For running unattended on a server.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Create a Service Account
5. Generate and download JSON key
6. Share the YouTube channel access with the service account email
7. Set path in `youtube-monitor-config.json` under `credentials_file`

### 3. Get Channel ID

Visit the YouTube channel and look in the URL:
- URL: `https://www.youtube.com/c/ConcessaObvius`
- Or use: `youtube-api.py` script to auto-lookup

```bash
python3 youtube-api.py
```

### 4. Update Configuration

Edit `.cache/youtube-monitor-config.json`:

```json
{
  "channel_name": "Concessa Obvius",
  "channel_id": "UCxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "api_key": "YOUR_API_KEY_HERE",
  "auto_respond_enabled": true,
  "response_templates": {
    "question": "Your response here...",
    "praise": "Your response here..."
  }
}
```

## Usage

### Manual Run
```bash
python3 .cache/youtube-monitor.py
```

### Cron Job (Every 30 Minutes)

Add to crontab:
```bash
crontab -e
```

Add this line:
```cron
*/30 * * * * cd /Users/abundance/.openclaw/workspace && /usr/bin/python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1
```

### Via OpenClaw Scheduler
The cron trigger `cron:114e5c6d-ac8b-47ca-a695-79ac31b5c076` will run this automatically.

## Output

### Logs
- **Comments**: `.cache/youtube-comments.jsonl` (one JSON object per line)
- **Stats**: `.cache/youtube-monitor-stats.jsonl` (run stats)
- **State**: `.cache/youtube-monitor-state.json` (processed IDs, last checked)

### Example Comment Entry
```json
{
  "timestamp": "2026-04-16T07:00:00",
  "comment_id": "abc123",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "question",
  "response_status": "auto_responded"
}
```

## Categories

| Category | Examples | Action |
|----------|----------|--------|
| **Question** | "How do I...", "What is...", "cost?", "timeline?" | ✅ Auto-respond |
| **Praise** | "Amazing!", "Inspiring", "Love this" | ✅ Auto-respond |
| **Spam** | "Crypto", "MLM", "Click link" | 🚫 Skip |
| **Sales** | "Partnership", "Collaboration", "Sponsorship" | 🚩 Flag for review |
| **Other** | Everything else | 📝 Log only |

## Customization

### Custom Response Templates

Edit `response_templates` in `youtube-monitor-config.json`:

```json
"response_templates": {
  "question": "Thanks for asking! We have a guide here: [LINK]\n\nLet us know if you need more help!",
  "praise": "You're awesome! 🙌 Thanks for the support!"
}
```

### Adjust Category Keywords

Edit `CATEGORY_PATTERNS` in `youtube-monitor.py` to add/modify regex patterns.

### Change Check Interval

Modify cron schedule in `/etc/crontab` or OpenClaw config.

## Troubleshooting

### "API key invalid"
- Verify API key in config
- Check API is enabled in Google Cloud Console
- Ensure YouTube Data API v3 is enabled (not v2)

### "Channel not found"
- Double-check channel ID
- Verify channel exists and is public
- Try running `youtube-api.py` to auto-lookup

### "Permission denied for posting replies"
- Using API key? Switch to OAuth 2.0 or Service Account credentials
- Check service account has channel access
- Verify YouTube Data API scopes include `youtube.force-ssl`

### No comments fetched
- Check if channel has recent videos
- Verify comments are enabled on the videos
- Check last_checked timestamp in state file

## Monitoring

### View Recent Report
```bash
tail -20 .cache/youtube-monitor-stats.jsonl
```

### View Flagged Comments
```bash
grep '"sales"' .cache/youtube-comments.jsonl | jq .
```

### View Auto-Responses Sent
```bash
grep '"auto_responded"' .cache/youtube-comments.jsonl | wc -l
```

## Security Notes

⚠️ **Never commit API keys or credentials to version control**

- Use environment variables: `YOUTUBE_API_KEY`, `YOUTUBE_CREDENTIALS_FILE`
- Keep credentials file in `.cache/` (excluded from git)
- Rotate credentials regularly
- Use service accounts for production automation

## Next Steps

1. ✅ Get API credentials
2. ✅ Update config with channel ID & API key
3. ✅ Test manually: `python3 .cache/youtube-monitor.py`
4. ✅ Set up cron job
5. ✅ Monitor logs and adjust response templates
6. ✅ Set up alerts for "flagged for review" comments

---

**Questions?** Check the logs in `.cache/` or enable debug mode by adding `--debug` flag.
