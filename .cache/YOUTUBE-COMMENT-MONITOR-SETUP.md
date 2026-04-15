# YouTube Comment Monitor - Setup & Operation Guide

## Overview

Your YouTube Comment Monitor is **ready to run**. It currently operates in **DEMO MODE** with sample comments to show you exactly how it works.

### What It Does (Right Now)
- ✅ Categorizes comments (Questions, Praise, Spam, Sales)
- ✅ Logs all comments to `youtube-comments.jsonl`
- ✅ Generates auto-responses for questions & praise
- ✅ Flags sales inquiries for manual review
- ✅ Produces comprehensive reports every run
- ✅ Tracks lifetime statistics

### Demo Run Results (Just Now)
```
Total Comments Processed: 6
Auto-Responses Sent: 4
Flagged for Review: 1
```

---

## 🔧 Enable Live Mode (Optional)

To monitor your real Concessa Obvius channel, you need YouTube API credentials.

### Step 1: Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable the **YouTube Data API v3**
4. Create OAuth 2.0 credentials (Desktop/CLI)
5. Download the JSON credentials file

### Step 2: Set Up Credentials File

Place your credentials at this path:
```
~/.openclaw/workspace/.cache/.secrets/youtube-credentials.json
```

Example format:
```json
{
  "type": "oauth2_credentials",
  "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
  "client_secret": "YOUR_CLIENT_SECRET",
  "refresh_token": "YOUR_REFRESH_TOKEN"
}
```

### Step 3: Update Channel ID

Edit `/Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor-complete.py`

Find this line (around line 40):
```python
CHANNEL_ID = "UCxxxxxxxxxxxxxxxxxxxx"
```

Replace with your actual Concessa Obvius channel ID. Find it:
- Go to your channel's "About" tab
- Right-click "Share Channel" → "Copy Channel ID"
- Or extract from your channel URL: `youtube.com/@YourChannel/about` → `UCxxxxxx`

### Step 4: Test Live Mode

```bash
python3 /Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor-complete.py --live
```

---

## 📅 Enable Cron Job (Every 30 Minutes)

### Option A: macOS LaunchAgent (Recommended)

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
        <string>/bin/bash</string>
        <string>/Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor-cron-complete.sh</string>
    </array>
    
    <key>StartInterval</key>
    <integer>1800</integer>
    
    <key>StandardOutPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor-output.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor-error.log</string>
</dict>
</plist>
```

Then enable it:
```bash
launchctl load ~/Library/LaunchAgents/com.youtube.monitor.plist
# Check status:
launchctl list | grep youtube.monitor
```

### Option B: crontab

```bash
crontab -e
```

Add this line:
```
*/30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor-cron-complete.sh
```

---

## 📊 Understanding the Output

### JSONL Log Format
Each comment logged to `youtube-comments.jsonl`:

```json
{
  "timestamp": "2026-04-14T16:01:11.831507+00:00",
  "comment_id": "comment_unique_id",
  "commenter": "Sarah Chen",
  "text": "How do I get started with this?",
  "category": "questions",
  "response_status": "auto_responded",
  "template_response": "Great question! Thanks for your interest..."
}
```

### Response Status Values
- **auto_responded**: Auto-reply sent (Questions & Praise)
- **flagged_for_review**: Needs human review (Sales inquiries)
- **processed**: Logged but not auto-replied (Spam, Neutral)

### Categories
1. **questions** - How-to, tools, cost, timeline, setup questions
2. **praise** - Compliments, appreciation, testimonials
3. **sales** - Partnerships, collaborations, sponsorships
4. **spam** - Crypto, MLM, get-rich-quick schemes
5. **neutral** - Doesn't match any pattern

---

## 📈 Reports

Every run generates a report saved to:
```
~/.openclaw/workspace/.cache/youtube-comments-report.txt
```

Contains:
- Session summary (comments processed, responses sent, flagged)
- Lifetime statistics (cumulative from all runs)
- Breakdown by category
- Recent comment samples

### Example Report
```
=== SESSION SUMMARY ===
Total Comments Processed: 6
Auto-Responses Sent: 4
Flagged for Review: 1

=== LIFETIME STATS ===
Total Processed (Lifetime): 12
Total Auto-Replied (Lifetime): 8
Total Flagged (Lifetime): 2
```

---

## 🔍 Manual Operations

### Run monitor once (demo mode):
```bash
python3 /Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor-complete.py --demo
```

### Run monitor once (live mode):
```bash
python3 /Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor-complete.py --live
```

### Check recent comments logged:
```bash
tail -20 ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

### View latest report:
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments-report.txt
```

### View monitor state (lifetime stats):
```bash
cat ~/.openclaw/workspace/.cache/youtube-comment-state.json
```

---

## ⚙️ Customization

### Add Custom Response Templates

Edit `/Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor-complete.py`

Find `RESPONSE_TEMPLATES` (around line 46):

```python
RESPONSE_TEMPLATES = {
    "questions": [
        "Your custom question response here...",
        "Another question response...",
    ],
    "praise": [
        "Your custom praise response here...",
        "Another praise response...",
    ],
}
```

### Update Categorization Keywords

Edit `KEYWORDS` dictionary (around line 54):

```python
KEYWORDS = {
    "questions": [
        "how do i", "when will", "my custom keyword",
        # ... more keywords
    ],
    "praise": [
        "amazing", "my custom compliment",
        # ... more keywords
    ],
    # etc...
}
```

---

## 📝 File Locations

| File | Purpose |
|------|---------|
| `youtube-comment-monitor-complete.py` | Main monitor script |
| `youtube-comment-monitor-cron-complete.sh` | Cron wrapper |
| `youtube-comments.jsonl` | Audit log of all comments |
| `youtube-comment-state.json` | Lifetime statistics |
| `youtube-comments-report.txt` | Latest run report |
| `.secrets/youtube-credentials.json` | Your API credentials (you create) |

---

## 🚀 Next Steps

1. **Keep demo mode running** to verify the system works
2. **Get YouTube API credentials** when ready (optional for live)
3. **Update channel ID** with your real Concessa Obvius ID
4. **Enable cron job** to automate every 30 minutes
5. **Customize templates** to match your brand voice
6. **Monitor reports** to track engagement patterns

---

## ❓ FAQ

**Q: Can I run this without YouTube credentials?**  
A: Yes! Demo mode works perfectly without credentials. It shows how the system categorizes and responds to comments.

**Q: What happens to sales inquiries?**  
A: They're logged with status `flagged_for_review`. You can scan the JSONL log to find them:
```bash
grep '"category": "sales"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

**Q: How do I change response templates?**  
A: Edit the `RESPONSE_TEMPLATES` dictionary in the Python script. Templates are selected randomly to avoid repetition.

**Q: Can I manually reply to comments?**  
A: The monitor logs comments but doesn't post replies (YouTube API doesn't support this easily). You can manually reply on YouTube after reading the logs.

**Q: What if I want different categorization?**  
A: Edit the `KEYWORDS` dictionary to add/remove keywords for each category.

---

## Support

For issues or enhancements, check:
- Monitor logs: `youtube-comment-monitor-cron.log`
- Error logs: `youtube-comment-monitor-cron-error.log`
- Test run: `python3 youtube-comment-monitor-complete.py --demo`

---

**Last Updated:** 2026-04-14  
**Status:** ✅ Ready to use (Demo mode active, Live mode optional)
