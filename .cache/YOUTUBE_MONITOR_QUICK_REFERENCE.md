# YouTube Comment Monitor - Quick Reference

**Task:** Monitor Concessa Obvius channel every 30 minutes  
**Status:** ✅ Ready to deploy

---

## 🚀 One-Time Setup

```bash
# 1. Set API key
export YOUTUBE_API_KEY="your-key-from-google-cloud"

# 2. Update channel ID in config
nano ~/.openclaw/workspace/.cache/youtube-monitor-config.json

# 3. Test
cd ~/.openclaw/workspace
node .cache/youtube-monitor-api.js
```

## ⏰ Register Cron Job

**OpenClaw:**
```bash
openclaw cron register \
  --name "youtube-comment-monitor" \
  --schedule "*/30 * * * *" \
  --command "node ~/.openclaw/workspace/.cache/youtube-monitor-api.js" \
  --env YOUTUBE_API_KEY="your-key"
```

**Or Crontab:**
```bash
*/30 * * * * cd ~/.openclaw/workspace && YOUTUBE_API_KEY="your-key" node .cache/youtube-monitor-api.js >> .cache/youtube-monitor-cron.log 2>&1
```

---

## 📊 Check Status

```bash
# View latest report
tail -15 .cache/youtube-comments.jsonl | jq '.'

# View state (totals)
cat .cache/youtube-monitor-state.json | jq '.'

# Count comments by category
echo "Q:" $(grep '"questions"' .cache/youtube-comments.jsonl | wc -l)
echo "P:" $(grep '"praise"' .cache/youtube-comments.jsonl | wc -l)
echo "S:" $(grep '"sales"' .cache/youtube-comments.jsonl | wc -l)
```

---

## 🎯 Categories & Auto-Responses

| Category | Pattern | Auto-Respond | Examples |
|----------|---------|:------------:|----------|
| **Questions** | "how", "cost", "tools", "timeline" | ✅ | How do I start? |
| **Praise** | "amazing", "love", "thank you", "awesome" | ✅ | This is incredible! |
| **Spam** | "crypto", "nft", "mlm", "dropshipping" | ❌ | Buy Bitcoin now! |
| **Sales** | "partnership", "sponsor", "advertise" | ⚠️ Flagged | Let's collaborate |
| **General** | Everything else | ❌ | Just logged |

---

## 📁 Files

```
.cache/
├── youtube-monitor-api.js          # Main monitor (production)
├── youtube-monitor.js              # Basic fallback
├── youtube-monitor-config.json     # Configuration
├── youtube-comments.jsonl          # Comment log
├── youtube-monitor-state.json      # Persistent state
├── YOUTUBE_MONITOR_SETUP.md        # Full setup guide
└── YOUTUBE_COMMENT_MONITOR_CRON_DEPLOYMENT.md  # Deployment details
```

---

## 🔧 Customize Responses

Edit `youtube-monitor-config.json`:

```json
{
  "responses": {
    "questions": [
      "Custom response 1",
      "Custom response 2"
    ],
    "praise": [
      "Thank you!",
      "Grateful!"
    ]
  }
}
```

---

## 📝 Log Format

Each entry (JSONL):
```json
{
  "timestamp": "2026-04-20T22:00:00Z",
  "commenter": "Name",
  "text": "Comment text",
  "category": "questions|praise|spam|sales|general",
  "response_status": "auto-responded|flagged-for-review|none",
  "autoResponseText": "..."
}
```

---

## ✅ Check Health

```bash
# Last run
stat -f "%Sm" ~/.openclaw/workspace/.cache/youtube-monitor-state.json

# Active?
ps aux | grep youtube-monitor

# Cron active?
launchctl list | grep youtube-monitor
# Or: crontab -l | grep youtube-monitor
```

---

## 🐛 Common Issues

| Issue | Fix |
|-------|-----|
| "YOUTUBE_API_KEY not set" | `export YOUTUBE_API_KEY="key"` |
| "API error 403" | Check API key & enable YouTube Data API v3 |
| "Channel not found" | Verify `channelId` in config |
| No comments processed | Run manually, check for new comments on channel |

---

## 📞 Support Files

- **Setup:** `YOUTUBE_MONITOR_SETUP.md`
- **Deploy:** `YOUTUBE_COMMENT_MONITOR_CRON_DEPLOYMENT.md`
- **Config:** `youtube-monitor-config.json`
- **Logs:** `youtube-comments.jsonl`
- **State:** `youtube-monitor-state.json`

---

**Run once manually to verify everything works before scheduling!**

```bash
cd ~/.openclaw/workspace && node .cache/youtube-monitor-api.js
```

Expected output: Report with comment count, responses sent, flagged items.

---

Created: 2026-04-20 22:00 UTC
