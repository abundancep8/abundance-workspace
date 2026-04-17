# YouTube Comment Monitor Setup

## Prerequisites

### 1. YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or use existing)
3. Enable the **YouTube Data API v3**
4. Create an **API Key** (in Credentials)
5. Copy your API key

### 2. Get Your Channel ID

For "Concessa Obvius" channel:
1. Go to the YouTube channel
2. Look at the URL: `youtube.com/@username` or `youtube.com/c/ChannelName`
3. Or visit the channel → click the profile icon → "Channel" → URL contains the ID
4. Format: Usually starts with `UC` followed by characters

## Installation

### Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Set Environment Variables

Create a `.env` file in the workspace:

```bash
export YOUTUBE_API_KEY="your-api-key-here"
export YOUTUBE_CHANNEL_ID="UCxxxxxxxxxxxxxxxx"
```

Then source it before running:

```bash
source .env
python3 .cache/youtube-monitor.py
```

## Running the Monitor

### Manual Run
```bash
source .env && python3 .cache/youtube-monitor.py
```

### As a Cron Job (Every 30 Minutes)

Add to your crontab:
```bash
*/30 * * * * cd /Users/abundance/.openclaw/workspace && source .cache/.env && python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1
```

### Monitor Logs
```bash
# See latest report
tail -20 .cache/youtube-monitor.log

# View processed comments
cat .cache/youtube-comments.jsonl | jq .

# Filter for flagged sales comments
cat .cache/youtube-comments.jsonl | jq 'select(.response_status=="flagged_review")'
```

## Output Files

- **`youtube-comments.jsonl`** — All processed comments (one JSON per line)
- **`youtube-state.json`** — Internal state (last processed ID, counts)
- **`youtube-monitor.log`** — Execution log (when run via cron)

## Customization

Edit template responses in `youtube-monitor.py`:

```python
TEMPLATES = {
    "question": "Your custom question response...",
    "praise": "Your custom praise response..."
}
```

Edit keywords in `CATEGORIES` dict to tune categorization:

```python
CATEGORIES = {
    "question": [r"how\s+do\s+i", r"what.*cost", ...],
    "praise": [r"amazing", r"inspiring", ...],
    ...
}
```

## Testing

Dry run (no API calls):
```bash
YOUTUBE_CHANNEL_ID="test" python3 .cache/youtube-monitor.py
```

This will show missing credentials without making API calls.
