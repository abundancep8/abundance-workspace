# YouTube Comment Monitor Setup

Automated monitoring and response system for the Concessa Obvius YouTube channel.

## Overview

The monitor runs every 30 minutes and:
- Fetches new comments from recent videos
- Categorizes them: **Questions**, **Praise**, **Spam**, **Sales**
- Auto-responds to Questions and Praise
- Flags Sales inquiries for manual review
- Logs all activity to `.cache/youtube-comments.jsonl`

## Setup

### 1. Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing one)
3. Enable the **YouTube Data API v3**:
   - Go to **APIs & Services** → **Enable APIs and Services**
   - Search for "YouTube Data API v3"
   - Click **Enable**
4. Create OAuth 2.0 credentials:
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **OAuth client ID**
   - Choose **Desktop application**
   - Download the JSON file
5. Save it to: `~/.openclaw/workspace/.cache/youtube-credentials.json`

### 2. Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. First Run (Authenticate)

```bash
python scripts/youtube-monitor.py
```

This will:
- Open a browser to authenticate
- Save your token to `.cache/youtube-token.json`
- Run the first monitor cycle

### 4. Set Up Cron Job

The cron system will automatically run every 30 minutes. The script handles:
- Finding the Concessa Obvius channel
- Fetching recent comments
- Categorizing and responding
- Logging all activity

## Configuration

### Auto-Response Templates

Edit `scripts/youtube-monitor.py` → `RESPONSES` dict:

```python
RESPONSES = {
    'question': "Your custom response for questions...",
    'praise': "Your custom response for praise..."
}
```

### Categorization Rules

Adjust keyword matching in the `categorize_comment()` function:

```python
question_keywords = ['how', 'what', 'cost', 'timeline', ...]
praise_keywords = ['amazing', 'inspiring', 'love', ...]
spam_keywords = ['bitcoin', 'crypto', 'mlm', ...]
sales_keywords = ['partnership', 'collaboration', 'sponsor', ...]
```

## Monitoring

### View Logs

```bash
tail -f .cache/youtube-comments.jsonl | jq
```

### Current Session Report

Run manually to see today's stats:

```bash
python scripts/youtube-monitor.py
```

### Sample Log Entry

```json
{
  "timestamp": "2026-04-21T06:30:00.123456",
  "video_id": "abcd1234",
  "comment_id": "xyz789",
  "author": "John Doe",
  "text": "How do I get started?",
  "published": "2026-04-21T05:00:00Z",
  "category": "question",
  "response_status": "auto_sent",
  "response_id": "reply123"
}
```

## Status Codes

- `none` - No response sent (spam/other)
- `auto_sent` - Automated response posted successfully
- `failed` - Response attempt failed (network issue)
- `flagged` - Marked for manual review (sales inquiries)

## Troubleshooting

### "Credentials not found"
- Ensure `.cache/youtube-credentials.json` exists
- Get it from [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

### "Token expired"
- Delete `.cache/youtube-token.json`
- Run the script again to re-authenticate

### "Channel not found"
- Verify the channel name in `scripts/youtube-monitor.py` → `CHANNEL_NAME`
- Use exact channel name or try channel handle (e.g., @username)

### Rate limiting
- YouTube API has quotas (default 10,000 units/day)
- Each comment check uses ~2-3 units
- Monitor at most every 30 minutes to stay under quota

## Files

- `scripts/youtube-monitor.py` - Main monitoring script
- `.cache/youtube-comments.jsonl` - Log of all processed comments
- `.cache/youtube-token.json` - OAuth token (auto-generated, don't edit)
- `.cache/youtube-state.json` - Last check time and processed IDs (for deduplication)

---

**Last Updated:** 2026-04-21
**Channel:** Concessa Obvius
**Monitor Frequency:** Every 30 minutes (via cron)
