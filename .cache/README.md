# YouTube Comment Monitor - Concessa Obvius

Complete automated comment monitoring system for the Concessa Obvius YouTube channel. Fetches comments every 30 minutes, categorizes them, auto-responds to questions & praise, and flags sales inquiries for manual review.

## 📦 What's Included

```
.cache/
├── youtube_monitor.py          # Main monitoring script
├── report_generator.py         # Report generation tool
├── AUTH_SETUP.md              # OAuth 2.0 authentication guide
├── CRON_CONFIG.sh             # Cron scheduler installation
├── youtube-comments.jsonl     # All comments log (auto-created)
├── youtube-monitor-state.json # Processing state (auto-created)
└── cron.log                   # Cron execution log (auto-created)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Setup OAuth 2.0 Authentication

```bash
python3 ~/.openclaw/workspace/.cache/youtube_monitor.py --setup-auth
```

See [AUTH_SETUP.md](AUTH_SETUP.md) for detailed instructions.

### 3. Test Single Run

```bash
python3 ~/.openclaw/workspace/.cache/youtube_monitor.py
```

Expected output:
```
2026-04-20 01:00:00 - INFO - 🚀 Starting YouTube Comment Monitor
2026-04-20 01:00:02 - INFO - ✅ Authenticated with YouTube API
2026-04-20 01:00:05 - INFO - ✅ Resolved 'Concessa Obvius' to UC...
2026-04-20 01:00:15 - INFO - 📝 Fetched 42 comments
2026-04-20 01:00:16 - INFO - 📌 Processed: User1 (Cat 1, auto_responded)
2026-04-20 01:00:16 - INFO - ✅ Session complete: 3 processed, 2 responded, 1 flagged
```

### 4. Setup Scheduled Execution (Every 30 Minutes)

```bash
bash ~/.openclaw/workspace/.cache/CRON_CONFIG.sh
```

Or manually:

```bash
crontab -e
# Add this line:
*/30 * * * * /usr/bin/python3 ~/.openclaw/workspace/.cache/youtube_monitor.py >> ~/.openclaw/workspace/.cache/cron.log 2>&1
```

## 📊 How It Works

### Comment Categorization

The script automatically categorizes each comment into one of four types:

| Category | Type | Keywords | Action |
|----------|------|----------|--------|
| **1** | **Questions** | how-to, cost, timeline, tools, where, when | ✅ Auto-respond |
| **2** | **Praise** | amazing, inspiring, love, thanks, brilliant | ✅ Auto-respond |
| **3** | **Spam** | crypto, bitcoin, MLM, "make money", follow me | 🚫 No action |
| **4** | **Sales** | partnership, collaboration, sponsor, advertise | 🚩 Flag for review |
| **0** | **No Match** | Other comments | 🚫 No action |

### Auto-Responses

**Category 1 (Questions):**
> "Thanks for asking! Check our FAQ or reply for more details."

**Category 2 (Praise):**
> "Thanks so much for the kind words! 🙏"

## 📝 Data Logging

Every comment is logged to `youtube-comments.jsonl` with full context:

```json
{
  "timestamp": "2026-04-20T01:00:00Z",
  "comment_id": "UgxABCD123XYZ...",
  "commenter": "Jane Viewer",
  "text": "How do you get started with this?",
  "category": 1,
  "response_status": "auto_responded"
}
```

The script maintains state in `youtube-monitor-state.json` to avoid reprocessing:

```json
{
  "processed_comment_ids": ["UgxABCD123...", "UgxDEF456..."],
  "last_run": "2026-04-20T01:00:00Z"
}
```

## 📊 Generating Reports

### Interactive Report

```bash
python3 ~/.openclaw/workspace/.cache/report_generator.py
```

Menu options:
1. **Full report** - All-time statistics
2. **Last hour** - Recent activity
3. **Last 24 hours** - Daily summary
4. **Last 7 days** - Weekly trend
5. **Show flagged** - Comments awaiting review
6. **Exit**

### Command-Line Reports

```bash
# Full statistics
python3 ~/.openclaw/workspace/.cache/report_generator.py --full

# Flagged comments (sales/partnerships)
python3 ~/.openclaw/workspace/.cache/report_generator.py --flagged

# Last 6 hours
python3 ~/.openclaw/workspace/.cache/report_generator.py --hours 6
```

### Sample Report Output

```
======================================================================
📊 YOUTUBE COMMENT MONITOR - SESSION REPORT
======================================================================

📈 OVERVIEW
   Total comments processed: 127
   First comment: 2026-04-18T14:30:00Z
   Latest comment: 2026-04-20T00:30:00Z

📂 COMMENTS BY CATEGORY
   ├─ Category 1 (Questions): 34
   ├─ Category 2 (Praise): 28
   ├─ Category 3 (Spam): 12
   ├─ Category 4 (Sales): 5
   └─ Category 0 (No Action): 48

✅ ACTIONS TAKEN
   Auto-responded: 62
   Flagged for review: 5
   No action taken: 60

👥 TOP COMMENTERS
   John Developer: 3 comments
   Sarah Enthusiast: 2 comments
   Mike Supporter: 2 comments
```

## 🔧 Configuration

### Channel Selection

To monitor a different YouTube channel, edit `youtube_monitor.py`:

```python
# Line ~47
CHANNEL_NAME = "Concessa Obvius"  # Change this to your channel name
```

### Response Templates

Customize auto-responses in `youtube_monitor.py`:

```python
# Lines ~60-63
RESPONSES = {
    1: "Thanks for asking! Check our FAQ or reply for more details.",
    2: "Thanks so much for the kind words! 🙏"
}
```

### Categorization Keywords

Add or modify keyword patterns in the `categorize_comment()` method:

```python
# Lines ~190-230
spam_keywords = [
    r'\bcrypto\b', r'\bbitcoin\b', ...
]
```

## 📋 Monitoring Checklist

- [ ] Dependencies installed (`pip install`)
- [ ] OAuth 2.0 credentials configured (`--setup-auth`)
- [ ] Single test run successful (`python3 youtube_monitor.py`)
- [ ] First comment logged to `.cache/youtube-comments.jsonl`
- [ ] Cron job installed (`CRON_CONFIG.sh`)
- [ ] Cron log verified (`tail .cache/cron.log`)
- [ ] Report generated successfully (`report_generator.py`)

## 🐛 Troubleshooting

### "Credentials file not found"
Run authentication setup again:
```bash
python3 youtube_monitor.py --setup-auth
```

### "Channel not found"
Verify the exact channel name in YouTube. Edit `youtube_monitor.py` line ~47.

### "No comments fetched"
- Check that the channel has public comments enabled
- Verify YouTube Data API quota (10,000 units/day)
- Check API permissions in Google Cloud Console

### "Cron not running"
Verify cron is running:
```bash
sudo launchctl list | grep cron  # macOS
sudo systemctl status cron       # Linux
```

Check cron log:
```bash
tail -f ~/.openclaw/workspace/.cache/cron.log
```

### "Auto-responses failing"
- Verify the YouTube channel is owned/managed by your Google account
- Check comment thread settings (replies must be enabled)
- Some comments may not support replies (community posts, etc.)

## 📦 Files Reference

| File | Purpose |
|------|---------|
| `youtube_monitor.py` | Main script - handles auth, fetching, categorizing, responding |
| `report_generator.py` | Standalone report tool for analyzing logs |
| `AUTH_SETUP.md` | Step-by-step OAuth 2.0 configuration |
| `CRON_CONFIG.sh` | Bash script to install cron job |
| `youtube-comments.jsonl` | NDJSON log of all processed comments |
| `youtube-monitor-state.json` | JSON state file tracking processed comment IDs |
| `youtube-token.pickle` | OAuth token (auto-created, keep safe) |
| `youtube-credentials.json` | OAuth credentials (auto-created from setup) |
| `cron.log` | Execution logs from cron runs |

## 🔐 Security Notes

- **Credentials:** Keep `youtube-credentials.json` and `youtube-token.pickle` private
- **API Key:** Never hardcode API keys; use OAuth 2.0 for authentication
- **Quota:** YouTube Data API has 10,000 units/day; monitor usage
- **Data:** All comments are logged locally; no cloud storage

## 📞 Support

For issues with the monitor:
1. Check the logs: `tail -f ~/.openclaw/workspace/.cache/cron.log`
2. Review [AUTH_SETUP.md](AUTH_SETUP.md) for authentication issues
3. Verify YouTube API is enabled: https://console.developers.google.com

## ✨ Features

✅ Automated fetching every 30 minutes  
✅ Intelligent comment categorization  
✅ Auto-responses to questions & praise  
✅ Flags sales inquiries for manual review  
✅ Complete JSONL logging  
✅ State tracking (no reprocessing)  
✅ Interactive & CLI reports  
✅ Cron-ready for scheduling  
✅ OAuth 2.0 authentication  
✅ Configurable keywords & responses  

## 📈 Next Steps

1. **Monitor logs:** `tail -f ~/.openclaw/workspace/.cache/cron.log`
2. **Review flagged:** `python3 report_generator.py` → Option 5
3. **Adjust keywords:** Edit categorization patterns in `youtube_monitor.py`
4. **Customize responses:** Update `RESPONSES` dict in `youtube_monitor.py`
5. **Schedule variations:** See options in `CRON_CONFIG.sh`

---

**Version 1.0** | Built for Concessa Obvius | Last updated: 2026-04-20
