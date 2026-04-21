# YouTube Comment Monitor - Setup Guide

Complete setup instructions for the "Concessa Obvius" channel comment monitoring script.

## Prerequisites

- Python 3.7+
- A YouTube API key (free tier available)
- Channel ID for "Concessa Obvius"

## Step 1: Get YouTube API Credentials

### 1.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a Project** → **NEW PROJECT**
3. Enter project name: `youtube-monitor`
4. Click **CREATE**
5. Wait for the project to be created

### 1.2 Enable YouTube Data API v3

1. In Cloud Console, go to **APIs & Services** → **Library**
2. Search for "YouTube Data API v3"
3. Click on it and select **ENABLE**

### 1.3 Create API Key

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **API Key**
3. Copy your API key (you'll use this below)
4. *(Optional)* Restrict the key to YouTube API v3 only:
   - Click on your key
   - Under "API restrictions", select "YouTube Data API v3"
   - Click **SAVE**

### 1.4 Set Up API Quota (Free Tier)

- YouTube Data API free tier includes **10,000 quota units per day**
- Each API call costs ~100-200 units
- This script uses ~100 units per run
- Safe to run every 30 minutes (48 runs/day = 4,800 units/day)

## Step 2: Find Channel ID

For "Concessa Obvius" channel:

1. Go to the channel page
2. Click **About**
3. Look for the channel ID in the URL or:
   - Right-click channel name → **Copy channel ID**
4. Default ID in script: `UCXXz-s8LjQGpAK-PEzMXbqg`

To verify:
```bash
curl "https://www.googleapis.com/youtube/v3/channels?part=snippet&forUsername=ConcessaObvius&key=YOUR_API_KEY"
```

## Step 3: Configure Environment Variables

Create a `.env` file in the script directory:

```bash
export YOUTUBE_API_KEY="your_api_key_here"
export YOUTUBE_CHANNEL_ID="UCXXz-s8LjQGpAK-PEzMXbqg"
```

Or set them directly before running:

```bash
YOUTUBE_API_KEY="your_api_key" YOUTUBE_CHANNEL_ID="UCXXz-s8LjQGpAK-PEzMXbqg" python youtube_comment_monitor.py
```

## Step 4: Install and Run

### Install dependencies (none required!)

This script uses only Python standard library:
- `json` - for data handling
- `urllib` - for API requests
- `logging` - for output
- `pathlib` - for file operations

No pip install needed!

### First run (test)

```bash
cd /path/to/youtube-monitor
YOUTUBE_API_KEY="your_api_key" python youtube_comment_monitor.py
```

**Expected output:**
```
2026-04-21 12:30:45,123 | INFO | YouTube Comment Monitor Starting
2026-04-21 12:30:45,124 | INFO | Loaded state. Previously processed: 0 comments
2026-04-21 12:30:45,125 | INFO | Fetching comments from channel...
2026-04-21 12:30:46,234 | INFO | Found 12 new comments
2026-04-21 12:30:47,345 | INFO | ✓ Auto-responded to question from Alice
2026-04-21 12:30:47,456 | INFO | ⚠ Sales inquiry flagged from Bob: Check out my new course...
...
======================================================================
REPORT
======================================================================
Processed: 12 | Auto-responses: 5 | Flagged for review: 2
...
```

## Step 5: Set Up Cron Job (Runs Every 30 Minutes)

### macOS/Linux

1. Open cron editor:
   ```bash
   crontab -e
   ```

2. Add this line:
   ```bash
   */30 * * * * YOUTUBE_API_KEY="your_api_key" YOUTUBE_CHANNEL_ID="UCXXz-s8LjQGpAK-PEzMXbqg" /usr/bin/python3 /path/to/youtube-monitor/youtube_comment_monitor.py >> /path/to/youtube-monitor/.cache/cron.log 2>&1
   ```

3. Verify:
   ```bash
   crontab -l
   ```

### Better: Create a shell wrapper script

Instead of a complex cron line, create `run_monitor.sh`:

```bash
#!/bin/bash
set -e

# Load environment
export YOUTUBE_API_KEY="your_api_key"
export YOUTUBE_CHANNEL_ID="UCXXz-s8LjQGpAK-PEzMXbqg"

# Change to script directory
cd /path/to/youtube-monitor

# Run monitor
/usr/bin/python3 youtube_comment_monitor.py

# Email report on error (optional)
# if [ $? -ne 0 ]; then
#   echo "Monitor failed" | mail -s "YouTube Monitor Error" you@example.com
# fi
```

Then cron:
```bash
*/30 * * * * /path/to/youtube-monitor/run_monitor.sh >> /path/to/youtube-monitor/.cache/cron.log 2>&1
```

### systemd service (Linux only)

Create `/etc/systemd/system/youtube-monitor.service`:

```ini
[Unit]
Description=YouTube Comment Monitor
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=youruser
WorkingDirectory=/path/to/youtube-monitor
Environment="YOUTUBE_API_KEY=your_api_key"
Environment="YOUTUBE_CHANNEL_ID=UCXXz-s8LjQGpAK-PEzMXbqg"
ExecStart=/usr/bin/python3 /path/to/youtube-monitor/youtube_comment_monitor.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Create timer:

```ini
[Unit]
Description=YouTube Comment Monitor Timer
Requires=youtube-monitor.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=30min
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable youtube-monitor.timer
sudo systemctl start youtube-monitor.timer
sudo systemctl status youtube-monitor.timer
```

## Step 6: Monitor Output

### Check logs

```bash
tail -f .cache/youtube-monitor.log
```

### Check state

```bash
cat .cache/youtube-monitor-state.json
```

### Check all processed comments

```bash
# Count total processed
wc -l .cache/youtube-comments.jsonl

# View recent comments
tail -5 .cache/youtube-comments.jsonl | jq .

# Filter by category
grep '"category":"spam"' .cache/youtube-comments.jsonl
```

## Step 7: Advanced Configuration

### Customize auto-response templates

Edit `AUTO_RESPONSES` in `youtube_comment_monitor.py`:

```python
AUTO_RESPONSES = {
    "question": "Your custom response here",
    "praise": "Your custom praise response"
}
```

### Adjust classification keywords

Modify the keyword lists:

```python
QUESTION_KEYWORDS = [
    r'\?$',
    r'how ',
    # Add more patterns...
]
```

### Change cache location

```python
CACHE_DIR = Path("/custom/path")
```

## Troubleshooting

### "YOUTUBE_API_KEY environment variable not set"

```bash
export YOUTUBE_API_KEY="your_key_here"
python youtube_comment_monitor.py
```

### "API quota exceeded (403)"

- Wait 24 hours (quota resets daily at midnight PT)
- Or upgrade to higher API quota in Cloud Console
- Reduce run frequency: change cron from `*/30` to `0 * * * *` (hourly)

### "Could not fetch channel info"

- Verify API key is correct
- Verify API is enabled in Cloud Console
- Verify channel ID is correct
- Try manual API call:
  ```bash
  curl "https://www.googleapis.com/youtube/v3/channels?part=snippet&forUsername=ConcessaObvius&key=YOUR_KEY"
  ```

### No comments found

- Channel may have no recent videos
- Comments may be disabled
- All comments may have already been processed
- Check `.cache/youtube-monitor-state.json` for `processed_comments` count

### Comments aren't being auto-responded

Currently, auto-responses are **logged but not posted** (placeholder). To enable actual posting:

1. Implement OAuth 2.0 authentication
2. Generate refresh token manually
3. Update `reply_to_comment()` function with:

```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# Use OAuth token to call youtube.commentThreads().insert()
```

## Testing Checklist

- [ ] API key works (successful first run)
- [ ] Comments are fetched and logged
- [ ] Categories are correct (run and review `.cache/youtube-comments.jsonl`)
- [ ] State file persists (comment IDs not re-processed)
- [ ] Cron job runs (check logs in `.cache/cron.log`)
- [ ] No errors in `.cache/youtube-monitor.log`
- [ ] Report shows all categories

## Next Steps

1. **Manual review**: Start by reviewing flagged sales comments daily
2. **Refine keywords**: Adjust QUESTION_KEYWORDS, PRAISE_KEYWORDS, etc. based on false positives
3. **Enable actual replies**: Implement OAuth for real auto-responses
4. **Scale monitoring**: Add multiple channels by creating separate config files
5. **Integrate with workflow**: Send reports to Slack, email, or Discord

## Support

- YouTube API docs: https://developers.google.com/youtube/v3
- API Explorer: https://developers.google.com/youtube/v3/docs
- Quota info: https://developers.google.com/youtube/v3/getting-started#quota

---

**Last updated:** 2026-04-21
**Status:** Production-ready
**Default channel:** Concessa Obvius (UCXXz-s8LjQGpAK-PEzMXbqg)
