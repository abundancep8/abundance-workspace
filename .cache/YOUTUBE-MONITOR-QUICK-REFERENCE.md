# 📺 YouTube Comment Monitor - Quick Reference Card

## 🚀 Setup (5 mins)

```bash
# 1. Install
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# 2. Get credentials
# → Go to console.cloud.google.com
# → Create project, enable YouTube Data API v3
# → Create OAuth client (Desktop)
# → Download JSON → save to ~/.openclaw/workspace/.cache/youtube-credentials.json

# 3. Update script
# Edit youtube-comment-monitor.py, line 45:
#   "channel_id": "UCyour_actual_id"

# 4. Test
cd ~/.openclaw/workspace
python3 .cache/youtube-comment-monitor.py
# → Browser opens for OAuth approval

# 5. Add to cron
crontab -e
# Add: */30 * * * * cd ~/.openclaw/workspace && python3 .cache/youtube-comment-monitor.py >> .cache/youtube-monitor.log 2>&1
```

---

## 📂 Files

| File | Purpose |
|------|---------|
| `youtube-comment-monitor.py` | Main script |
| `youtube-comment-monitor.sh` | Cron wrapper |
| `youtube-credentials.json` | OAuth client secret (YOU create) |
| `youtube-token.json` | Auth token (auto-created) |
| `youtube-comments.jsonl` | All comments logged here |
| `youtube-monitor-state.json` | Tracks what's been processed |
| `youtube-monitor.log` | Cron execution log |
| `youtube-monitor-report.txt` | Summary reports |

---

## 📊 Comment Categories

| Category | Pattern | Action | Review? |
|----------|---------|--------|---------|
| **Questions** | "How...", "What...", "cost", "tools", "timeline" | Auto-respond | ❌ |
| **Praise** | "amazing", "inspiring", "love", "thank you" | Auto-respond | ❌ |
| **Spam** | "crypto", "MLM", "get rich quick" | Log only | ❌ |
| **Sales** | "partnership", "collaboration", "sponsor" | Log & flag | ✅ |
| **Other** | Nothing matches | Log only | ❌ |

---

## 📝 Logs & Commands

```bash
# View all comments
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Pretty-print
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | python3 -m json.tool

# Filter by category
grep '"category": "questions"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Count by category
grep -o '"category": "[^"]*"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | sort | uniq -c

# View execution log
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log

# View reports
tail ~/.openclaw/workspace/.cache/youtube-monitor-report.txt

# Check if cron is running
crontab -l | grep youtube-comment-monitor
```

---

## 🔧 Customization

**Change response templates:**
```python
RESPONSES = {
    "questions": "Your custom response here: {answer}",
    "praise": "Thank you!",
}
```

**Add categorization rule:**
```python
"questions": [
    r"your custom pattern here",
]
```

**Change cron frequency:**
- Every 15 min: `*/15 * * * *`
- Every hour: `0 * * * *`
- Every 6 hours: `0 */6 * * *`

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| "Channel not found" | Check channel ID (youtube.com/channel/UCxxx) |
| "API quota exceeded" | Request quota increase in Google Cloud |
| "Auth failed" | Delete token: `rm ~/.openclaw/workspace/.cache/youtube-token.json` |
| "Cron not running" | Verify: `crontab -l` and check `.log` file |
| "No new comments" | Check if comments are enabled on channel |

---

## 🔐 Security Checklist

- [ ] Credentials.json NOT in git
- [ ] Token.json NOT shared
- [ ] Use `.gitignore` for `.cache/*`
- [ ] Rotate credentials every 6 months
- [ ] Keep Python dependencies updated

---

## 📈 Monitor Status

```bash
# What's happening right now?
tail -20 ~/.openclaw/workspace/.cache/youtube-monitor.log

# Latest report
tail -30 ~/.openclaw/workspace/.cache/youtube-monitor-report.txt

# How many comments processed?
wc -l ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Last run?
ls -lh ~/.openclaw/workspace/.cache/youtube-monitor-report.txt
```

---

## 🎯 What It Does Every 30 Minutes

1. ✅ Authenticate with YouTube API
2. ✅ Fetch 5 most recent videos from channel
3. ✅ Get 20 top comments from each video
4. ✅ Check if already processed (state file)
5. ✅ Categorize each new comment
6. ✅ Auto-respond to questions & praise
7. ✅ Flag sales inquiries
8. ✅ Log everything to JSONL
9. ✅ Generate report with stats
10. ✅ Update state file for next run

---

## 📞 Support

- Full guide: `youtube-comment-monitor-setup.md`
- README: `YOUTUBE-MONITOR-README.md`
- Config example: `youtube-monitor-config.example.json`
- Log example: `youtube-comments.example.jsonl`

---

**Cron Job:** 114e5c6d-ac8b-47ca-a695-79ac31b5c076  
**Created:** 2026-04-18  
**Next Run:** Every 30 minutes automatically
