# YouTube Comment Monitor Setup

## Prerequisites

1. **Python 3.8+** with Google API libraries:
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. **YouTube Data API** enabled in Google Cloud:
   - Go to https://console.cloud.google.com
   - Create a new project
   - Enable "YouTube Data API v3"
   - Create OAuth 2.0 credentials (Desktop app)
   - Download credentials as JSON

3. **Channel ID** for "Concessa Obvius"
   - Visit the channel
   - Extract ID from URL or use channel lookup

## Configuration

### 1. Set Channel ID

Edit `youtube-monitor.py` and update:
```python
CHANNEL_ID = "UCYourChannelId"  # Replace with actual ID
```

### 2. Add Credentials

Save your OAuth credentials JSON to:
```
~/.openclaw/youtube-credentials.json
```

First run will prompt for authorization and cache a token automatically.

### 3. Customize Response Templates

Edit the `RESPONSES` dict in `youtube-monitor.py`:
```python
RESPONSES = {
    "question": "Your custom response here...",
    "praise": "Your custom response here...",
}
```

## Categorization Rules

The monitor categorizes comments into 4 types:

| Category | Pattern | Auto-Response |
|----------|---------|----------------|
| **Question** | "how", "what", "where", "cost", "timeline", "tools", "?" | ✅ Yes |
| **Praise** | "amazing", "awesome", "inspiring", "love", "thank" | ✅ Yes |
| **Spam** | "crypto", "bitcoin", "MLM", "make money fast" | ❌ No |
| **Sales** | "partnership", "collaborate", "sponsor", "business opportunity" | 🚩 Flagged |

Customize patterns in the `PATTERNS` dict.

## Cron Schedule

Add to crontab (every 30 minutes):
```bash
0,30 * * * * cd /Users/abundance/.openclaw/workspace && bash youtube-monitor.sh
```

View logs:
```bash
ls -la .cache/logs/
tail -f .cache/logs/monitor_*.log
```

## Data Storage

Comments are logged to `.cache/youtube-comments.jsonl`:

```json
{
  "timestamp": "2026-04-16T12:05:00.123456",
  "comment_id": "Ugx...",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "question",
  "response_status": "sent"
}
```

Response statuses:
- `sent` - Auto-response delivered
- `failed` - Auto-response failed to send
- `flagged` - Flagged for manual review (sales inquiries)
- `none` - No action taken

## Monitoring

View current stats:
```bash
python3 -c "
import json
from pathlib import Path

log_file = Path('.cache/youtube-comments.jsonl')
if log_file.exists():
    comments = [json.loads(line) for line in log_file.read_text().split('\n') if line]
    categories = {}
    for c in comments:
        cat = c['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f'Total comments: {len(comments)}')
    for cat, count in categories.items():
        print(f'  {cat}: {count}')
"
```

## Troubleshooting

**"YouTube credentials not found"**
- Save your OAuth JSON to `~/.openclaw/youtube-credentials.json`

**"Channel not found"**
- Verify `CHANNEL_ID` is correct in `youtube-monitor.py`

**"Permission denied" on first run**
- Browser will open for authentication
- Allow all requested permissions
- Token caches automatically

**No comments being processed**
- Check that videos have comments enabled
- Verify channel ID is correct
- Check logs: `tail .cache/logs/monitor_*.log`

## Manual Test

```bash
python3 youtube-monitor.py
```

Should output a report showing comments processed and actions taken.
