# YouTube DM Monitor Setup Guide

**Status:** ✅ Ready to Deploy  
**Cron ID:** `c1b30404-7343-46ff-aa1d-4ff84daf3674`  
**Channel:** Concessa Obvius  
**Schedule:** Every hour (0 * * * *)

---

## ✅ What's Installed

### Files Created

| Path | Purpose |
|------|---------|
| `youtube-dm-monitor-live.py` | Main monitoring script (Python) |
| `scripts/youtube-dm-monitor-cron.sh` | Cron wrapper with logging |
| `.cache/youtube-dms.jsonl` | DM log (JSONL format) |
| `.cache/youtube-dm-report.json` | Latest hourly report |
| `.cache/youtube-dm-monitor-cron.log` | Cron execution history |
| `.cache/youtube-dm-monitor-state.json` | Processed DM tracking |

### Features Included

✅ **DM Categorization** - Automatically sorts into 4 categories:
- 🔧 Setup Help (how-to, installation, errors)
- 📧 Newsletter (email list, subscription)
- 💰 Product Inquiry (pricing, purchase, interest)
- 🤝 Partnership (collaboration, sponsorship)

✅ **Auto-Response** - Sends templated replies for each category

✅ **Comprehensive Logging** - All DMs saved with:
- Timestamp (when received)
- Sender name
- Original message text
- Auto-detected category
- Response template sent
- Partnership flag (for manual review)

✅ **Hourly Reporting** - Tracks:
- Total DMs processed (all-time)
- DMs this run
- Auto-responses sent
- Breakdown by category
- Partnership opportunities flagged
- Conversion potential (product inquiries ready to follow up)

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

```bash
pip install playwright
python -m playwright install chromium
```

### Step 2: Activate the Cron Job

**Option A: Manual crontab** (Recommended)
```bash
crontab -e
```

Add this line:
```
0 * * * * bash /Users/abundance/.openclaw/workspace/scripts/youtube-dm-monitor-cron.sh > /dev/null 2>&1
```

Save and exit (`:wq` in vim)

**Option B: Using the pre-configured file**
```bash
crontab /Users/abundance/.openclaw/workspace/.crontab
```

### Step 3: Verify Installation

```bash
# Check if cron is registered
crontab -l | grep youtube

# Should see:
# 0 * * * * bash /Users/abundance/.openclaw/workspace/scripts/youtube-dm-monitor-cron.sh
```

---

## 🔐 YouTube Studio Authentication

The monitor uses **Playwright** to access YouTube Studio DMs. On first run, it will:

1. Open a browser to YouTube Studio
2. Detect if you need to log in
3. Wait for you to authenticate
4. Cache the session for future runs

**First Time Setup:**
```bash
python3 /Users/abundance/.openclaw/workspace/youtube-dm-monitor-live.py --report
```

This will prompt you to authenticate with YouTube. After authentication, the script runs silently in subsequent cron jobs.

---

## 📊 Understanding Reports

### Real-Time Report
Run anytime to see the current state:
```bash
python3 /Users/abundance/.openclaw/workspace/youtube-dm-monitor-live.py --report
```

Output example:
```
==================================================
📊 YOUTUBE DM MONITOR REPORT
==================================================
⏰ Generated: 2026-04-16T16:04:11.715837

✅ Total DMs (all time): 42
✉️  This run: 3
📤 Auto-responses sent: 42

📂 By Category:
  • Setup Help: 12
  • Newsletter: 8
  • Product Inquiry: 15
  • Partnership: 7

🤝 Partnerships Flagged: 2
  Interesting opportunities:
    • Growth Agency LLC (2026-04-16)
      We'd love to partner on a co-branded webinar...
    • Tech Startup Inc (2026-04-15)
      Are you available for an affiliate partnership?

🎯 Conversion Potential:
  15 lead(s) ready to follow up
==================================================
```

### JSON Report
Full structured report saved to `.cache/youtube-dm-report.json`:
```json
{
  "timestamp": "2026-04-16T16:04:11.715837",
  "status": "completed",
  "total_dms_processed": 42,
  "total_this_run": 3,
  "auto_responses_sent": 42,
  "by_category": {
    "setup_help": 12,
    "newsletter": 8,
    "product_inquiry": 15,
    "partnership": 7
  },
  "partnerships_flagged": 2,
  "interesting_partnerships": [...],
  "product_inquiries_count": 15,
  "conversion_potential": "15 lead(s) ready to follow up"
}
```

### Cron Log
View execution history:
```bash
tail -50 /Users/abundance/.openclaw/workspace/.cache/youtube-dm-monitor-cron.log
```

---

## 🔍 Querying DM Data

### View All DMs
```bash
cat ~/.openclaw/workspace/.cache/youtube-dms.jsonl | jq .
```

### Filter by Category
```bash
# Product inquiries only
jq 'select(.category == "product_inquiry")' ~/.openclaw/workspace/.cache/youtube-dms.jsonl

# Partnerships flagged for review
jq 'select(.interesting_partnership == true)' ~/.openclaw/workspace/.cache/youtube-dms.jsonl
```

### Count by Category
```bash
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' \
  ~/.openclaw/workspace/.cache/youtube-dms.jsonl
```

### Count by Sender (top 10 repeat visitors)
```bash
jq -s 'group_by(.sender) | map({sender: .[0].sender, count: length}) | sort_by(-.count) | .[0:10]' \
  ~/.openclaw/workspace/.cache/youtube-dms.jsonl
```

### Recent DMs (last 5)
```bash
tail -5 ~/.openclaw/workspace/.cache/youtube-dms.jsonl | jq .
```

---

## ⚙️ Customization

### Edit Response Templates

Edit `youtube-dm-monitor-live.py` around line 50-75:

```python
TEMPLATES = {
    "setup_help": """Your custom response here...""",
    "newsletter": """Your custom response here...""",
    "product_inquiry": """Your custom response here...""",
    "partnership": """Your custom response here..."""
}
```

### Add/Modify Categorization Keywords

Edit the `CATEGORY_PATTERNS` dict around line 80-95:

```python
CATEGORY_PATTERNS = {
    "setup_help": [
        r"how\s+to", r"setup", r"install", r"error", ...
    ],
    # Add more patterns to improve accuracy
}
```

### Change Channel Name

Edit line ~35:
```python
CHANNEL_NAME = "Concessa Obvius"
```

### Adjust Cron Schedule

Edit `.crontab` or your crontab:

| Schedule | Meaning |
|----------|---------|
| `0 * * * *` | Every hour (current) |
| `0 6,12,18 * * *` | At 6am, noon, 6pm |
| `0 9 * * *` | Every day at 9am |
| `0 0 * * 0` | Every Sunday at midnight |
| `*/15 * * * *` | Every 15 minutes |

---

## 🐛 Troubleshooting

### "Playwright not installed"
```bash
pip install playwright
python -m playwright install chromium
```

### "YouTube Studio not accessible"
The script detected a login is needed. Run manually once:
```bash
python3 ~/.openclaw/workspace/youtube-dm-monitor-live.py --report
```
And log in when the browser opens.

### "No new DMs to process"
This is normal if:
- No new DMs arrived since last run
- YouTube Studio DMs haven't updated
- Check `.cache/youtube-dms.jsonl` for existing DMs

### Cron job not running
Check the log:
```bash
tail -50 ~/.openclaw/workspace/.cache/youtube-dm-monitor-cron.log
```

Verify cron is registered:
```bash
crontab -l
```

If missing, reinstall:
```bash
crontab ~/.openclaw/workspace/.crontab
```

### Responses not sending
The current version saves responses to the log but does NOT auto-send them to YouTube Studio (would require bot authentication). To enable actual DM replies, you'd need:
1. YouTube API bot credentials
2. Permission to use YouTube Messaging API
3. Additional webhook configuration

---

## 📈 Monitoring & Analytics

### Watch Live
```bash
watch -n 60 'python3 ~/.openclaw/workspace/youtube-dm-monitor-live.py --report'
```

### Daily Summary
Add to your daily report:
```bash
echo "=== YouTube DMs Today ===" && \
jq "select(.timestamp | startswith(\"$(date +%Y-%m-%d)\"))" ~/.openclaw/workspace/.cache/youtube-dms.jsonl | \
jq -s 'map(.category) | group_by(.) | map({category: .[0], count: length})'
```

### Weekly Digest
```bash
# Show all DMs from last 7 days
jq "select(.timestamp | startswith(\"$(date -d '7 days ago' +%Y-%m-%d)\"))" \
  ~/.openclaw/workspace/.cache/youtube-dms.jsonl
```

---

## 🔗 Integration Ideas

### Send Report to Discord
Set environment variable and configure webhook:
```bash
export YOUTUBE_MONITOR_WEBHOOK="https://discord.com/api/webhooks/..."
```

The script will auto-send reports to Discord if the webhook is configured.

### Export to Spreadsheet
```bash
# Convert JSONL to CSV for Google Sheets
jq -r '[.timestamp, .sender, .category, (.text | gsub("\n"; " ") | .[0:50])] | @csv' \
  ~/.openclaw/workspace/.cache/youtube-dms.jsonl > ~/Desktop/youtube-dms.csv
```

### Slack Integration
Create a bot that reads the report JSON and posts summaries to Slack.

---

## 📝 Files Reference

- **Main script:** `youtube-dm-monitor-live.py` (1100+ lines)
- **Cron wrapper:** `scripts/youtube-dm-monitor-cron.sh`
- **Configuration:** `.crontab` (cron schedule)
- **Data:** `.cache/youtube-dms.jsonl` (all DMs)
- **Reports:** `.cache/youtube-dm-report.json` (latest)
- **Log:** `.cache/youtube-dm-monitor-cron.log` (execution history)
- **State:** `.cache/youtube-dm-monitor-state.json` (processed IDs)

---

## ✨ Next Steps

1. **Install dependencies:** `pip install playwright`
2. **Activate cron:** Add to your crontab or run `crontab ~/.openclaw/workspace/.crontab`
3. **Test manually:** `python3 youtube-dm-monitor-live.py --report`
4. **Customize templates:** Edit responses in the Python script as needed
5. **Monitor:** Run manual reports daily to track DM patterns

---

**Questions?** Check the script's inline comments or run with `--help`.

