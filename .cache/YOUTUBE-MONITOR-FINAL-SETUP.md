# YouTube Comment Monitor - Complete Setup & Deployment

## 🎯 Overview

A complete, production-ready YouTube comment monitoring system for the **Concessa Obvius** channel that:

1. **Fetches new comments** from videos uploaded in the last 30 minutes
2. **Categorizes comments** into 4 types (Questions, Praise, Spam, Sales)
3. **Auto-responds** to Questions and Praise with template responses
4. **Flags Sales inquiries** for manual review
5. **Logs everything** to JSONL for analysis and tracking
6. **Generates reports** with statistics and metrics

---

## 📦 What You Get

### Core Scripts
- **`youtube_monitor.py`** - Main production script (requires API key)
- **`youtube_monitor_demo.py`** - Demo with sample comments (no API key needed)
- **`setup-youtube-monitor.sh`** - Automated setup script

### Documentation
- **`YOUTUBE_MONITOR_README.md`** - Complete documentation
- **`YOUTUBE-MONITOR-FINAL-SETUP.md`** - This file

### Output Files (`.cache/`)
- **`youtube-comments.jsonl`** - All comments with metadata (line-delimited JSON)
- **`youtube-processed.json`** - Duplicate prevention tracking
- **`youtube-errors.log`** - System errors and API issues
- **`youtube-report-[timestamp].txt`** - Formatted reports with statistics

---

## 🚀 Quick Start (3 Steps)

### Step 1: Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Create an **OAuth 2.0 API Key**
5. Copy the API key

### Step 2: Run Setup Script

```bash
cd /Users/abundance/.openclaw/workspace
chmod +x setup-youtube-monitor.sh
./setup-youtube-monitor.sh "YOUR_API_KEY_HERE"
```

**Or manually set environment variable:**
```bash
export YOUTUBE_API_KEY="YOUR_API_KEY_HERE"
```

### Step 3: Test It

```bash
# Test with demo (no API key)
python3 youtube_monitor_demo.py

# Run with real API key (if you have one)
python3 youtube_monitor.py
```

---

## 📊 Demo Output

Running the demo shows exactly how the system works:

```
🎬 YouTube Comment Monitor DEMO
📝 Processing sample comments...

  ✅ [Questions] Sarah Mitchell
     → Response sent: Thanks for the question! Check our FAQ...

  ✅ [Praise] Alex Johnson
     → Response sent: Thank you so much! Really appreciate...

  ❌ [Spam] CryptoBro2000
     → SPAM FILTERED

  🚨 [Sales] Business Inquiry Team
     → FLAGGED FOR MANUAL REVIEW
```

**Report Generated:**
```
Total Comments Processed:      6
  Questions (1):               2
  Praise (2):                  2
  Spam (3):                    1
  Sales Inquiries (4):         1

Auto-Responses Sent:           4
Flagged for Review:            1
Spam Filtered:                 1
```

---

## 🔧 How It Works

### Comment Categorization

**Category 1 - Questions** (Auto-Response)
- Keywords: how, tutorial, tool, cost, price, timeline, startup, where, help, ?
- Response: "Thanks for the question! Check our FAQ or reply with specifics."

**Category 2 - Praise** (Auto-Response)
- Keywords: amazing, inspiring, great, love, awesome, excellent, thanks, 🙏
- Response: "Thank you so much! Really appreciate the support 🙏"

**Category 3 - Spam** (Filtered)
- Keywords: crypto, bitcoin, nft, mlm, blackhat, scam, get-rich-quick
- Action: Skipped entirely, logged as spam

**Category 4 - Sales** (Manual Review)
- Keywords: partnership, collaborate, sponsorship, business inquiry
- Action: Flagged for human review, no auto-response

### Logging System

All comments logged to `.cache/youtube-comments.jsonl` (one JSON object per line):

```json
{
  "timestamp": "2026-04-16T19:30:44Z",
  "comment_id": "Ugx_JhF3kL_FvN8K",
  "commenter": "Sarah Mitchell",
  "text": "How do I get started with this?",
  "category": 1,
  "response_status": "sent"
}
```

### Duplicate Prevention

Processed comment IDs stored in `.cache/youtube-processed.json`:

```json
{
  "comment_ids": ["Ugx_JhF3kL_FvN8K", "Ugz_PqR7sL_MvN2K", ...]
}
```

Prevents sending duplicate responses on subsequent runs.

---

## ⚙️ Automation Options

### Option 1: Cron Job (Recommended)

Installed automatically by setup script. Runs every 30 minutes:

```bash
crontab -l  # View your cron jobs
crontab -e  # Edit cron jobs
```

The setup script adds:
```
*/30 * * * * export YOUTUBE_API_KEY='...' && cd /Users/abundance/.openclaw/workspace && python3 youtube_monitor.py
```

### Option 2: OpenClaw HEARTBEAT

Add to your OpenClaw `HEARTBEAT.md` to check every 30 minutes.

### Option 3: Manual Execution

Run anytime you want:
```bash
python3 youtube_monitor.py
```

---

## 📈 Viewing Results

### Check the Latest Report

```bash
ls -ltr .cache/youtube-report-*.txt | tail -1 | awk '{print $NF}' | xargs cat
```

### Query All Comments

```bash
# All comments
cat .cache/youtube-comments.jsonl | jq .

# Only questions
cat .cache/youtube-comments.jsonl | jq 'select(.category == 1)'

# Only flagged for review
cat .cache/youtube-comments.jsonl | jq 'select(.category == 4)'

# Count by category
cat .cache/youtube-comments.jsonl | jq -r '.category' | sort | uniq -c
```

### Export to CSV

```bash
cat .cache/youtube-comments.jsonl | \
  jq -r '[.timestamp, .comment_id, .commenter, .text, .category, .response_status] | @csv' \
  > comments.csv
```

---

## 🔐 Security Notes

- **API Key**: Stored in environment variable (not in code)
- **Auto-Responses**: Posted publicly as YouTube comments (under your account)
- **Data**: Stored locally in `.cache/` directory
- **Logs**: Include errors and API issues for debugging

**⚠️ Important**: Never commit API keys to version control. Always use environment variables.

---

## 🐛 Troubleshooting

### API Key Not Set
```
ERROR: YOUTUBE_API_KEY environment variable is not set
```
**Fix:** `export YOUTUBE_API_KEY="your-key-here"`

### Channel Not Found
```
ERROR: Channel 'Concessa Obvius' not found
```
**Fix:** 
- Verify channel name spelling
- Check channel exists on YouTube
- Ensure API has permission to search

### API Error 403
```
YouTube API error: 403
```
**Fix:**
- Verify API key is valid
- Check YouTube Data API is enabled in Google Cloud
- Check quota limits not exceeded

### No Comments Found
- Channel may not have recent videos (last 30 minutes)
- Check `.cache/youtube-errors.log` for details
- Run demo instead to verify system works

---

## 📚 Files Reference

| File | Purpose |
|------|---------|
| `youtube_monitor.py` | Main production script |
| `youtube_monitor_demo.py` | Demo with sample data |
| `setup-youtube-monitor.sh` | Automated setup |
| `YOUTUBE_MONITOR_README.md` | Full documentation |
| `.cache/youtube-comments.jsonl` | All comments (JSONL) |
| `.cache/youtube-processed.json` | Processed IDs |
| `.cache/youtube-errors.log` | Error log |
| `.cache/youtube-report-*.txt` | Reports |

---

## ✅ Checklist

- [ ] Created Google Cloud project
- [ ] Enabled YouTube Data API v3
- [ ] Generated API key
- [ ] Ran `./setup-youtube-monitor.sh "YOUR_KEY"`
- [ ] Tested with `python3 youtube_monitor_demo.py`
- [ ] Set `YOUTUBE_API_KEY` environment variable
- [ ] Verified cron job: `crontab -l`
- [ ] Checked first report in `.cache/youtube-report-*.txt`
- [ ] Bookmarked documentation

---

## 🎓 Next Steps

1. **Run the demo first** - See how it works without API key
2. **Get real API key** - Set up Google Cloud credentials
3. **Test with production** - Run `youtube_monitor.py` manually
4. **Set up automation** - Use cron for continuous monitoring
5. **Monitor reports** - Check `.cache/` for statistics and comments
6. **Customize responses** - Edit `TEMPLATES` in `youtube_monitor.py` if needed

---

## 📞 Support

For detailed information, see:
- **Full Documentation**: `YOUTUBE_MONITOR_README.md`
- **Error Log**: `.cache/youtube-errors.log`
- **System Output**: `.cache/youtube-monitor-cron.log` (after cron runs)

---

**Built with ❤️ for Concessa Obvius community engagement.**

*Last updated: 2026-04-16*
