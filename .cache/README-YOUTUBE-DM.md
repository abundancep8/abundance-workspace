# 📺 YouTube DM Monitor - Complete Setup

**Status:** ✅ Ready to deploy  
**Channel:** Concessa Obvius  
**Frequency:** Hourly  
**Last Updated:** 2026-04-14

## 🎯 What It Does

Automatically monitors YouTube DMs, categorizes them, sends templated responses, and provides hourly reports on engagement metrics.

### Features

✅ **Auto-Categorization** - 4 smart categories  
✅ **Template Responses** - Customizable per category  
✅ **Conversation Logging** - JSONL format for analysis  
✅ **Partnership Flagging** - Manual review queue  
✅ **Hourly Reports** - Metrics on DMs, conversions, partnerships  

## 📋 Categories

| Category | Pattern | Response |
|----------|---------|----------|
| **Setup Help** | Installation, errors, confusion | Help guide + support link |
| **Newsletter** | Email signup, updates | Confirms addition to list |
| **Product Inquiry** | Pricing, features, purchase | Product overview + link |
| **Partnership** | Collaboration, sponsorship, affiliate | Flags for manual review |

## 🚀 Quick Start

### 1. Install Python Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Set Up YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select a project
3. Enable **YouTube Data API v3**
4. Create **OAuth 2.0 Desktop Application** credentials
5. Download JSON and save as `.cache/youtube-credentials.json`

**Note:** First run will prompt browser-based auth. Credentials are saved for future runs.

### 3. Test the System

```bash
# Test categorization logic
python3 .cache/youtube-dm-test.py

# Check generated files
cat .cache/youtube-dms.jsonl | jq .
```

### 4. Set Up Hourly Execution

**Option A: Using crontab (Linux/Mac)**

```bash
crontab -e
```

Add this line:
```
0 * * * * cd /Users/abundance/.openclaw/workspace && /usr/bin/python3 .cache/youtube-dm-monitor.py >> .cache/youtube-dm-monitor.log 2>&1
```

**Option B: Using macOS LaunchAgent**

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

## 📊 Sample Report Output

```
============================================================
YouTube DM Monitor Report - 2026-04-14 18:05:00
============================================================

📊 SUMMARY
  Total DMs processed:    8
  Auto-responses sent:    8
  Product inquiries:      3
  Partnership requests:   2

💡 PRODUCT INQUIRIES (Conversion Potential)
  • Carol White: What's your pricing? I'm interested in buying...
  • Grace Lee: Which product would you recommend for a small...
  • Henry Brown: How much does the premium plan cost per month...

🤝 PARTNERSHIPS (Flagged for Manual Review)
  • Diana Prince: Hey! I run a tech blog with 50k followers...
  • Frank Thomas: I'm a YouTube affiliate. Can we discuss an...

============================================================
```

## 📁 Files

```
.cache/
├── youtube-dm-monitor.py          # Main script
├── youtube-dm-test.py             # Testing script
├── youtube-credentials.json       # OAuth creds (create manually)
├── youtube-token.json             # Auth token (auto-generated)
├── youtube-dm-state.json          # Last check timestamp
├── youtube-dms.jsonl              # DM log (append-only)
├── youtube-dm-monitor.log         # Execution log
├── YOUTUBE-DM-SETUP.md            # Detailed setup guide
└── youtube-dm-monitor.cron        # Cron schedule reference
```

## 🔧 Customization

### Change Response Templates

Edit `RESPONSES` dict in `youtube-dm-monitor.py`:

```python
RESPONSES = {
    'setup_help': 'Your custom message here...',
    'newsletter': 'Your custom message here...',
    'product_inquiry': 'Your custom message here...',
    'partnership': 'Your custom message here...',
}
```

### Adjust Categorization Patterns

Edit `categorize_dm()` method to add/remove patterns:

```python
setup_patterns = [
    r'your pattern here',
    r'another pattern',
]
```

### Change Monitor Frequency

**Crontab examples:**
- Every 30 minutes: `*/30 * * * * ...`
- Every 2 hours: `0 */2 * * * ...`
- Daily at 9 AM: `0 9 * * * ...`
- Every weekday at 8 AM: `0 8 * * 1-5 ...`

## 📈 Analysis & Monitoring

### View Recent Activity

```bash
# Last 10 DMs
tail -10 .cache/youtube-dms.jsonl | jq .

# All product inquiries
cat .cache/youtube-dms.jsonl | jq 'select(.category == "Product inquiry")'

# Partnership requests (for follow-up)
cat .cache/youtube-dms.jsonl | jq 'select(.category == "Partnership")'
```

### Check Monitor Health

```bash
# View latest report
tail -20 .cache/youtube-dm-monitor.log

# Check last run
ls -lh .cache/youtube-dm-state.json
cat .cache/youtube-dm-state.json | jq .

# Verify cron is active (if using crontab)
crontab -l | grep youtube

# Or for LaunchAgent
launchctl list | grep youtube
```

### Example Analysis Script

```bash
#!/bin/bash
# Analyze this week's DMs

echo "=== This Week's DM Summary ==="
cat .cache/youtube-dms.jsonl | jq -s '
  group_by(.category) |
  map({
    category: .[0].category,
    count: length,
    responses_sent: map(select(.response_sent == true)) | length
  })
'

echo ""
echo "=== Product Inquiry Senders (Potential Customers) ==="
cat .cache/youtube-dms.jsonl | jq -r '
  select(.category == "Product inquiry") |
  [.timestamp, .sender, .text] |
  @csv
'
```

## 🛠️ Troubleshooting

### "Authentication failed"
- Delete `.cache/youtube-token.json` and re-run
- Verify OAuth scopes in `youtube-credentials.json`
- Check Google Cloud project has YouTube API enabled

### "No new DMs found"
- This is normal if no new DMs since last run
- Monitor continues to run on schedule
- Check `.cache/youtube-dm-state.json` for last check time

### "Script doesn't run on schedule"

**For crontab:**
```bash
# Verify it's in crontab
crontab -l

# Check if cron daemon is running
ps aux | grep cron

# View cron logs (macOS)
log stream --predicate 'process == "cron"'
```

**For LaunchAgent:**
```bash
# Verify it's loaded
launchctl list | grep youtube

# Check for errors
launchctl list com.youtube.dm-monitor

# View logs
tail -20 .cache/youtube-dm-monitor.log
```

### "API Rate Limits"

YouTube API provides 1M quota/day. At 1 call/hour = 24 calls/day (well within limits). Not an issue.

## 📝 Notes

- **Security**: Keep `youtube-credentials.json` safe (contains auth tokens)
- **Privacy**: DMs are logged locally only, never sent externally
- **Persistence**: Log file grows over time; archive periodically if needed
- **Customization**: Template responses and patterns are easy to adjust

## 🎓 Further Reading

- [YouTube Data API Docs](https://developers.google.com/youtube/v3)
- [Google Auth Docs](https://developers.google.com/identity/protocols/oauth2)
- [Python Google Client Library](https://github.com/googleapis/google-api-python-client)

---

## 📞 Support

For issues, customizations, or enhancements:

1. Check `.cache/youtube-dm-monitor.log` for error details
2. Review inline comments in `youtube-dm-monitor.py`
3. Test categorization with `python3 .cache/youtube-dm-test.py`
4. Verify API credentials and OAuth setup

---

**Version:** 1.0  
**Created:** 2026-04-14  
**Status:** ✅ Production Ready
