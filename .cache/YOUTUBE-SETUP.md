# YouTube Comment Monitor Setup

## Status
🔴 **Not Configured** — Waiting for YouTube API credentials

## What's Ready
✅ Monitoring script created: `.cache/youtube-monitor.py`
✅ Comment logging configured: `.cache/youtube-comments.jsonl`
✅ Categorization logic implemented (Questions, Praise, Spam, Sales)
✅ Auto-response templates prepared

## Next Steps

### 1. Install Python Dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Create Google Cloud Project
1. Go to https://console.cloud.google.com
2. Create a new project (name it `youtube-monitor` or similar)
3. Enable **YouTube Data API v3**

### 3. Create OAuth 2.0 Credentials
1. Go to **Credentials** in Google Cloud Console
2. Click **Create Credentials** → **OAuth client ID**
3. Choose **Desktop application**
4. Download JSON and save as:
   ```
   .cache/youtube-credentials.json
   ```

### 4. Run the Monitor
```bash
python3 .cache/youtube-monitor.py
```

First run will prompt you to authorize in your browser. After that, it will cache the token.

## How It Works

**Categorization:**
- **Questions** (auto-respond): "how to start", "tools", "cost", "timeline"
- **Praise** (auto-respond): "amazing", "inspiring", "love", "excellent"
- **Spam** (skip): "crypto", "bitcoin", "mlm", "forex"
- **Sales** (flag for review): "partnership", "collaboration", "sponsor"

**Output:**
- `.cache/youtube-comments.jsonl` — One comment per line (JSON)
- Report printed to console

**Schedule:**
This runs every 30 minutes via cron. Each run will only see new comments since the last run.

## What Gets Logged
```json
{
  "timestamp": "2026-04-15T07:30:00.000Z",
  "commenter": "User Name",
  "text": "Full comment text",
  "category": "question|praise|spam|sales",
  "response_status": "auto_responded|flagged_for_review|pending",
  "videoId": "...",
  "commentId": "..."
}
```

## Customize Templates
Edit `TEMPLATES` dict in `youtube-monitor.py` to change auto-response messages.

---

**Next:** Set up Google Cloud credentials, then run `python3 .cache/youtube-monitor.py`
