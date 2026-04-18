# YouTube Comment Monitor Setup

## Requirements

1. **Python Libraries**
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client anthropic
   ```

2. **YouTube API Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable YouTube Data API v3
   - Create OAuth 2.0 Desktop App credentials
   - Download JSON and save as: `~/.openclaw/workspace/.cache/youtube-credentials.json`

3. **Anthropic API Key**
   - Set `ANTHROPIC_API_KEY` environment variable
   - Or configure in `~/.openclaw/workspace/.cache/.env`

## First Run

```bash
python ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

This will:
1. Open browser for YouTube OAuth2 login
2. Save token to `~/.openclaw/workspace/.cache/youtube-token.json`
3. Begin monitoring

## Cron Setup

Every 30 minutes:
```bash
*/30 * * * * /usr/bin/python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py >> ~/.openclaw/workspace/.cache/monitor.log 2>&1
```

## Customization

### Response Templates
Edit `RESPONSE_TEMPLATES` in `youtube-comment-monitor.py`:

```python
RESPONSE_TEMPLATES = {
    "questions": "Your custom response here...",
    "praise": "Your custom response here..."
}
```

### Category Patterns
Add or modify keywords in `CATEGORY_PATTERNS` to improve categorization.

## Logs

All comments logged to: `~/.openclaw/workspace/.cache/youtube-comments.jsonl`

Each entry:
```json
{
  "timestamp": "2026-04-18T05:30:00.123456",
  "commenter": "User Name",
  "text": "Comment text...",
  "category": "questions|praise|spam|sales",
  "response_status": "auto_responded|flagged_for_review|no_response",
  "video_id": "dQw4w9WgXcQ"
}
```

## Monitoring

Check monitor log:
```bash
tail -f ~/.openclaw/workspace/.cache/monitor.log
```

View categorized comments:
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .
```

Count by category:
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq -r .category | sort | uniq -c
```

## Troubleshooting

**"ERROR: youtube-credentials.json not found"**
→ Download OAuth credentials from Google Cloud Console

**"ERROR: Google API client not installed"**
→ Run: `pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client`

**"No new comments in past hour"**
→ Script is working; channel just hasn't received comments recently

**Token expired**
→ Delete `~/.openclaw/workspace/.cache/youtube-token.json` and re-run to re-authenticate
