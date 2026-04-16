# 🎬 YouTube Comment Monitor

**Automated comment management for the Concessa Obvius YouTube channel.**

## Quick Start

### 1️⃣ Install Dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2️⃣ Get API Credentials
Follow **YOUTUBE-SETUP.md** to get your API key or OAuth credentials.

### 3️⃣ Configure
Edit `youtube-monitor-config.json`:
```json
{
  "channel_id": "UCxxxxxxxxxx",
  "api_key": "YOUR_KEY_HERE",
  "auto_respond_enabled": true
}
```

### 4️⃣ Test
```bash
python3 youtube-monitor-integrated.py --debug
```

### 5️⃣ Deploy
Cron job will run automatically every 30 minutes. Check logs:
```bash
tail -50 youtube-monitor-stats.jsonl | jq .
```

---

## 📁 Files

| File | Purpose |
|------|---------|
| `youtube-monitor-integrated.py` | **Main script** — Run this |
| `youtube-api.py` | YouTube API integration |
| `youtube-monitor-config.json` | Configuration (API key, channel, templates) |
| `youtube-comments.jsonl` | Comment log (one JSON per line) |
| `youtube-monitor-stats.jsonl` | Run statistics |
| `youtube-monitor-state.json` | Internal state (processed IDs, last checked) |
| `YOUTUBE-SETUP.md` | Detailed setup guide |

---

## 🎯 What It Does

**Every 30 minutes:**

1. **Fetch** new comments from the Concessa Obvius channel
2. **Categorize** each comment:
   - ❓ **Questions** → auto-respond
   - 👏 **Praise** → auto-respond
   - 🚫 **Spam** → skip
   - 🚩 **Sales** → flag for review
   - 📝 **Other** → log only
3. **Respond** automatically to questions and praise
4. **Flag** partnership/sponsorship inquiries for manual review
5. **Log** everything with timestamps
6. **Report** stats: total processed, auto-responses, flagged items

---

## 📊 Example Report

```
============================================================
📊 YouTube Comment Monitor Report
============================================================
Time: 2026-04-16T07:00:00

✅ Processed: 12 comments
✉️  Auto-responses: 8
🚩 Flagged for review: 2

📈 Breakdown by category:
   ❓ Question: 5
   👏 Praise: 3
   🚫 Spam: 2
   🚩 Sales: 2
============================================================
```

---

## 📝 Log Format

**youtube-comments.jsonl** (one comment per line):
```json
{
  "timestamp": "2026-04-16T07:00:00",
  "comment_id": "xyz789",
  "commenter": "John Doe",
  "text": "How do I get started with this?",
  "category": "question",
  "response_status": "auto_responded",
  "likes": 5,
  "video_id": "dQw4w9WgXcQ"
}
```

**youtube-monitor-stats.jsonl** (one report per run):
```json
{
  "timestamp": "2026-04-16T07:00:00",
  "total_processed": 12,
  "auto_responses_sent": 8,
  "flagged_for_review": 2,
  "by_category": {
    "question": 5,
    "praise": 3,
    "spam": 2,
    "sales": 2,
    "other": 0
  }
}
```

---

## 🔧 Customization

### Custom Response Templates

Edit `youtube-monitor-config.json`:

```json
"response_templates": {
  "question": "Great question! 🤔 Check out our guide: [LINK]\n\nLet me know if you need more help!",
  "praise": "Wow, thank you! 🙏 Your support means everything to us!"
}
```

### Adjust Categories

Edit `CATEGORY_PATTERNS` in `youtube-monitor-integrated.py` to add/modify patterns:

```python
"question": [
    r"how\s+do",
    r"cost\s*\?",
    # Add more patterns here
]
```

### Change Check Frequency

The cron schedule (every 30 min) is set in OpenClaw config or system crontab.

---

## 🐛 Troubleshooting

### "API key invalid"
- Verify key in `youtube-monitor-config.json`
- Check YouTube Data API v3 is enabled in Google Cloud Console
- Keys may take a few minutes to activate

### "Channel not found"
- Ensure `channel_id` is correct
- Format should be: `UCxxxxxxxxxx` (starts with UC)
- Try: `python3 youtube-api.py` to auto-lookup

### "Permission denied"
- Using API key? It's read-only. Need OAuth 2.0 or Service Account for posting replies.
- See YOUTUBE-SETUP.md for credential setup

### "No comments fetched"
- Check if YouTube API libraries are installed
- Verify channel has recent videos
- Make sure comments are enabled on videos
- Check `youtube-monitor-state.json` for `last_checked` timestamp

### Debug Mode
```bash
python3 youtube-monitor-integrated.py --debug
```

---

## 📊 Monitoring & Analytics

### Recent Activity
```bash
tail -5 youtube-monitor-stats.jsonl | jq .
```

### All Comments (Formatted)
```bash
jq . youtube-comments.jsonl
```

### Questions Asked
```bash
grep '"question"' youtube-comments.jsonl | wc -l
```

### Flagged for Review
```bash
grep '"flagged_for_review"' youtube-comments.jsonl | jq .
```

### Auto-Responses Sent
```bash
grep '"auto_responded"' youtube-comments.jsonl | wc -l
```

### Most Liked Comments
```bash
jq -s 'sort_by(.likes) | reverse | .[0:10]' youtube-comments.jsonl
```

---

## 🔒 Security

⚠️ **Never commit API keys or credentials!**

- Keep API keys in `youtube-monitor-config.json` (in `.cache/` — excluded from git)
- Use environment variables: `YOUTUBE_API_KEY`, `YOUTUBE_CREDENTIALS_FILE`
- Use service accounts for production
- Rotate credentials periodically

---

## 🚀 Advanced

### Email Alerts for Flagged Comments
```bash
# Add to crontab after monitor runs
*/30 * * * * grep '"flagged_for_review"' .cache/youtube-comments.jsonl | tail -1 | mail -s "New Sales Inquiry" admin@example.com
```

### Dashboard with Daily Summaries
```bash
# Aggregate daily stats
jq -s 'group_by(.timestamp[:10]) | map({date: .[0].timestamp[:10], total: map(.total_processed) | add})' .cache/youtube-monitor-stats.jsonl
```

### Slack Notifications
```bash
# Post stats to Slack webhook
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"📊 YouTube Monitor: 12 comments, 8 auto-responses, 2 flagged\"}" \
  $SLACK_WEBHOOK_URL
```

---

## 📞 Support

- **Setup issues?** See YOUTUBE-SETUP.md
- **Code errors?** Run with `--debug` flag
- **Google Cloud issues?** Check [Google Cloud Console](https://console.cloud.google.com/)
- **YouTube API docs?** [YouTube Data API Reference](https://developers.google.com/youtube/v3)

---

**Last updated:** 2026-04-16  
**Monitor interval:** Every 30 minutes  
**Status:** ✅ Ready to deploy
