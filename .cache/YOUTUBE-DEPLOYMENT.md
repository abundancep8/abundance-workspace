# 📺 YouTube Comment Monitor - Deployment Guide

**Cron Job:** `youtube-comment-monitor`  
**Schedule:** Every 30 minutes  
**Status:** 🔴 **SETUP REQUIRED** (YouTube API credentials needed)

---

## 🎯 What You're Getting

An automated system that monitors the Concessa Obvius YouTube channel for new comments, categorizes them, and automatically responds to questions and praise while flagging sales inquiries for review.

**Key Features:**
- ✅ Auto-replies to questions with templates
- ✅ Auto-replies to praise messages
- 🚩 Flags sales/partnership inquiries for manual review
- 🔒 Filters out spam automatically
- 📊 Comprehensive logging in JSONL format
- 📈 Built-in analytics & reporting

---

## 📂 System Files

```
~/.openclaw/workspace/.cache/

Core Scripts:
├── youtube-monitor.py              (Main 30-min monitor)
├── youtube-log-viewer.py           (Analysis tool)
└── youtube-test.py                 (Setup validator)

Documentation:
├── YOUTUBE-README.md               (Start here!)
├── YOUTUBE-SETUP.md                (Detailed OAuth setup)
├── YOUTUBE-DEPLOYMENT.md           (This file)
└── youtube-config-template.json    (Config reference)

Data Files:
├── youtube-comments.jsonl          (All logged comments)
├── youtube-monitor-state.json      (Tracks processed comments)
├── youtube-credentials.json        (OAuth credentials - YOU PROVIDE)
└── youtube-token.json              (Generated automatically)
```

---

## 🚀 Getting Started (5 Steps)

### Step 1: Install Python Dependencies (1 min)
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 2: Create YouTube API Credentials (5 min)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project: "YouTube Comment Monitor"
3. Enable **YouTube Data API v3**
4. Create **OAuth 2.0 Desktop Client** credentials
5. Download the JSON file
6. Save it to: `~/.openclaw/workspace/.cache/youtube-credentials.json`

👉 **Full instructions** in `YOUTUBE-SETUP.md`

### Step 3: Run the Tester (1 min)
```bash
python3 ~/.openclaw/workspace/.cache/youtube-test.py
```

This validates your setup before the monitor runs.

### Step 4: Run the Monitor Manually (First Time Only)
```bash
python3 ~/.openclaw/workspace/.cache/youtube-monitor.py
```

- Opens browser for OAuth permission (one-time)
- Fetches recent comments
- Posts auto-replies
- Creates log files

### Step 5: Verify It Worked
```bash
# Check the log file
tail ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Run the analyzer
python3 ~/.openclaw/workspace/.cache/youtube-log-viewer.py summary
```

✅ **Done!** Monitor runs automatically every 30 minutes now.

---

## 📋 What Happens Each Run

The monitor:

1. **Fetches** new videos from the past 35 minutes
2. **Scans** comments on those videos
3. **Categorizes** each comment:
   - ❓ Question → Auto-reply (template)
   - 👏 Praise → Auto-reply (template)
   - 🚫 Spam → Ignore
   - 💼 Sales → Flag for review
   - 📝 Other → Log only
4. **Posts** auto-replies to YouTube
5. **Logs** everything to `youtube-comments.jsonl`
6. **Reports** stats (total processed, sent, flagged)

**Runtime:** ~30-60 seconds per run

---

## 🎮 Daily Operations

### View New Comments Since Last Check
```bash
# What needs attention?
python3 youtube-log-viewer.py flagged        # Sales to review
python3 youtube-log-viewer.py unanswered    # Questions we missed
```

### Analyze This Week's Activity
```bash
# Stats for last 7 days
python3 youtube-log-viewer.py summary 7

# All questions asked
python3 youtube-log-viewer.py questions

# All praise received
python3 youtube-log-viewer.py praise
```

### Review Specific Categories
```bash
python3 youtube-log-viewer.py sales         # Partnership inquiries
python3 youtube-log-viewer.py spam          # Spam caught
```

---

## ⚙️ Customization

### Change Auto-Reply Templates
Edit `youtube-monitor.py`, lines 56-63:
```python
TEMPLATES = {
    "question": "Your custom response...",
    "praise": "Your custom response..."
}
```

### Adjust Comment Categorization
Edit `CATEGORY_PATTERNS`, lines 65-71:
```python
CATEGORY_PATTERNS = {
    "question": r"(how|what|help|cost|...)",
    "praise": r"(amazing|love|inspiring|...)",
    "spam": r"(crypto|bitcoin|...)",
    "sales": r"(partner|collab|sponsor|...)"
}
```

### Change Monitoring Channel
Edit line 28:
```python
CHANNEL_NAME = "Your Channel Name"  # Must match exactly
```

### Adjust Check Interval
Currently checks every 35 minutes of lookback. To change the window in `get_recent_videos()`:
```python
def get_recent_videos(youtube, uploads_id, minutes=35):  # Change this
```

---

## 📊 Reporting & Analytics

### Generate Weekly Report
```bash
python3 youtube-log-viewer.py summary 7
```

Output:
```
Total comments: 42
By Category:
  Question:     18 (42.9%)
  Praise:       12 (28.6%)
  Sales:         5 (11.9%)
  Spam:          4 (9.5%)
  Other:         3 (7.1%)

By Response Status:
  Sent:         30 (71.4%)
  Flagged for review:  5 (11.9%)
  Pending:       7 (16.7%)
```

### Export for Further Analysis
```bash
# Get all sales inquiries as CSV
python3 youtube-log-viewer.py sales > sales.txt

# Or as JSON
python3 youtube-log-viewer.py export sales sales.jsonl
```

---

## 🔐 Security

**Credentials are stored locally only:**
- `youtube-credentials.json` — Your OAuth credentials (keep private)
- `youtube-token.json` — Access token (auto-generated, expires in 6 months)

**Best practices:**
- Don't commit credentials to git
- Don't share credentials.json with others
- Monitor stays on your machine (no cloud sync)

---

## ⚠️ Troubleshooting

### "Could not find channel"
- Channel name must match exactly (check @ChannelName on YouTube)
- Channel must be public
- Try: `CHANNEL_NAME = "Concessa Obvius"`

### "Permission denied" posting replies
- Verify YouTube API has `youtube.force-ssl` scope
- Delete `youtube-token.json` and re-authenticate
- Check Google Cloud Console for permission errors

### No new comments found
- Check recent videos (must be <35 min old)
- Manually verify comments exist on channel
- Check if comments are hidden/restricted

### "Invalid OAuth token"
```bash
rm ~/.openclaw/workspace/.cache/youtube-token.json
python3 ~/.openclaw/workspace/.cache/youtube-monitor.py
# Re-authorize in browser
```

### API quota exceeded
- YouTube API has daily quotas (usually 10,000 units/day)
- Check usage in Google Cloud Console
- Reduce check frequency if needed

**See full troubleshooting:** `YOUTUBE-SETUP.md`

---

## 📈 Monitoring the Monitor

The system logs everything for visibility:

```bash
# Check latest entries
tail -20 ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Find errors
grep '"response_status": "failed"' youtube-comments.jsonl

# See processing timeline
grep '"timestamp"' youtube-comments.jsonl | sort | tail -10
```

---

## 🔄 Cron Integration

The monitor is scheduled as an OpenClaw cron job:
- **ID:** `youtube-comment-monitor`
- **Frequency:** Every 30 minutes
- **Command:** `python3 ~/.openclaw/workspace/.cache/youtube-monitor.py`

To view/modify cron schedule:
```bash
openclaw cron list
openclaw cron edit youtube-comment-monitor
```

---

## 📝 State Management

The system tracks processed comments to avoid duplicates:

**`youtube-monitor-state.json`:**
```json
{
  "last_check": "2026-04-16T15:30:00Z",
  "processed_comments": ["UgyAbCdE...", "UgxFghIjk...", ...]
}
```

**Important:**
- Don't delete this file — it prevents duplicate responses
- Auto-updated after each run
- Safe to inspect but don't edit manually

---

## 🎯 Next Actions

**Immediate:**
1. ✅ Run `youtube-test.py` to validate setup
2. ✅ Follow `YOUTUBE-SETUP.md` for OAuth
3. ✅ Run `youtube-monitor.py` manually once
4. ✅ Check `youtube-comments.jsonl` for results

**Ongoing:**
1. Monitor flagged sales inquiries weekly
2. Review auto-reply effectiveness
3. Adjust templates based on response patterns
4. Track analytics with `youtube-log-viewer.py`

**Optional Advanced:**
- Customize categorization patterns
- Build custom analytics on the JSONL data
- Export metrics to dashboard
- Integrate with Discord/Slack for alerts

---

## 📞 Support Resources

- **Setup Help:** `YOUTUBE-SETUP.md`
- **Full Documentation:** `YOUTUBE-README.md`
- **Configuration Reference:** `youtube-config-template.json`
- **Quick Test:** `python3 youtube-test.py`

---

## Version Info

- **Monitor Version:** 1.0
- **YouTube API:** v3
- **Python:** 3.7+
- **Dependencies:** google-auth-oauthlib, google-api-python-client
- **Deployed:** 2026-04-16
- **Last Updated:** 2026-04-16

---

**Status:** Ready to deploy. Follow Step 1-5 above to activate. 🚀
