# YouTube Comment Monitor - Implementation Guide

Complete step-by-step guide to deploy and run the Concessa Obvius comment monitor.

## 📋 Overview

This system monitors the Concessa Obvius YouTube channel for new comments every 30 minutes, automatically:

1. **Fetches** comments from the channel
2. **Categorizes** them (Questions, Praise, Spam, Sales)
3. **Auto-responds** to Questions and Praise
4. **Flags** Sales inquiries for manual review
5. **Logs** everything to a structured JSONL file
6. **Reports** statistics and activity

## ⚙️ Components

| Component | File | Purpose |
|-----------|------|---------|
| Main Script | `youtube_monitor.py` | Core logic: auth, fetch, categorize, respond, log |
| Report Tool | `report_generator.py` | Generate statistics and summaries |
| Cron Config | `CRON_CONFIG.sh` | Install scheduler for 30-minute intervals |
| Auth Guide | `AUTH_SETUP.md` | OAuth 2.0 configuration instructions |
| Setup Script | `setup.sh` | Automated setup wizard |
| Dependencies | `requirements.txt` | Python package versions |
| Documentation | `README.md` | Full user guide |

## 🚀 Installation (5 Minutes)

### Option A: Automatic Setup (Recommended)

```bash
bash ~/.openclaw/workspace/.cache/setup.sh
```

This wizard will:
- ✅ Check Python installation
- ✅ Install dependencies
- ✅ Prepare scripts
- ✅ Guide through OAuth setup
- ✅ Install cron job

### Option B: Manual Setup

#### 1. Install Python Dependencies

```bash
pip install -r ~/.openclaw/workspace/.cache/requirements.txt
```

Or individually:
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

#### 2. Get OAuth 2.0 Credentials

1. Go to [Google Cloud Console](https://console.developers.google.com)
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create OAuth 2.0 Desktop credentials
5. Download the JSON file

#### 3. Configure the Monitor

```bash
python3 ~/.openclaw/workspace/.cache/youtube_monitor.py --setup-auth
```

When prompted, paste the path to your downloaded credentials JSON file.

#### 4. Test the Monitor

```bash
python3 ~/.openclaw/workspace/.cache/youtube_monitor.py
```

Expected output:
```
2026-04-20 01:00:00 - INFO - 🚀 Starting YouTube Comment Monitor
2026-04-20 01:00:02 - INFO - ✅ Authenticated with YouTube API
2026-04-20 01:00:03 - INFO - ✅ Resolved 'Concessa Obvius' to UC...
2026-04-20 01:00:10 - INFO - 📝 Fetched 42 comments
2026-04-20 01:00:11 - INFO - 📌 Processed: John (Cat 1, auto_responded)
2026-04-20 01:00:12 - INFO - ✅ Session complete: 3 processed, 2 responded, 1 flagged
```

#### 5. Install Cron Job

```bash
bash ~/.openclaw/workspace/.cache/CRON_CONFIG.sh
```

This installs a cron job that runs every 30 minutes.

Verify installation:
```bash
crontab -l
```

You should see:
```
*/30 * * * * /usr/bin/python3 ~/.openclaw/workspace/.cache/youtube_monitor.py >> ~/.openclaw/workspace/.cache/cron.log 2>&1
```

## 📊 Usage

### Run Manually (Single Check)

```bash
python3 ~/.openclaw/workspace/.cache/youtube_monitor.py
```

### View Live Logs

```bash
tail -f ~/.openclaw/workspace/.cache/cron.log
```

### Generate Reports

#### Interactive Report

```bash
python3 ~/.openclaw/workspace/.cache/report_generator.py
```

Menu:
1. Full report (all-time statistics)
2. Last hour
3. Last 24 hours
4. Last 7 days
5. Show flagged comments
6. Exit

#### Quick Reports

```bash
# All statistics
python3 ~/.openclaw/workspace/.cache/report_generator.py --full

# Show comments flagged for review
python3 ~/.openclaw/workspace/.cache/report_generator.py --flagged

# Last 6 hours
python3 ~/.openclaw/workspace/.cache/report_generator.py --hours 6
```

## 📁 File Locations

```
~/.openclaw/workspace/.cache/
├── youtube_monitor.py                    (Main script)
├── report_generator.py                   (Report tool)
├── setup.sh                              (Setup wizard)
├── CRON_CONFIG.sh                        (Cron installer)
├── youtube-comments.jsonl                (Log - created on first run)
├── youtube-monitor-state.json            (State - tracks processed comments)
├── youtube-credentials.json              (OAuth credentials - after --setup-auth)
├── youtube-token.pickle                  (OAuth token - auto-created)
├── cron.log                              (Cron execution log)
├── requirements.txt                      (Python dependencies)
├── README.md                             (User guide)
├── AUTH_SETUP.md                         (Auth instructions)
└── IMPLEMENTATION_GUIDE.md               (This file)
```

## 🔄 How It Works

### 1. Fetching Comments

Every 30 minutes, the monitor:
- Authenticates with YouTube API using OAuth 2.0
- Resolves "Concessa Obvius" to a channel ID
- Fetches the 5 most recent videos
- Collects all comments from those videos

### 2. Categorizing Comments

Each comment is analyzed and placed in one category:

```
Category 1: Questions
├─ Patterns: how-to, cost, timeline, tools, where, when
└─ Example: "How do you get started with this?"

Category 2: Praise
├─ Patterns: amazing, inspiring, love, thanks, brilliant
└─ Example: "This is amazing work! So inspiring!"

Category 3: Spam
├─ Patterns: crypto, bitcoin, MLM, make money
└─ Example: "Click here to earn $$$$$"

Category 4: Sales
├─ Patterns: partnership, collaboration, sponsor
└─ Example: "We'd love to collaborate with you!"

Category 0: No Match (no action)
└─ Example: "Just watched this, was interesting"
```

### 3. Auto-Responding

For Categories 1-2, the system automatically replies:

**Category 1 (Questions):**
```
Thanks for asking! Check our FAQ or reply for more details.
```

**Category 2 (Praise):**
```
Thanks so much for the kind words! 🙏
```

For Categories 3-4, no automatic reply is sent.
- Category 3 (Spam): Ignored
- Category 4 (Sales): Flagged for manual review

### 4. Logging

Every comment is logged to `youtube-comments.jsonl` with full details:

```json
{
  "timestamp": "2026-04-20T01:00:00Z",
  "comment_id": "UgxABCD123...",
  "commenter": "Jane Viewer",
  "text": "How do you get started?",
  "category": 1,
  "response_status": "auto_responded"
}
```

### 5. State Tracking

Processed comment IDs are stored in `youtube-monitor-state.json` to prevent reprocessing on subsequent runs:

```json
{
  "processed_comment_ids": ["UgxABC123...", "UgxDEF456..."],
  "last_run": "2026-04-20T01:00:00Z"
}
```

### 6. Reporting

Reports aggregate statistics from the log file:

```
Total comments: 127
By category: Questions=34, Praise=28, Spam=12, Sales=5, Other=48
Actions: Auto-responded=62, Flagged=5, No-action=60
Top commenters: [list of most active users]
```

## 🔧 Customization

### Change Channel

Edit `youtube_monitor.py` line ~47:

```python
CHANNEL_NAME = "Your Channel Name"  # Change this
```

### Modify Auto-Response Templates

Edit `youtube_monitor.py` lines ~60-63:

```python
RESPONSES = {
    1: "Your custom response for questions",
    2: "Your custom response for praise"
}
```

### Adjust Categorization Keywords

Edit `youtube_monitor.py` lines ~190-230 to add/remove patterns:

```python
spam_keywords = [
    r'\bcrypto\b',      # Add or remove patterns
    r'\byour_keyword\b', # Use regex for matching
]
```

### Change Cron Schedule

Edit your crontab:

```bash
crontab -e
```

Examples:

```bash
# Every 15 minutes
*/15 * * * * python3 ~/.openclaw/workspace/.cache/youtube_monitor.py >> ~/.openclaw/workspace/.cache/cron.log 2>&1

# Every hour
0 * * * * python3 ~/.openclaw/workspace/.cache/youtube_monitor.py >> ~/.openclaw/workspace/.cache/cron.log 2>&1

# Business hours only (9 AM - 6 PM)
*/30 9-17 * * * python3 ~/.openclaw/workspace/.cache/youtube_monitor.py >> ~/.openclaw/workspace/.cache/cron.log 2>&1

# Weekdays only
*/30 * * * 1-5 python3 ~/.openclaw/workspace/.cache/youtube_monitor.py >> ~/.openclaw/workspace/.cache/cron.log 2>&1
```

## 🐛 Troubleshooting

### Problem: "Credentials file not found"

**Solution:**
```bash
python3 ~/.openclaw/workspace/.cache/youtube_monitor.py --setup-auth
```

Paste the path to your downloaded Google credentials JSON file.

### Problem: "Channel not found"

**Solution:**
1. Verify the exact channel name in YouTube
2. Edit `youtube_monitor.py` line ~47 with correct name
3. Delete `youtube-token.pickle` to force re-authentication
4. Run monitor again

### Problem: "Authentication failed"

**Solution:**
1. Verify YouTube Data API is enabled in Google Cloud Console
2. Delete `youtube-token.pickle`:
   ```bash
   rm ~/.openclaw/workspace/.cache/youtube-token.pickle
   ```
3. Re-authenticate:
   ```bash
   python3 ~/.openclaw/workspace/.cache/youtube_monitor.py --setup-auth
   ```

### Problem: "No comments fetched"

**Solution:**
- Check that channel has public comments enabled
- Verify YouTube Data API quota (10,000 units/day): https://console.developers.google.com
- Some videos may have comments disabled

### Problem: "Cron job not running"

**Solution:**

Check if cron is running:
```bash
# macOS
sudo launchctl list | grep cron

# Linux
sudo systemctl status cron
```

Check cron logs:
```bash
tail -100 ~/.openclaw/workspace/.cache/cron.log
```

Check if job is in crontab:
```bash
crontab -l
```

If missing, reinstall:
```bash
bash ~/.openclaw/workspace/.cache/CRON_CONFIG.sh
```

### Problem: "Auto-responses not working"

**Solution:**
- Verify you own/manage the YouTube channel
- Check comment reply settings are enabled
- Some comment threads may not support replies (e.g., community posts)
- Try a manual reply on YouTube to test

## 📈 Monitoring Checklist

Before going live:

- [ ] Python 3.7+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] OAuth 2.0 credentials obtained from Google Cloud Console
- [ ] Auth setup completed (`python3 youtube_monitor.py --setup-auth`)
- [ ] Test run successful (check `youtube-comments.jsonl`)
- [ ] Comments log created with sample entries
- [ ] Report generator works (`python3 report_generator.py`)
- [ ] Cron job installed (`CRON_CONFIG.sh`)
- [ ] Cron log shows successful runs (`tail cron.log`)
- [ ] First 30 minutes of scheduled runs completed successfully

## 📊 Expected Behavior

### First Run
- Fetches all comments from recent videos
- Logs them all
- Responds to relevant ones
- Creates `youtube-comments.jsonl` and `youtube-monitor-state.json`

### Subsequent Runs (Every 30 Minutes)
- Fetches only **new** comments (using state tracking)
- Logs new comments
- Responds to relevant new comments
- Updates state file with new comment IDs
- Cron log shows success/failure

### After 24 Hours
- ~48 executions (every 30 min)
- Hundreds of comments processed (if channel is active)
- Report shows daily trends and top commenters
- Flagged comments ready for manual review

## 🔐 Security & Privacy

- **OAuth 2.0**: Industry standard authentication
- **Local Storage**: All data stored locally, no cloud sync
- **API Key**: Never hardcoded; credentials file is read-only
- **Credentials**: Kept in `.cache/` directory, add to `.gitignore`

Never commit these files to version control:
```
youtube-credentials.json
youtube-token.pickle
cron.log
youtube-comments.jsonl (optional, based on sensitivity)
```

## 📞 Support Resources

- **Setup Issues:** See `AUTH_SETUP.md`
- **Usage Guide:** See `README.md`
- **Report Issues:** Check `cron.log` for errors
- **API Quota:** https://console.developers.google.com

## ✨ Next Steps

1. **Monitor logs daily:**
   ```bash
   tail -f ~/.openclaw/workspace/.cache/cron.log
   ```

2. **Review flagged comments weekly:**
   ```bash
   python3 ~/.openclaw/workspace/.cache/report_generator.py
   # Select option 5 to show flagged comments
   ```

3. **Analyze trends:**
   ```bash
   python3 ~/.openclaw/workspace/.cache/report_generator.py --full
   ```

4. **Adjust categorization as needed:**
   - Edit keyword patterns in `youtube_monitor.py`
   - Customize responses
   - Change cron schedule

---

**Setup Time:** 5-10 minutes  
**Active Monitoring:** Automatic (every 30 minutes)  
**Maintenance:** ~5 minutes per week (review flagged)

Let the system run. It'll handle comment monitoring on its own. 🎬
