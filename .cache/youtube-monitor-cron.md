# YouTube Comment Monitor - Cron Configuration

## Schedule
Every 30 minutes: `*/30 * * * *`

## Setup Instructions

### 1. Get YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **YouTube Data API v3**:
   - Search for "YouTube Data API v3"
   - Click Enable
4. Create credentials (API Key):
   - Click "Create Credentials" → "API Key"
   - Copy the key
5. Add to your environment:
   ```bash
   export YOUTUBE_API_KEY="your-api-key-here"
   ```

Or add to your OpenClaw config:
```yaml
env:
  YOUTUBE_API_KEY: "your-api-key-here"
```

### 2. Install Dependencies

```bash
pip install google-auth google-api-python-client
```

### 3. Register Cron Job in OpenClaw

Add this to your `openclaw.yml`:

```yaml
cron:
  - id: youtube-comment-monitor
    schedule: "*/30 * * * *"
    command: "python3 .cache/youtube-monitor.py"
    env:
      YOUTUBE_API_KEY: "${YOUTUBE_API_KEY}"
    timeout: 300
    notify:
      channel: discord
      on: always
```

## Output

- **Log file:** `.cache/youtube-comments.jsonl` (JSONL format with timestamp, author, text, category, response_status)
- **State file:** `.cache/youtube-monitor-state.json` (tracks last processed comments)

## Comment Categories

| Category | Action |
|----------|--------|
| **Question** | Auto-respond with FAQ/help template |
| **Praise** | Auto-respond with thank you |
| **Spam** | Log only (crypto, MLM, trading schemes) |
| **Sales** | Flag for manual review (partnerships, sponsorships) |
| **Neutral** | Log only |

## Example Log Entry

```json
{
  "timestamp": "2026-04-20T08:30:45.123456",
  "published": "2026-04-20T08:15:30Z",
  "video_id": "dQw4w9WgXcQ",
  "comment_id": "Ugya1b2c3d4e5f6g7h8i",
  "author": "John Doe",
  "text": "How do I get started with this?",
  "category": "question",
  "response_status": "auto_responded"
}
```

## Dashboard

View comment stats:
```bash
tail -f .cache/youtube-comments.jsonl | jq .
```

Count by category:
```bash
jq -r .category .cache/youtube-comments.jsonl | sort | uniq -c
```

Sales/Review queue:
```bash
jq 'select(.response_status == "flagged")' .cache/youtube-comments.jsonl
```
