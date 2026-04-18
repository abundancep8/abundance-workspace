# YouTube Comment Monitor Setup

## Quick Start

### 1. Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (name: "Concessa Obvius Monitor")
3. Enable the YouTube Data API v3
4. Create a **Service Account** (not OAuth):
   - Go to Credentials → Create Credentials → Service Account
   - Download the JSON key file
5. Save the JSON file to: `~/.openclaw/youtube-credentials.json`

### 2. Update Channel Configuration

Edit `scripts/youtube-comment-monitor.py` and replace:

```python
CHANNEL_ID = "UCH_YOUR_CHANNEL_ID"
```

Find your actual channel ID by:
- Going to your YouTube channel
- Checking the URL: `youtube.com/channel/UC...`
- Or use: `https://www.youtube.com/@yourusername` → inspect network for channel ID

### 3. Test the Script

```bash
cd ~/.openclaw/workspace
python3 scripts/youtube-comment-monitor.py
```

If successful, you'll see:
- Log entries in `.cache/youtube-comments.jsonl`
- A summary report with stats
- Processed comments in the log

### 4. Set Up Cron (Every 30 Minutes)

Add to your crontab (`crontab -e`):

```bash
# YouTube Comment Monitor - Every 30 minutes
*/30 * * * * cd /Users/abundance/.openclaw/workspace && /usr/bin/python3 scripts/youtube-comment-monitor.py >> logs/youtube-monitor.log 2>&1
```

### 5. Create Log Directory

```bash
mkdir -p ~/.openclaw/workspace/logs
```

## Configuration

### Template Responses

Edit the `TEMPLATES` dict in `youtube-comment-monitor.py`:

```python
TEMPLATES = {
    "question": "Your question response template here...",
    "praise": "Your praise response template here...",
}
```

### Category Patterns

Modify `PATTERNS` to customize how comments are categorized:

```python
PATTERNS = {
    "questions": [...],   # Patterns that match questions
    "praise": [...],      # Patterns that match praise
    "spam": [...],        # Patterns that match spam
    "sales": [...],       # Patterns that match sales/partnerships
}
```

## Monitoring Output

### Log File Format (.cache/youtube-comments.jsonl)

Each line is a JSON object:

```json
{
  "timestamp": "2026-04-17T14:30:00.000000Z",
  "comment_id": "UgxAbC123xyz",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "questions",
  "response_status": "sent",
  "logged_at": "2026-04-17T14:35:12.345678Z"
}
```

### Response Statuses

- `sent` - Auto-response was sent successfully
- `pending` - Comment received but no response sent
- `error` - Error sending response
- `flagged_for_review` - Sales/partnership comments (manual review needed)
- `spam_filtered` - Marked as spam

### Sample Report Output

```json
{
  "timestamp": "2026-04-17T14:35:12.345678Z",
  "stats": {
    "total_processed": 42,
    "auto_responses_sent": 15,
    "flagged_for_review": 3,
    "errors": 0
  },
  "log_entries": {
    "total": 42,
    "by_category": {
      "questions": 15,
      "praise": 12,
      "sales": 3,
      "spam": 9,
      "other": 3
    },
    "by_status": {
      "sent": 27,
      "flagged_for_review": 3,
      "spam_filtered": 9,
      "pending": 3
    }
  }
}
```

## Troubleshooting

### "Credentials file not found"

Make sure `~/.openclaw/youtube-credentials.json` exists and is valid.

### "YouTube API not authenticated"

Check that:
- Service account credentials JSON is in the right place
- YouTube Data API v3 is enabled in Google Cloud Console
- Service account has access to the channel

### "Module not found: google.auth"

Install dependencies:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Comments not showing up

- Check that `CHANNEL_ID` is correct
- Verify the service account email has channel access
- Review logs/youtube-monitor.log for errors

## Advanced

### Running on Schedule with OpenClaw

Instead of system cron, you can use OpenClaw's cron feature. In HEARTBEAT.md or a cron task:

```
Every 30 minutes: Run youtube-comment-monitor.py and report stats
```

### Customizing Auto-Responses

The templates support basic customization. To add context-aware responses:

1. Parse the comment text more thoroughly
2. Extract specific keywords (tools, timeline, cost)
3. Return targeted responses based on what they're asking

### Filtering by Subscribers/Verified

The current script processes all comments. To filter:

```python
# In _process_comment():
if not comment.get("authorChannelId"):
    return  # Skip anonymous
```

## Support

Check logs:

```bash
tail -f logs/youtube-monitor.log
```

View all comments:

```bash
cat .cache/youtube-comments.jsonl | jq '.'
```

Filter by category:

```bash
cat .cache/youtube-comments.jsonl | jq 'select(.category=="questions")'
```
