# YouTube Comment Monitor - Setup Guide

**Status:** 🚀 Ready to deploy  
**Cron Schedule:** Every 30 minutes  
**Current Time:** Thursday, April 16th, 2026 — 1:30 AM PST

## 📦 What's Installed

✅ **Script:** `.scripts/youtube-monitor.py` (1,100 lines)
✅ **Wrapper:** `.scripts/youtube-monitor.sh`
✅ **Log directory:** `.cache/` (auto-created)
✅ **Output files:**
   - `.cache/youtube-comments.jsonl` — all comments with metadata
   - `.cache/youtube-monitor-summary.json` — latest run stats
   - `.cache/youtube-monitor.log` — cron execution log

## 🔧 Setup Steps

### 1. Install Dependencies
```bash
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### 2. Set Up YouTube API Credentials

The monitor looks for credentials at:
```
~/.openclaw/credentials/youtube-api.json
```

**Option A: Service Account** (Recommended for automation)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable YouTube Data API v3
4. Create a Service Account:
   - Go to **Service Accounts** (in Credentials)
   - Click "Create Service Account"
   - Grant roles: **Editor** (for testing) or **YouTube API - YouTube Read Only** (production)
5. Create a JSON key and save to `~/.openclaw/credentials/youtube-api.json`
6. Share the channel with the service account email (or make the channel public)

**Option B: OAuth 2.0** (For user-specific access)
1. Create OAuth 2.0 credentials (Installed Application)
2. Save the JSON and run once to generate refresh token
3. The monitor will use the cached token

### 3. Install Cron Job

#### **Method A: Manual Setup** (If macOS crontab is finicky)
```bash
# Add to ~/.openclaw/crontab (create if doesn't exist):
*/30 * * * * /Users/abundance/.openclaw/workspace/.scripts/youtube-monitor.sh

# Install it:
crontab ~/.openclaw/crontab

# Verify:
crontab -l
```

#### **Method B: Using launchd** (macOS native)
Create `~/Library/LaunchAgents/com.openclaw.youtube-monitor.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.youtube-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/abundance/.openclaw/workspace/.scripts/youtube-monitor.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>StandardOutPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log</string>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.youtube-monitor.plist
launchctl list | grep youtube-monitor  # Verify it's loaded
```

## 🎯 What It Does

Every 30 minutes, the monitor:

1. **Fetches** recent comments from Concessa Obvius channel
2. **Categorizes** each new comment:
   - **Questions** (keywords: how, what, cost, tools, timeline, start)
   - **Praise** (keywords: amazing, inspiring, love, great, awesome)
   - **Spam** (crypto, bitcoin, nft, mlm, pyramid, forex, dropship)
   - **Sales** (partnership, collaboration, sponsor, brand deal, affiliate)

3. **Auto-responds** to:
   - Questions → Template response with resources & guidance
   - Praise → Thank you + engagement message

4. **Flags for Review:**
   - Sales inquiries (partnerships, collaborations)

5. **Logs Everything:**
   ```json
   {
     "timestamp": "2026-04-16T01:30:00",
     "video_id": "abc123xyz",
     "commenter": "John Doe",
     "text": "How do I get started?",
     "category": "questions",
     "response_status": "auto_responded",
     "response_template": "questions"
   }
   ```

## 📊 Reports

### Live Summary (every run)
```
📺 YouTube Comment Monitor - 2026-04-16T01:30:00
📥 Fetched 5 comments
  ✅ Auto-response queued for question by Jane
  ✅ Auto-response queued for praise by Bob
  🚩 Sales inquiry flagged from Alice
  🚫 Spam marked from Spam Bot

📊 Report (2026-04-16 01:30:00)
  Total processed: 3
  Questions: 1
  Praise: 1
  Spam: 1
  Sales (flagged): 1
  Auto-responses sent: 2
  Flagged for review: 1
```

### Historical Log
Check `.cache/youtube-monitor-summary.json` for the latest run stats.

## 🔍 Monitoring

### Check Latest Report
```bash
cat .cache/youtube-monitor-summary.json
```

### View All Comments
```bash
tail -20 .cache/youtube-comments.jsonl
```

### View Execution Log
```bash
tail -50 .cache/youtube-monitor.log
```

### Check If Cron is Running
```bash
# If using crontab:
crontab -l | grep youtube

# If using launchd:
launchctl list | grep youtube-monitor
ps aux | grep youtube-monitor
```

## 🚀 To Get Started Right Now

### Minimal Test Run
```bash
# Run once manually to test:
python3 .scripts/youtube-monitor.py
```

You'll see:
- ✅ If credentials are found
- ❌ If they're missing (with setup instructions)
- 📊 Comment processing stats

### Full Activation Checklist

- [ ] Install dependencies (`pip install google-api-...`)
- [ ] Set up YouTube API credentials
- [ ] Save credentials to `~/.openclaw/credentials/youtube-api.json`
- [ ] Test with manual run: `python3 .scripts/youtube-monitor.py`
- [ ] Verify output in `.cache/youtube-comments.jsonl`
- [ ] Install cron job (Method A or B above)
- [ ] Verify cron is running
- [ ] Check logs after 30 minutes

## 🎯 Channel

For the Concessa Obvius channel:
- **Channel ID:** `UCJa8b_2h5ztfGJ3F5Jqvswg` (configured in script)
- Edit the script if you need to monitor a different channel

## 📝 Templates

Modify response templates in `.scripts/youtube-monitor.py`:

```python
TEMPLATES = {
    "questions": "Your custom question response here...",
    "praise": "Your custom praise response here..."
}
```

## ⚠️ Troubleshooting

**"YouTube API libraries not available"**
→ Run: `pip install google-api-python-client google-auth-oauthlib google-auth-httplib2`

**"YouTube API credentials not found"**
→ Set up credentials at `~/.openclaw/credentials/youtube-api.json` (see Setup Steps)

**Cron not running**
→ Check with `crontab -l` or `launchctl list | grep youtube`
→ Verify script is executable: `chmod +x .scripts/youtube-monitor.sh`

**No comments being processed**
→ Channel might be set to private
→ Check if API credentials have access to the channel
→ Test manually: `python3 .scripts/youtube-monitor.py`

---

**Status:** Ready for deployment 🚀
**Scheduled:** Every 30 minutes
**Logs:** `.cache/youtube-monitor.log`
**Data:** `.cache/youtube-comments.jsonl`
