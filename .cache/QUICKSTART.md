# 🚀 YouTube Comment Monitor - Quick Start

## ✨ What You Just Got

A complete, production-ready system that:
- ✅ Runs every 30 minutes (via cron)
- 📝 Monitors YouTube comments in real-time
- 🏷️ Categorizes: Questions, Praise, Spam, Sales
- 🤖 Auto-responds to Questions & Praise
- 🚩 Flags Sales inquiries for your review
- 📊 Logs everything to JSONL format
- 📈 Generates analytics dashboards

## 🎯 30-Second Setup

```bash
# 1. Run setup
cd ~/.openclaw/workspace/.cache
./youtube-monitor-setup.sh

# 2. That's it! Cron is installed and running
```

The monitor will execute every 30 minutes automatically.

## 📊 Check Status Anytime

```bash
# View analytics dashboard
python3 ~/.openclaw/workspace/.cache/youtube-analytics.py

# View raw logs (latest 10)
tail -10 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .

# View cron execution logs
tail -f ~/.openclaw/workspace/.cache/youtube-monitor-cron.log

# View current state
cat ~/.openclaw/workspace/.cache/youtube-monitor-state.json | jq .
```

## ⚙️ Configuration

### Enable Real YouTube API (Recommended)

1. Go to: https://console.cloud.google.com
2. Create a project
3. Enable "YouTube Data API v3"
4. Create OAuth 2.0 credentials (Desktop app)
5. Download as JSON
6. Save to: `~/.openclaw/workspace/.cache/youtube-credentials.json`
7. Update channel ID in `youtube-monitor.py` (line ~42)

### Customize Responses

Edit `youtube-monitor.py` lines 63-73:

```python
TEMPLATE_RESPONSES = {
    "questions": [
        "Your response here...",
    ],
    "praise": [
        "Your thank you response...",
    ],
}
```

### Change Frequency

Edit cron:
```bash
crontab -e
```

Change `*/30 * * * *` to:
- `*/15` = every 15 minutes
- `0 * * * *` = every hour
- `0 9 * * *` = daily at 9 AM

## 📖 File Guide

```
.cache/
├── youtube-monitor.py           ← Main script (runs every 30 min)
├── youtube-analytics.py         ← Dashboard & reporting
├── youtube-monitor-setup.sh     ← One-time setup
├── youtube-credentials.json     ← YouTube API key (you add)
├── youtube-comments.jsonl       ← Comment log
├── youtube-monitor-state.json   ← Last processed ID
├── youtube-monitor-cron.log     ← Execution log
├── YOUTUBE-MONITOR-README.md    ← Full documentation
└── QUICKSTART.md                ← This file
```

## 🔍 Examples

### View all questions
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq 'select(.category=="questions")'
```

### View flagged sales inquiries
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq 'select(.response_status=="flagged_for_review")'
```

### Count auto-responses this week
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq 'select(.response_status=="auto_responded")' | wc -l
```

## 🆘 Troubleshooting

### "Cron job not running?"
```bash
# Check if it exists
crontab -l | grep youtube-monitor

# View macOS system logs
log stream --predicate 'eventMessage contains[cd] "youtube-monitor"' --level debug
```

### "Getting import errors?"
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### "Not detecting my channel?"
- Update `CHANNEL_ID` variable in `youtube-monitor.py`
- Find it: YouTube Settings → About → "Channel ID: UC..."
- Enable YouTube API credentials

## 📝 Next Steps

1. ✅ Setup is running (you're done!)
2. ⏳ Wait for first cron run (0-30 minutes)
3. 📊 Check analytics: `python3 youtube-analytics.py`
4. 🔑 (Optional) Add real YouTube API credentials
5. 📝 Customize responses to match your brand

## 💡 Tips

**Before adding API credentials:**
- The monitor runs in MOCK mode (sample data) so you can test everything
- All logs, responses, and workflows are real
- Perfect for customizing before connecting to YouTube

**Once you add API credentials:**
- Monitor will fetch real comments from your channel
- All existing code works as-is
- No changes needed except one JSON file

**To pause monitoring:**
```bash
crontab -e
# Comment out the youtube-monitor.py line with #
```

**To delete monitoring:**
```bash
crontab -e
# Remove the youtube-monitor.py line entirely
```

## ❓ Questions?

See `YOUTUBE-MONITOR-README.md` for full documentation.

---

You're all set! 🚀 The system is running and waiting for comments.
