# YouTube Comment Monitor - Setup Guide

This automated monitor tracks new comments on the Concessa Obvius YouTube channel, categorizes them, auto-responds to questions/praise, and flags sales inquiries for review.

## Prerequisites

1. **Python 3.8+**
2. **Google Cloud Project** with YouTube Data API v3 enabled
3. **OAuth 2.0 Credentials** (Desktop application)

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project: **"Concessa Obvius Monitor"**
3. Enable YouTube Data API v3:
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Go to **Credentials** → **Create Credentials** → **OAuth client ID**
   - Choose **Desktop application**
   - Download the JSON file
   - Save it to: `~/.openclaw/workspace/.cache/youtube_credentials.json`

## Step 2: Install Dependencies

```bash
cd ~/.openclaw/workspace
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Step 3: Get Channel ID

If you don't know the exact channel ID:

```bash
python3 -c "
from urllib.parse import urlparse, parse_qs
url = input('Paste Concessa Obvius channel URL: ')
# Extract from various URL formats
if 'youtube.com/c/' in url:
    channel_handle = url.split('/c/')[1].split('/')[0]
    print(f'Channel handle: @{channel_handle}')
elif 'youtube.com/@' in url:
    channel_handle = url.split('@')[1].split('/')[0]
    print(f'Channel handle: @{channel_handle}')
elif 'youtube.com/channel/' in url:
    channel_id = url.split('/channel/')[1].split('/')[0]
    print(f'Channel ID: {channel_id}')
"
```

Update `CHANNEL_ID` in the monitor script with the actual ID.

## Step 4: First Run (Interactive)

The first time you run the script, it will:
1. Read your credentials from `youtube_credentials.json`
2. Open a browser for you to authorize
3. Save the token to `youtube_token.json`

```bash
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

Follow the browser prompt to authorize.

## Step 5: Configure Cron

Make the cron wrapper executable:

```bash
chmod +x ~/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

Install the cron job (every 30 minutes):

```bash
# Use crontab -e to edit your crontab, then add:
*/30 * * * * /bin/bash /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

Or use the setup script:

```bash
python3 ~/.openclaw/workspace/.cache/setup-youtube-cron.py
```

## Monitoring

### View Logs

Monitor the live monitor logs:
```bash
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log
tail -f ~/.openclaw/workspace/.cache/youtube-monitor-cron.log
```

### View Comment History

All comments are logged to `.cache/youtube-comments.jsonl`:

```bash
# Pretty-print the last 10 comments
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | tail -10 | python3 -m json.tool

# Count comments by category
jq -r '.category' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | sort | uniq -c

# Find flagged sales comments
jq 'select(.response_status == "flagged_for_review")' ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

### Dashboard Command

Get current stats:
```bash
tail -100 ~/.openclaw/workspace/.cache/youtube-monitor.log | grep -A 20 "Stats:"
```

## Customization

### Response Templates

Edit `RESPONSE_TEMPLATES` in the monitor script to customize auto-responses:

```python
RESPONSE_TEMPLATES = {
    "question": "Your custom response for questions...",
    "praise": "Your custom response for praise...",
}
```

### Category Patterns

Update `PATTERNS` dict to adjust categorization logic:

```python
PATTERNS = {
    "spam": [r"pattern1", r"pattern2"],
    "sales": [r"partnership", r"sponsorship"],
    # ...
}
```

### Upgrade to LLM-Based Categorization

For more accurate categorization, modify `categorize_comment()` to use Claude or another LLM:

```python
def categorize_comment(text: str) -> str:
    """Use Claude to categorize comments."""
    # Call to Claude API for smarter categorization
    pass
```

## Troubleshooting

### "No valid YouTube credentials found"

- Verify `youtube_credentials.json` exists and is valid
- Delete `youtube_token.json` and run the script again to re-authorize
- Check that you've enabled YouTube Data API v3 in Google Cloud Console

### "Channel not found"

- Verify `CHANNEL_ID` is correct
- Run the channel lookup command above

### Cron job not running

- Check crontab: `crontab -l`
- Check system logs: `log stream --predicate 'process == "cron"'`
- Verify script is executable: `ls -la ~/.openclaw/workspace/.cache/youtube-monitor-cron.sh`
- Test manually: `bash ~/.openclaw/workspace/.cache/youtube-monitor-cron.sh`

### Rate limiting

The script respects YouTube API quotas. Each operation costs quota:
- Get comments: 1 quota unit
- Post reply: 50 quota units
- Typical daily limit: 10,000 quota units

Monitor your quota in Google Cloud Console > YouTube Data API v3 > Quotas.

## API Reference

The monitor integrates with:

- **YouTube Data API v3**: Fetch comments, post replies
- **OAuth 2.0**: Secure authentication
- **Local JSON storage**: `.cache/youtube-comments.jsonl` for audit trail

## Security Notes

- `youtube_credentials.json`: **Never commit to git**. Add to `.gitignore`.
- `youtube_token.json`: Contains refresh token. Keep secure.
- Auto-responses are logged and can be reviewed/edited before posting (optional manual approval step can be added)

## Next Steps

1. ✅ Create Google Cloud Project
2. ✅ Download credentials JSON
3. ✅ Run script for first authorization
4. ✅ Set up cron job
5. 📊 Monitor logs and adjust templates as needed
6. 🔄 Periodic review of flagged sales comments

---

**Questions?** Check the logs or reach out for customization help.
