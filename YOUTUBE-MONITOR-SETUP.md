# YouTube Comment Monitor - Complete Setup

## 📦 What Was Created

A fully-automated YouTube comment monitoring system for the **Concessa Obvius** channel that:

✅ Monitors for new comments every 30 minutes  
✅ Categorizes comments into 4 types  
✅ Auto-responds to Questions and Praise  
✅ Flags Sales/Partnership offers for review  
✅ Logs everything to JSONL for analysis  
✅ Integrates with cron for 24/7 automation  

## 📁 Files Delivered

### Scripts
- **`scripts/youtube-comment-monitor.py`** — Main monitoring engine (11.8 KB)
- **`scripts/youtube-monitor-cron.sh`** — Cron wrapper script (1 KB)
- **`scripts/youtube-monitor-status.sh`** — Status reporting tool (4.3 KB)

### Documentation
- **`scripts/QUICKSTART.md`** — 5-minute setup guide
- **`scripts/YOUTUBE-MONITOR-README.md`** — Full documentation (7.1 KB)
- **`scripts/youtube-monitor-setup.md`** — Detailed setup instructions (3.6 KB)

### Config & Examples
- **`.env.youtube-example`** — Environment variable template
- **`.cache/youtube-comments.jsonl.example`** — Sample comment log
- **`.cache/youtube-review.txt.example`** — Sample review queue

## 🎯 How It Works

```
Every 30 minutes (automated by cron):

1. FETCH new comments from channel videos
2. CATEGORIZE each comment:
   • Category 1: Questions (how, cost, timeline, tools)
   • Category 2: Praise (amazing, inspiring, great, love)
   • Category 3: Spam (crypto, MLM, forex) — filtered
   • Category 4: Sales/Partnerships — flagged for review

3. AUTO-RESPOND:
   • Questions → Template: "Thanks for the question! [details]"
   • Praise → Template: "Thank you so much! 💙"
   • Sales → Flag in review queue
   • Spam → Ignore

4. LOG all comments to: .cache/youtube-comments.jsonl
   Format: {timestamp, author, text, category, response_status}

5. REPORT:
   • Total processed
   • Auto-responses sent
   • Flagged for manual review
   • Spam filtered
```

## 🚀 Getting Started (5 Minutes)

### 1. Install Dependencies
```bash
pip install google-auth-oauthlib google-api-python-client
```

### 2. Get YouTube API Credentials
- Visit: https://console.cloud.google.com/
- Create project
- Enable "YouTube Data API v3"
- Create "API Key" credential
- Copy your API Key

### 3. Find Your Channel ID
- Go to your YouTube channel
- Copy ID from URL: `https://www.youtube.com/channel/UCxxxxxxxxxx`

### 4. Set Environment Variables
```bash
export YOUTUBE_API_KEY="your-key-here"
export YOUTUBE_CHANNEL_ID="UCxxxxxxxxxx"
```

Or create `.env` file:
```bash
cp .env.youtube-example .env
# Edit .env with your credentials
```

### 5. Test the Script
```bash
python scripts/youtube-comment-monitor.py
```

### 6. Install Cron Job
```bash
crontab -e
```

Add this line:
```
*/30 * * * * /Users/abundance/.openclaw/workspace/scripts/youtube-monitor-cron.sh
```

## 📊 Output & Monitoring

### View Status
```bash
bash scripts/youtube-monitor-status.sh
```

### View Recent Comments
```bash
tail -5 .cache/youtube-comments.jsonl | jq .
```

### Review Flagged Comments
```bash
cat .cache/youtube-review.txt
```

### Check Logs
```bash
tail -20 .cache/monitor.log
```

## 📋 Comment Categories & Actions

| Category | Keywords | Auto-Response | Example |
|----------|----------|---------------|---------|
| 1️⃣ Questions | how, cost, timeline, tools, start | ✅ Yes | "How do I get started?" |
| 2️⃣ Praise | amazing, inspiring, great, love | ✅ Yes | "This is amazing work!" |
| 3️⃣ Spam | crypto, MLM, forex, gambling | ❌ No | "Earn 1000% returns!" |
| 4️⃣ Sales | partnership, collab, sponsor | 🚩 Flag | "Let's work together..." |

## 📁 Output Files

### `.cache/youtube-comments.jsonl` (JSONL Log)
```json
{
  "timestamp": "2026-04-20T06:00:00.123456",
  "comment_id": "UgwJ_abc123",
  "author": "Sarah Chen",
  "text": "How do I get started?",
  "category": 1,
  "category_name": "Questions",
  "response_sent": true
}
```

### `.cache/youtube-review.txt` (Manual Review Queue)
```
--- 2026-04-20T06:00:00 ---
Author: Agency XYZ
Category: Sales/Partnerships
Text: We'd love to partner with you...
Comment ID: UgwJ_sales456
```

### `.cache/youtube-monitor.json` (State)
```json
{
  "last_checked": "2026-04-20T06:00:00.123456",
  "processed_comments": ["UgwJ_abc123", "UgwJ_sales456", ...]
}
```

### `.cache/monitor.log` (Cron Log)
```
==========================================
Monitor run: Sun Apr 20 06:00:00 PDT 2026
...INFO - Found 5 total comments
...INFO - Processed: 3, Auto-responses: 2, Flagged: 1
==========================================
```

## 📈 Sample Report

After each run, you'll see:
```
============================================================
YOUTUBE COMMENT MONITOR REPORT
============================================================
Timestamp: 2026-04-20T06:00:00.000000
Channel: UCyourChannelIdHere

Comments Processed: 7
  - Questions: 3
  - Praise: 2
  - Spam (filtered): 1
  - Sales/Partnerships: 1
  - Uncategorized: 0

Auto-Responses Sent: 5
Flagged for Review: 1
Log File: .cache/youtube-comments.jsonl
Review File: .cache/youtube-review.txt
============================================================
```

## ⚙️ Customization

### Edit Response Templates
Open `scripts/youtube-comment-monitor.py` and find `CATEGORIES`:

```python
1: {  # Questions
    "template": "Your custom response here..."
},
2: {  # Praise
    "template": "Your custom response here..."
}
```

### Add Keywords
Modify the `"keywords"` lists in `CATEGORIES`:

```python
1: {
    "keywords": ["how", "where", "your-keywords-here"],
    ...
}
```

### Disable Auto-Reply
Comment out the `auto_respond()` call if you only want logging:
```python
# response_sent = auto_respond(...)
response_sent = False
```

## 🔐 Security & Best Practices

- **Keep API Key Secret**: Add `.env` to `.gitignore`
- **Use OAuth for Replies**: If you need write permissions
- **Backup Logs**: Save `.cache/youtube-comments.jsonl` regularly
- **Review Flagged**: Check `.cache/youtube-review.txt` daily
- **Monitor Cron**: Verify script runs every 30 minutes

## 🐛 Troubleshooting

### Script doesn't run from cron
```bash
# Check cron logs
tail .cache/monitor.log

# Run manually
bash scripts/youtube-monitor-cron.sh

# Verify cron is installed
crontab -l | grep youtube-monitor
```

### "Permission denied" when replying
- API Key is read-only
- Switch to OAuth 2.0 or disable auto-reply

### No comments found
- Verify YOUTUBE_CHANNEL_ID is correct
- Wait for new comments

### Rate limited (429)
- YouTube API quota exhausted
- Wait 24 hours or upgrade quota

## 📚 Documentation

- **QUICKSTART.md** — 5-minute setup (START HERE)
- **YOUTUBE-MONITOR-README.md** — Complete guide
- **youtube-monitor-setup.md** — Detailed setup

## ✅ Verification Checklist

- [ ] Dependencies installed (`pip install google-auth-oauthlib google-api-python-client`)
- [ ] API Key obtained and tested
- [ ] Channel ID verified
- [ ] Environment variables set (or `.env` created)
- [ ] Manual test run successful (`python scripts/youtube-comment-monitor.py`)
- [ ] Cron job installed (`crontab -e`)
- [ ] Status checked (`bash scripts/youtube-monitor-status.sh`)
- [ ] Response templates customized (optional)

## 🎯 Next Steps

1. ✅ Complete Setup Checklist above
2. ✅ Monitor `.cache/youtube-review.txt` daily for partnership inquiries
3. ✅ Check status weekly: `bash scripts/youtube-monitor-status.sh`
4. ✅ Review analytics: `jq -r '.category_name' .cache/youtube-comments.jsonl | sort | uniq -c`
5. ✅ Customize response templates based on your brand

## 📞 Support

If something isn't working:

1. Check `.cache/monitor.log` for errors
2. Verify environment variables: `echo $YOUTUBE_API_KEY`
3. Run script manually: `python scripts/youtube-comment-monitor.py`
4. Read full docs: `scripts/YOUTUBE-MONITOR-README.md`

---

**Status**: Ready to deploy ✅

**Last Generated**: Sunday, April 20, 2026 @ 6:00 PM PST  
**Cron Schedule**: Every 30 minutes  
**Channel**: Concessa Obvius  

Start with `scripts/QUICKSTART.md` — you'll be up and running in 5 minutes!
