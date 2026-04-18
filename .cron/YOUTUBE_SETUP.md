# YouTube Comment Monitor - Setup Guide

## Prerequisites

### 1. Install Dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Create YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project: "YouTube Comment Monitor"
3. Enable the YouTube Data API v3:
   - Search "YouTube Data API v3"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
   - Application type: **Desktop application**
   - Download JSON file as `youtube_credentials.json` in your workspace root

### 3. Configure Credentials
```bash
# Place the downloaded file in your workspace root
cp ~/Downloads/client_secret_*.json youtube_credentials.json
```

## First Run

The script will:
1. Check for `youtube_credentials.json`
2. Open a browser for you to authorize access
3. Save token to `.cache/youtube_token.json` (secure, persisted)
4. Begin monitoring

## Configuration

Edit the script to customize:

**Channel to monitor:**
```python
CHANNEL_HANDLE = "ConcessaObvius"  # Change to your channel
```

**Auto-response templates:**
```python
RESPONSE_TEMPLATES = {
    "questions": "Your template here...",
    "praise": "Your template here..."
}
```

**Categorization keywords:**
Edit the `categorize_comment()` function to add/remove keywords.

## Logs & Reports

**Comment log:** `.cache/youtube-comments.jsonl`
- Each line is a JSON entry with: timestamp, commenter, text, category, response_status

**State file:** `.cache/youtube-monitor-state.json`
- Tracks last check time to avoid reprocessing

## Viewing Reports

```bash
# Recent comments
tail -50 .cache/youtube-comments.jsonl | jq .

# Comments flagged for review
cat .cache/youtube-comments.jsonl | jq 'select(.response_status == "flagged")'

# Count by category
cat .cache/youtube-comments.jsonl | jq -s 'group_by(.category) | map({category: .[0].category, count: length})'
```

## Cron Job Setup

To run every 30 minutes:

```bash
# Edit crontab
crontab -e

# Add (adjust path to your workspace):
*/30 * * * * cd /Users/abundance/.openclaw/workspace && python .cron/youtube-comment-monitor.py >> .cache/youtube-monitor.log 2>&1
```

## Troubleshooting

**"youtube_credentials.json not found"**
- Follow step 2 above to download from Google Cloud Console

**"Channel not found"**
- Check `CHANNEL_HANDLE` matches the exact channel name/handle

**Replies not posting**
- Verify your YouTube account has permission to reply (channel owner)
- Check `.cache/youtube-monitor.log` for errors

**OAuth token expired**
- Delete `.cache/youtube_token.json` and rerun; you'll be prompted to authorize again

## Notes

- First run may take longer as it authorizes your account
- The script only processes new comments since last check
- Auto-responses are only sent once per comment
- Category 4 (sales) comments are flagged but not automatically replied to
