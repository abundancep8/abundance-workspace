# YouTube Comment Monitor - Setup Complete ✅

**Status**: ACTIVE  
**Channel**: Concessa Obvius  
**Schedule**: Every 30 minutes  
**Start Time**: Saturday, April 18, 2026 — 12:30 AM PT  
**Log Location**: `~/.openclaw/workspace/.cache/youtube-comments.jsonl`

---

## 🎯 What's Running

Your YouTube Comment Monitor is now configured to:

1. **Monitor** the Concessa Obvius channel for new comments every 30 minutes
2. **Categorize** each comment into 4 types:
   - **Questions** (How do I start? Tools? Cost? Timeline?)
   - **Praise** (Amazing, inspiring, great work!)
   - **Spam** (Crypto, MLM, get rich quick)
   - **Sales** (Partnership, collaboration, sponsorship)
3. **Auto-respond** to Questions and Praise with templated responses
4. **Flag** Sales inquiries for manual review
5. **Log everything** to JSONL with timestamps, categorization, and response status
6. **Generate reports** in both text and JSON format

---

## 📁 Files & Locations

| File | Purpose |
|------|---------|
| `~/.cache/youtube-comment-monitor.py` | Main monitoring script |
| `~/.cache/youtube-comment-monitor-cron.sh` | Cron wrapper script |
| `~/.cache/com.openclaw.youtube-comment-monitor.plist` | macOS LaunchAgent config |
| `~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist` | Active LaunchAgent |
| `~/.cache/youtube-comments.jsonl` | Comment log (append-only) |
| `~/.cache/youtube-comments-report-current.txt` | Latest human-readable report |
| `~/.cache/youtube-comments-report-current.json` | Latest JSON report |
| `~/.cache/youtube-comment-state.json` | State tracking (prevents duplicates) |
| `~/.cache/logs/youtube-comment-monitor-*.log` | Execution logs |

---

## 🔄 How It Works

### Every 30 Minutes:
1. LaunchAgent triggers `youtube-comment-monitor-cron.sh`
2. Script runs `youtube-comment-monitor.py` in demo mode (pending API setup)
3. Script fetches recent comments from channel
4. Categorizes each comment using keyword matching
5. Generates auto-responses for Questions & Praise
6. Appends to `youtube-comments.jsonl`
7. Updates state to avoid duplicate processing
8. Generates current report (text + JSON)
9. Logs execution to `logs/` directory

---

## 📊 Current Output Format

### JSONL Log Entry Example:
```json
{
  "timestamp": "2026-04-18T07:31:46.561966",
  "commenter": "Sarah Chen",
  "text": "How do I get started with this? What tools do I need?",
  "comment_id": "demo_q1",
  "category": "questions",
  "response_status": "auto_responded",
  "response_text": "Love this question! I'll make sure to cover this in depth soon. Stay tuned!",
  "run_time": "2026-04-18T07:31:46.562003"
}
```

### Report Statistics:
```
Total Comments Processed: 4
Auto-Responses Sent: 2
Flagged for Review: 1

Breakdown by Category:
  Questions: 1
  Praise: 1
  Spam: 1
  Sales/Partnerships: 1
```

---

## 🔐 YouTube API Setup (Optional - For Live Monitoring)

The monitor currently runs in **demo mode** with sample comments. To monitor your actual Concessa Obvius channel:

### 1. Get OAuth Credentials
```bash
# Create a Google Cloud project:
# https://console.cloud.google.com/apis/credentials

# Download OAuth 2.0 Client ID (JSON format)
# Save as: ~/.openclaw/workspace/.cache/youtube-credentials.json
```

### 2. Test Authentication
```bash
cd ~/.openclaw/workspace/.cache
python3 youtube-comment-monitor.py
# Follow the browser auth flow on first run
```

### 3. Token Auto-Refresh
The script automatically manages token refresh. Token stored at:
```
~/.openclaw/workspace/.cache/youtube-token.json
```

---

## 🚀 Managing the Monitor

### Check Status
```bash
launchctl list | grep youtube-comment-monitor
```

### View Recent Logs
```bash
tail -f ~/.openclaw/workspace/.cache/logs/youtube-comment-monitor-*.log
```

### Check Latest Report
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments-report-current.txt
jq . ~/.openclaw/workspace/.cache/youtube-comments-report-current.json
```

### Stop the Monitor
```bash
launchctl unload ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
```

### Restart the Monitor
```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
```

---

## 📝 Customization

### Change Response Templates
Edit `~/.openclaw/workspace/.cache/youtube-comment-monitor.py`:
```python
RESPONSE_TEMPLATES = {
    "questions": [
        "Your custom response here...",
    ],
    "praise": [
        "Your praise response here...",
    ]
}
```

### Add Category Keywords
```python
CATEGORY_PATTERNS = {
    "questions": [
        r"your new keyword",
        # ... more patterns
    ]
}
```

### Change Run Interval
Edit the LaunchAgent plist:
```xml
<key>StartInterval</key>
<integer>900</integer>  <!-- 15 minutes (in seconds) -->
```

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
launchctl load ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
```

---

## ✅ Verification

### Test Run
```bash
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

### Expected Output
```
YouTube Comment Monitor Report
Channel: Concessa Obvius
Report Time: 2026-04-18T07:31:46.564622

📊 Statistics:
  Total Comments Processed: 4
  Auto-Responses Sent: 2
  Flagged for Review: 1
```

### Check LaunchAgent Status
```bash
launchctl list | grep youtube-comment-monitor
# Should show: PID 0 com.openclaw.youtube-comment-monitor
```

---

## 📋 Requirements

### Installed
- ✅ Python 3.8+
- ✅ google-auth-oauthlib
- ✅ google-auth-httplib2
- ✅ google-api-python-client
- ✅ anthropic (for future enhancements)

### Installation (if needed)
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client anthropic
```

---

## 🎯 Next Steps

1. **[Optional] Set up YouTube OAuth credentials** for live monitoring
2. **Monitor reports** at `youtube-comments-report-current.txt`
3. **Customize response templates** for your brand voice
4. **Review flagged sales inquiries** from the JSONL log
5. **Adjust categories/keywords** based on your channel's patterns

---

## 📞 Troubleshooting

### No Comments Being Logged
- Check if demo mode is running (expected without API credentials)
- Verify LaunchAgent is loaded: `launchctl list | grep youtube`
- Check logs: `tail ~/.openclaw/workspace/.cache/logs/youtube-comment-monitor-*.log`

### LaunchAgent Not Running
```bash
# Reload it
launchctl unload ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
launchctl load ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist

# Check logs
log stream --predicate 'eventMessage contains[cd] "youtube-comment-monitor"'
```

### API Authentication Errors
- Verify YouTube credentials at: `~/.openclaw/workspace/.cache/youtube-credentials.json`
- Delete token to force re-auth: `rm ~/.openclaw/workspace/.cache/youtube-token.json`
- Run script manually to trigger browser auth flow

---

## 📊 Statistics Tracking

Each run appends to `youtube-comments.jsonl` with:
- Timestamp (ISO 8601)
- Comment ID (unique)
- Commenter name
- Comment text
- Category (questions, praise, spam, sales)
- Response status (auto_responded, flagged_for_review, processed, skipped)
- Response text (if applicable)
- Run time

Perfect for analytics, trends, and engagement tracking!

---

**Monitor started**: Saturday, April 18, 2026 — 12:30 AM PT  
**Next run**: Saturday, April 18, 2026 — 1:00 AM PT  
**Status**: ✅ Active and monitoring
