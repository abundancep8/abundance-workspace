# YouTube DM Monitor - Setup Guide

## Overview

Automated monitoring and categorization of YouTube DMs for the "Concessa Obvius" channel with auto-responses and reporting.

**Run:** Every hour via cron

## Prerequisites

1. **Google API Credentials**
   - Create OAuth 2.0 Desktop Application credentials in [Google Cloud Console](https://console.cloud.google.com/)
   - Download the credentials JSON file
   - Save as `.cache/youtube-credentials.json`

2. **Python Packages**
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

## Setup

### 1. Configure YouTube API Credentials

```bash
# In Google Cloud Console:
1. Create new project or select existing
2. Enable YouTube Data API v3
3. Create OAuth 2.0 Desktop Application (Authorized JavaScript origins + Redirect URIs)
4. Download credentials as JSON
5. Save to .cache/youtube-credentials.json
```

### 2. Make Script Executable

```bash
chmod +x .cache/youtube-dm-monitor.py
```

### 3. Set Up Cron Job

**Option A: Using crontab**
```bash
# Run every hour
0 * * * * cd /Users/abundance/.openclaw/workspace && python3 .cache/youtube-dm-monitor.py >> .cache/youtube-dm-monitor.log 2>&1
```

**Option B: Using macOS LaunchAgent** (recommended)
Create `~/Library/LaunchAgents/com.youtube.dm-monitor.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.youtube.dm-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/abundance/.openclaw/workspace/.cache/youtube-dm-monitor.py</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>StandardOutPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-dm-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-dm-monitor.log</string>
    <key>WorkingDirectory</key>
    <string>/Users/abundance/.openclaw/workspace</string>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.youtube.dm-monitor.plist
```

## Features

### DM Categorization

The script automatically categorizes incoming DMs into 4 categories:

1. **Setup Help** - "How do I set up?", "I'm confused", technical issues
2. **Newsletter** - Email list signups, update requests
3. **Product Inquiry** - Pricing, features, purchase intent, recommendations
4. **Partnership** - Collaborations, sponsorships, affiliate programs

### Auto-Responses

Each category gets a templated response:
- **Setup**: Directs to setup guide
- **Newsletter**: Confirms email signup
- **Product**: Describes value, links to product page
- **Partnership**: Flags for manual review

### Logging

All DMs logged to `.cache/youtube-dms.jsonl` with:
- Timestamp
- Sender name & ID
- DM text
- Detected category
- Response template used
- Response delivery status

### Hourly Report

Printed at each run:
```
📊 SUMMARY
  Total DMs processed:    N
  Auto-responses sent:    N
  Product inquiries:      N
  Partnership requests:   N

💡 PRODUCT INQUIRIES (Conversion Potential)
  • Sender: [message preview]...

🤝 PARTNERSHIPS (Flagged for Manual Review)
  • Sender: [message preview]...
```

## Files

- `.cache/youtube-dm-monitor.py` - Main script
- `.cache/youtube-credentials.json` - OAuth credentials (create manually)
- `.cache/youtube-token.json` - Generated auth token (auto-created)
- `.cache/youtube-dm-state.json` - Monitor state (timestamp, count)
- `.cache/youtube-dms.jsonl` - DM log (line-delimited JSON)
- `.cache/youtube-dm-monitor.log` - Execution log

## Manual DM Processing

To manually add DMs for testing or if API isn't available:

```python
# Add to a test file, then import:
test_dms = [
    {
        'id': 'dm_123',
        'sender': 'John Doe',
        'sender_id': 'user_123',
        'text': 'How do I set up your product?'
    },
    # ... more DMs
]
```

## Troubleshooting

**"Authentication failed"**
- Ensure `.cache/youtube-credentials.json` exists
- Check OAuth scopes include `youtube.force-ssl`
- Try deleting `.cache/youtube-token.json` and re-authenticating

**"No new DMs found"**
- This is normal if no new DMs since last check
- Monitor will continue running on schedule

**API Rate Limits**
- YouTube API has rate limits (1M quota per day)
- At 1 call/hour = 24 calls/day (well within limits)

## Customization

Edit `RESPONSES` dict in the script to customize templates:

```python
RESPONSES = {
    'setup_help': 'Your custom setup message...',
    'newsletter': 'Your custom newsletter message...',
    # ...
}
```

Edit categorization patterns in `categorize_dm()` method to adjust detection.

## Monitoring

Check status:
```bash
# View recent reports
tail -50 .cache/youtube-dm-monitor.log

# View DM log
tail -5 .cache/youtube-dms.jsonl | jq .

# Check cron status (if using LaunchAgent)
launchctl list | grep youtube
```

## Support

For issues or customizations, review the inline comments in `youtube-dm-monitor.py`.
