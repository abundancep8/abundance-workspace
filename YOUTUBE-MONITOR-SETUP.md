# YouTube Comment Monitor Setup Guide

## Quick Start

The `scripts/youtube-monitor.py` script monitors the Concessa Obvius YouTube channel for new comments, categorizes them, and sends auto-responses.

## Prerequisites

```bash
# Install Google API libraries
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Make script executable
chmod +x scripts/youtube-monitor.py
```

## YouTube API Setup

1. **Create Google Cloud Project**
   - Go to https://console.cloud.google.com/
   - Create a new project (name: "YouTube Monitor")

2. **Enable YouTube Data API**
   - In Cloud Console, go to APIs & Services > Library
   - Search for "YouTube Data API v3"
   - Click it and press "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to APIs & Services > Credentials
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the JSON file

4. **Save Credentials**
   ```bash
   # Save the downloaded JSON to:
   cp ~/Downloads/client_secret_*.json ~/.openclaw/workspace/youtube-credentials.json
   ```

5. **Run Script Once Manually**
   ```bash
   python3 scripts/youtube-monitor.py
   ```
   This will:
   - Open your browser to authorize access
   - Save a token for future runs
   - Process any pending comments

## Cron Setup (Every 30 Minutes)

### Option 1: System Cron (Recommended)

```bash
# Edit crontab
crontab -e

# Add this line to run every 30 minutes:
*/30 * * * * cd ~/.openclaw/workspace && /usr/bin/python3 scripts/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1
```

### Option 2: OpenClaw Cron

Use the built-in OpenClaw cron scheduling:

```bash
openclaw cron schedule youtube-monitor \
  --interval "*/30 * * * *" \
  --command "cd ~/.openclaw/workspace && python3 scripts/youtube-monitor.py"
```

### Option 3: Launchd (macOS)

Create `~/Library/LaunchAgents/com.youtube.monitor.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.youtube.monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/abundance/.openclaw/workspace/scripts/youtube-monitor.py</string>
    </array>
    <key>StartInterval</key>
    <integer>1800</integer> <!-- 30 minutes in seconds -->
    <key>StandardOutPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log</string>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.youtube.monitor.plist
```

## Monitoring & Logs

### Check Live Log
```bash
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log
```

### View Processed Comments
```bash
# Pretty-print JSONL log
jq . ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Count by category
jq '.category' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | sort | uniq -c

# See flagged sales comments
jq 'select(.category==4)' ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

## Configuration

### Modify Keywords

Edit `scripts/youtube-monitor.py`, find the `KEYWORDS` section:

```python
KEYWORDS = {
    1: {  # Questions
        "how do i", "tools", "cost", ...
    },
    2: {  # Praise
        "amazing", "inspiring", ...
    },
    ...
}
```

### Change Response Templates

In the `send_response()` calls, modify text:

```python
response_text = "Your custom message here"
```

### Track Different Channel

Edit the script:
```python
CHANNEL_NAME = "Your Channel Name"
```

## Troubleshooting

### "Credentials not found"
- Make sure `youtube-credentials.json` exists in workspace root
- Run the script once manually to authorize

### "Channel not found"
- Check the exact channel name
- Make sure your Google account has access to the channel

### Responses not posting
- Check YouTube API quota in Cloud Console
- Verify the channel owner account is authenticated
- Check `.cache/youtube-monitor.log` for errors

### Cron not running
- Verify path is absolute in cron command
- Check cron logs: `log stream --predicate 'eventMessage contains "youtube"'`
- Test manually: `python3 ~/.openclaw/workspace/scripts/youtube-monitor.py`

## Output

Each run produces:
- **stdout**: Summary report (comments processed, categories, responses sent, flagged items)
- **`.cache/youtube-comments.jsonl`**: Full audit log (one JSON object per line)
- **`.cache/.youtube-monitor-state.json`**: Last check timestamp and processed comment IDs

Example report output:
```
============================================================
📊 YOUTUBE COMMENT MONITOR REPORT
============================================================
⏱️  Run time: 2026-04-21 00:35:00
📝 Total comments processed: 5
📋 Breakdown by category:
   Questions: 2
   Praise: 2
   Sales: 1
✅ Auto-responses sent: 4
🚩 Flagged for review: 1
📁 Log file: /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl
============================================================
```

## Security Notes

- `youtube-token.json` is automatically saved after first auth — this is sensitive, keep it private
- `youtube-credentials.json` should not be committed to version control
- The script runs with your channel owner credentials, so only deploy on trusted machines
- Consider using a service account if deploying to servers

---

**Need help?** Check the log files or run the script manually in debug mode.
