# YouTube Comment Monitor - Cron Deployment Summary

**Task ID:** `114e5c6d-ac8b-47ca-a695-79ac31b5c076`  
**Task Name:** YouTube Comment Monitor (Every 30 minutes)  
**Channel:** Concessa Obvius  
**Deployed:** 2026-04-20 22:00 UTC / 3:00 PM PT  
**Status:** ✅ Ready to Deploy

---

## 📋 What Was Created

### 1. **Main Monitor Scripts**

| File | Purpose |
|------|---------|
| `youtube-monitor.js` | Basic monitor (placeholder API) |
| `youtube-monitor-api.js` | Full production monitor with YouTube API integration |
| `youtube-monitor-config.json` | Centralized configuration |

### 2. **Setup & Documentation**

| File | Purpose |
|------|---------|
| `YOUTUBE_MONITOR_SETUP.md` | Complete setup guide with credentials |
| `YOUTUBE_COMMENT_MONITOR_CRON_DEPLOYMENT.md` | This file |

### 3. **Logging & State**

| File | Purpose |
|------|---------|
| `youtube-comments.jsonl` | Comment log (JSON Lines format) |
| `youtube-monitor-state.json` | Persistent state (last checked, counts) |

---

## 🚀 Deployment Steps

### Step 1: Set YouTube API Key
```bash
export YOUTUBE_API_KEY="your-api-key-from-google-cloud"
```

Or add to `~/.zshrc` for persistence:
```bash
echo 'export YOUTUBE_API_KEY="your-api-key"' >> ~/.zshrc
source ~/.zshrc
```

### Step 2: Update Channel ID
Edit `.cache/youtube-monitor-config.json`:
```json
{
  "channel": {
    "name": "Concessa Obvius",
    "channelId": "UC_YOUR_CHANNEL_ID_HERE"
  }
}
```

### Step 3: Test the Monitor
```bash
cd ~/.openclaw/workspace
node .cache/youtube-monitor-api.js
```

Expected output:
```
[2026-04-20T22:00:00Z] Starting YouTube comment monitor...
Found 50 recent videos
Video abc123: 15 comment threads
✓ [questions] "How do I start?"
✓ [praise] "This is amazing..."
⚠ [sales] "Partnership opportunity"

============================================================
YOUTUBE COMMENT MONITOR REPORT
============================================================
Channel: Concessa Obvius
Timestamp: 2026-04-20T22:00:00Z
New comments processed: 20
Total comments processed (all-time): 20
Auto-responses sent: 8
Flagged for review: 3
```

### Step 4: Register with OpenClaw Cron

**Option A: Via OpenClaw CLI**
```bash
openclaw cron register \
  --name "youtube-comment-monitor" \
  --schedule "*/30 * * * *" \
  --command "node ~/.openclaw/workspace/.cache/youtube-monitor-api.js" \
  --env YOUTUBE_API_KEY="your-api-key"
```

**Option B: Via Crontab**
```bash
# Edit crontab
crontab -e

# Add this line:
*/30 * * * * cd ~/.openclaw/workspace && YOUTUBE_API_KEY="your-key" node .cache/youtube-monitor-api.js >> .cache/youtube-monitor-cron.log 2>&1
```

**Option C: Via macOS launchd**
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
        <string>/usr/bin/node</string>
        <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor-api.js</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>YOUTUBE_API_KEY</key>
        <string>your-api-key</string>
    </dict>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>StandardErrorPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor-launchd-error.log</string>
    <key>StandardOutPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor-launchd.log</string>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.youtube-monitor.plist
```

---

## 🎯 Comment Categorization

### Category 1: Questions ❓
**Pattern:** "how do i", "how can i", "cost", "price", "timeline", "tools", "start"  
**Auto-Response:** YES  
**Response Templates:**
- "Thanks for your question! I cover this in detail in our resources—check the linked guide in the channel description."
- "Great question! This is addressed in our latest video. Watch for the full breakdown."
- "Happy to help! Our FAQ section covers this. See the pinned comment for the link."

### Category 2: Praise ⭐
**Pattern:** "amazing", "inspiring", "love it", "thank you", "awesome", "excellent"  
**Auto-Response:** YES  
**Response Templates:**
- "Thank you so much! Your support means everything. More coming soon."
- "Comments like this fuel the mission. Grateful for you."
- "This is exactly why we do this. Thank you for believing in it."

### Category 3: Spam 🚫
**Pattern:** "crypto", "bitcoin", "nft", "mlm", "forex", "dropshipping", "click here"  
**Auto-Response:** NO  
**Action:** Logged only

### Category 4: Sales 💼
**Pattern:** "partnership", "collaboration", "sponsor", "advertise", "affiliate", "brand deal"  
**Auto-Response:** NO  
**Action:** Flagged for manual review

### Category 5: General 📝
**Pattern:** Anything else  
**Auto-Response:** NO  
**Action:** Logged only

---

## 📊 Log Format

Each comment is stored in JSON Lines format (`.cache/youtube-comments.jsonl`):

```json
{
  "timestamp": "2026-04-20T22:00:00.123Z",
  "commenter": "John Doe",
  "text": "How do I get started with your course?",
  "category": "questions",
  "response_status": "auto-responded",
  "autoResponseText": "Thanks for your question! I cover this in detail..."
}
```

**Valid response_status values:**
- `none` — No action taken
- `auto-responded` — Automatic reply sent
- `flagged-for-review` — Flagged for manual review
- `response-failed` — Attempted but failed
- `general` — General comment logged

---

## 📈 Reports Generated

At each run, the monitor outputs:

```
============================================================
YOUTUBE COMMENT MONITOR REPORT
============================================================
Channel: Concessa Obvius
Timestamp: 2026-04-20T22:00:00Z
New comments processed: 20
Total comments processed (all-time): 1,234
Auto-responses sent: 8
Total auto-responses (all-time): 456
Flagged for review: 3
Total flagged (all-time): 78
Log file: .cache/youtube-comments.jsonl
============================================================
```

**Tracking:** All stats are cumulative and persisted in `.cache/youtube-monitor-state.json`.

---

## 🔍 Querying the Logs

### View Recent Comments
```bash
tail -20 .cache/youtube-comments.jsonl | jq '.'
```

### Count by Category
```bash
echo "Questions:" && grep '"category":"questions"' .cache/youtube-comments.jsonl | wc -l
echo "Praise:" && grep '"category":"praise"' .cache/youtube-comments.jsonl | wc -l
echo "Spam:" && grep '"category":"spam"' .cache/youtube-comments.jsonl | wc -l
echo "Sales:" && grep '"category":"sales"' .cache/youtube-comments.jsonl | wc -l
```

### Extract Flagged Sales
```bash
grep '"category":"sales"' .cache/youtube-comments.jsonl | jq '.' > flagged-sales.json
```

### Count Auto-Responses
```bash
grep '"response_status":"auto-responded"' .cache/youtube-comments.jsonl | wc -l
```

---

## ⚙️ Configuration Options

Edit `.cache/youtube-monitor-config.json`:

### Add New Response Template
```json
{
  "responses": {
    "questions": [
      "New custom response here..."
    ]
  }
}
```

### Add New Category
```json
{
  "categories": {
    "feedback": {
      "patterns": ["bug", "issue", "broken", "error"],
      "autoRespond": false,
      "action": "flag"
    }
  }
}
```

### Adjust Check Interval
```json
{
  "channel": {
    "checkInterval": 30  // minutes
  }
}
```

---

## 🔐 Security Checklist

- [ ] API key stored in environment variable (not committed to git)
- [ ] Config file does not contain sensitive data
- [ ] Logs contain public comments only
- [ ] State file has no sensitive data
- [ ] OAuth setup (if needed for reply posting) uses secure token storage

---

## 📝 Manual Testing

```bash
# Navigate to workspace
cd ~/.openclaw/workspace

# Run monitor directly
node .cache/youtube-monitor-api.js

# Check logs immediately after
tail -20 .cache/youtube-comments.jsonl

# View current state
cat .cache/youtube-monitor-state.json | jq '.'
```

---

## 🐛 Troubleshooting

### "YOUTUBE_API_KEY not set"
```bash
export YOUTUBE_API_KEY="your-key"
# Or add to ~/.zshrc
```

### "API error: 403"
- Verify API key is valid in Google Cloud Console
- Confirm YouTube Data API v3 is enabled
- Check quota limits haven't been exceeded

### "Channel not found (404)"
- Verify `channelId` in config is correct
- Ensure channel is public
- Try looking up channel ID via: `https://www.youtube.com/oembed?url=https://www.youtube.com/@ConcessaObvious&format=json`

### No comments processed
- Run manually to test: `node .cache/youtube-monitor-api.js`
- Check `.cache/youtube-monitor-state.json` for last successful run
- Verify channel has recent comments
- Check API quota limits

---

## 📅 Cron Frequency: Every 30 Minutes

```
┌─────────────────── minute (0-59)
│ ┌───────────────── hour (0-23)
│ │ ┌─────────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌─────────── day of week (0-6) (Sunday-Saturday)
│ │ │ │ │
*/30 * * * * <command>
```

**Runs at:** 00, 30 mins every hour, every day.

---

## 🚀 Next Steps

1. **Get API Key** from Google Cloud Console
2. **Update config** with your channel ID
3. **Test manually** with `node .cache/youtube-monitor-api.js`
4. **Register cron** via OpenClaw or system cron
5. **Monitor logs** at `.cache/youtube-comments.jsonl`
6. **Review flagged comments** and adjust templates as needed

---

**Files Deployed:**
- ✅ `youtube-monitor-api.js` (production ready)
- ✅ `youtube-monitor.js` (basic fallback)
- ✅ `youtube-monitor-config.json` (centralized config)
- ✅ `youtube-comments.jsonl` (log file)
- ✅ `youtube-monitor-state.json` (state tracking)
- ✅ `YOUTUBE_MONITOR_SETUP.md` (detailed guide)

**Status:** Ready for deployment. Awaiting API key and channel ID configuration.

---

**Last Updated:** 2026-04-20 22:00 UTC  
**Task ID:** 114e5c6d-ac8b-47ca-a695-79ac31b5c076
