# YouTube Comment Monitor - Setup Guide

## Step 1: Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or use existing)
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the JSON file and save as: `~/.youtube_credentials.json`

## Step 2: Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Step 3: Find Your Channel ID

Navigate to your YouTube channel and look at the URL:
- Format: `youtube.com/c/CHANNEL_NAME/` → extract channel ID
- Or use this search: https://www.youtube.com/s/gaming/search

Get the Concessa Obvius channel ID and update line in the script:
```python
CHANNEL_ID = "UCxxxxxxxxxxxxx"  # Replace this
```

## Step 4: Test Manually

```bash
cd ~/.openclaw/workspace
python3 .cache/youtube-monitor.py
```

First run will authenticate and set up the cache directory.

## Step 5: Schedule with Cron (Every 30 Minutes)

```bash
crontab -e
```

Add this line:
```
*/30 * * * * cd ~/.openclaw/workspace && python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1
```

Verify it's installed:
```bash
crontab -l
```

## Step 6: Monitor Logs

```bash
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log
```

## Customization

Edit `TEMPLATES` dict in the script to customize auto-responses:

```python
TEMPLATES = {
    "question": "Your custom question response...",
    "praise": "Your custom praise response..."
}
```

Edit `SPAM_KEYWORDS` etc. to adjust categorization logic.

## Files Generated

- `.cache/youtube-comments.jsonl` - All comments logged (1 per line)
- `.cache/youtube-monitor-state.json` - Last check timestamp & processed IDs
- `.cache/youtube-monitor.log` - Cron execution log

## Troubleshooting

**"Credentials file not found"**
- Save your OAuth JSON file to `~/.youtube_credentials.json`

**"API not enabled"**
- Go to Cloud Console → Enable YouTube Data API v3

**"Invalid channel ID"**
- Double-check the channel ID format (should be "UC..." followed by letters/numbers)

**Cron not running**
- Check permissions: `chmod +x .cache/youtube-monitor.py`
- Verify Python path: `which python3`
- Check crontab logs: `log stream --predicate 'eventMessage contains[c] "cron"' --level debug`

## Manual Execution

Run anytime to check for new comments:
```bash
python3 ~/.openclaw/workspace/.cache/youtube-monitor.py
```
