# 📺 Concessa Obvius YouTube Comment Monitor

Automated comment monitoring, categorization, and response system for the Concessa Obvius YouTube channel.

**Status:** 🔴 Requires Setup (YouTube API credentials)  
**Schedule:** Every 30 minutes (OpenClaw cron)  
**Last Run:** See `youtube-monitor-state.json`

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Set Up YouTube API
Follow the **detailed setup** in `YOUTUBE-SETUP.md` (takes ~10 minutes):
- Create Google Cloud project
- Enable YouTube Data API v3
- Download OAuth credentials → `~/.openclaw/workspace/.cache/youtube-credentials.json`

### 3. Test It
```bash
python3 ~/.openclaw/workspace/.cache/youtube-monitor.py
```

The script will:
- Open a browser for OAuth authorization (one-time)
- Fetch recent videos from Concessa Obvius channel
- Find new comments
- Categorize and respond
- Log everything to `youtube-comments.jsonl`

---

## 📋 What It Does

### Automatic Comment Processing

| Category | Examples | Action |
|----------|----------|--------|
| **Question** | "How do I start?" "What tools?" "Cost?" | ✅ Auto-reply with template |
| **Praise** | "Amazing!" "This inspired me" "Love it" | ✅ Auto-reply with template |
| **Spam** | Crypto, MLM, "passive income", etc. | ⏭️ Skip (no action) |
| **Sales** | "Partnership?", "Sponsor", "Collab" | 🚩 Flag for your review |
| **Other** | Doesn't match patterns | ⏭️ Skip |

### Response Templates
Auto-replies are customizable in `youtube-monitor.py`:
```python
TEMPLATES = {
    "question": """Thanks for the question!
    
**Getting Started:** [link]
**Tools:** [link]
**Cost:** See pricing page
**Timeline:** Most see results in 30 days

Reply if you need more!""",
    
    "praise": "Thank you! 🙏 Really means a lot. Keep us posted!"
}
```

---

## 📁 Files & Directories

```
~/.openclaw/workspace/.cache/
├── youtube-monitor.py              ← Main monitoring script
├── youtube-log-viewer.py           ← Analysis & reporting tool
├── youtube-credentials.json        ← YOUR API KEY (keep safe!)
├── youtube-token.json              ← Auto-generated OAuth token
├── youtube-monitor-state.json      ← Tracks last run + processed comments
├── youtube-comments.jsonl          ← All logged comments (log file)
├── YOUTUBE-README.md               ← This file
├── YOUTUBE-SETUP.md                ← Detailed setup guide
└── YOUTUBE-CONFIG.json             ← [Optional] Alternative config file
```

---

## 📊 Usage

### Monitor (Runs Every 30 Minutes Automatically)
```bash
# Manual run (useful for testing):
python3 ~/.openclaw/workspace/.cache/youtube-monitor.py
```

Output:
```
[2026-04-16 15:30:00] Starting YouTube Comment Monitor
Found channel ID: UCxxx...
Fetching recent videos...
Found 3 recent videos
Found 5 new comments to process
[question] Jane Doe: How do I start with your course?...
[praise] Bob Smith: This was absolutely amazing!...
[sales] Acme Corp: We'd love to sponsor your channel!...

============================================================
YOUTUBE COMMENT MONITOR REPORT
============================================================
Timestamp: 2026-04-16T15:30:00.123456
Channel: Concessa Obvius

Statistics:
  Total comments processed: 5
  Auto-responses sent: 2
  Flagged for review: 1

Breakdown by category:
  Question: 2
  Praise: 1
  Sales: 1
  Other: 1
============================================================
```

### View & Analyze Comments

#### Summary Statistics
```bash
# All-time statistics
python3 youtube-log-viewer.py summary

# Last 7 days only
python3 youtube-log-viewer.py summary 7
```

#### View Flagged Sales Inquiries
```bash
python3 youtube-log-viewer.py flagged
```

#### View Unanswered Questions
```bash
python3 youtube-log-viewer.py unanswered
```

#### View Specific Category
```bash
python3 youtube-log-viewer.py questions    # All questions
python3 youtube-log-viewer.py praise       # All praise
python3 youtube-log-viewer.py spam         # All spam
python3 youtube-log-viewer.py sales        # All sales
```

#### Export to File
```bash
python3 youtube-log-viewer.py export questions questions.jsonl
```

---

## 📝 Log Format (youtube-comments.jsonl)

Each line is a JSON object:
```json
{
  "timestamp": "2026-04-16T15:30:45Z",
  "comment_id": "UgxAbCdE...",
  "video_id": "dQw4w9WgXcQ",
  "commenter": "Jane Doe",
  "text": "How do I get started with your course?",
  "category": "question",
  "published_at": "2026-04-16T15:25:00Z",
  "like_count": 3,
  "reply_count": 0,
  "response_id": "UgyBcDeFg...",
  "response_status": "sent"
}
```

**response_status values:**
- `pending` - Waiting to be processed
- `sent` - Auto-reply was posted successfully
- `failed` - Reply attempt failed (check permissions)
- `flagged_for_review` - Marked for manual action (sales inquiries)

---

## ⚙️ Configuration

### Change Channel
Edit line 28 in `youtube-monitor.py`:
```python
CHANNEL_NAME = "Your Channel Name"  # Must be exact
```

### Customize Auto-Responses
Edit the `TEMPLATES` dict (lines 56-63):
```python
TEMPLATES = {
    "question": "Your custom response here...",
    "praise": "Your custom response here..."
}
```

### Adjust Categorization
Edit `CATEGORY_PATTERNS` (lines 65-71) to match your comment styles:
```python
CATEGORY_PATTERNS = {
    "question": r"(how|what|help|cost|...)",
    "praise": r"(amazing|love|inspiring|...)",
    "spam": r"(crypto|bitcoin|...)",
    "sales": r"(partner|collab|sponsor|...)"
}
```

### Change Check Interval
The cron job runs every 30 minutes. To adjust:
- Edit the cron trigger in OpenClaw config
- Or manually adjust `minutes=35` in `get_recent_videos()` function

---

## 🔍 Troubleshooting

### "Missing YouTube API dependencies"
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### "Could not find channel: Concessa Obvius"
- Channel name must be **exact** (case-sensitive)
- Channel must be public/searchable
- Verify at youtube.com/@ConcessaObvius

### "Permission denied" when posting replies
- Verify YouTube API has correct scope enabled
- Re-authenticate: `rm ~/.openclaw/workspace/.cache/youtube-token.json`
- Re-run the monitor to get fresh token

### No new comments showing up
- Check if videos were published recently (within 35 minutes)
- Manually verify comments on the channel
- Run monitor manually to see detailed debug output

### "oauth2.error: ProviderError: invalid_grant"
- Token may have expired
- Delete `youtube-token.json` and re-run
- Verify credentials JSON is still valid

### Comments not being responded to
- Check `response_status` in log file
- Verify templates are not empty
- Ensure API has posting permission

---

## 📈 Analytics Examples

### Get All Sales Inquiries This Week
```bash
python3 youtube-log-viewer.py summary 7
# Then check "sales" count in output
```

### Find High-Engagement Comments
```bash
# Manual: Open youtube-comments.jsonl and sort by like_count
jq 'select(.like_count > 5)' youtube-comments.jsonl
```

### Success Rate
```bash
# Count auto-responses sent vs. questions asked
grep '"category": "question"' youtube-comments.jsonl | wc -l
grep '"response_status": "sent"' youtube-comments.jsonl | wc -l
```

---

## 🔐 Security Notes

- **Keep `youtube-credentials.json` safe** — Don't commit to git
- **Token expires after 6 months** — Re-authenticate if needed
- **API quotas** — YouTube API has daily quotas; monitor usage in Cloud Console
- **Private data** — Comments are stored locally; no cloud sync by default

---

## 📞 Support

### Check the Full Setup Guide
See `YOUTUBE-SETUP.md` for detailed OAuth setup and troubleshooting.

### Manual Debugging
```bash
# Enable verbose output (modify script to add print statements)
python3 youtube-monitor.py

# Check raw log file
tail -20 youtube-comments.jsonl

# Parse specific comment
grep '"comment_id": "xxx"' youtube-comments.jsonl | jq .
```

### Common Issues Checklist
- [ ] Dependencies installed? `pip list | grep google`
- [ ] Credentials file exists? `ls ~/.openclaw/workspace/.cache/youtube-credentials.json`
- [ ] Channel name correct? Check @ YouTube
- [ ] API enabled? Check Cloud Console
- [ ] OAuth scope correct? `youtube.force-ssl`

---

## 📚 Next Steps

1. ✅ Follow `YOUTUBE-SETUP.md` to authorize
2. ✅ Run monitor once manually: `python3 youtube-monitor.py`
3. ✅ Check `youtube-comments.jsonl` for results
4. ✅ Use `youtube-log-viewer.py` to analyze
5. ✅ Monitor runs automatically every 30 minutes

---

**Version:** 1.0  
**Last Updated:** 2026-04-16  
**Monitor Cron ID:** `youtube-comment-monitor`
