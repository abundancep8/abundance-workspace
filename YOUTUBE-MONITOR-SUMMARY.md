# YouTube Comment Monitor - Complete System

**Status:** ✅ Ready to Deploy  
**Channel:** Concessa Obvius  
**Schedule:** Every 30 minutes (via cron)  
**Created:** April 18, 2026

---

## 🎯 What This System Does

**Automatically monitors your YouTube channel for new comments:**

1. ✅ Fetches comments every 30 minutes
2. 🏷️ Categorizes each comment (questions, praise, spam, sales, neutral)
3. 💬 Auto-responds to questions and praise with templates
4. 🚩 Flags sales/partnership inquiries for manual review
5. 📝 Logs everything to a searchable JSON file
6. 📊 Generates statistics and reports

---

## 📦 What's Included

### Core Scripts (in `.cache/`)

| File | Purpose |
|------|---------|
| `youtube-comment-monitor.py` | Main monitoring script (runs every 30 min) |
| `youtube-monitor-report.py` | Generate analytics & reports |
| `youtube-monitor-install.sh` | Automated setup wizard |
| `youtube-monitor-verify.sh` | Verify setup & diagnose issues |

### Configuration

| File | Purpose |
|------|---------|
| `youtube-monitor-config.json` | Channel ID, templates, keywords |
| `seen-comment-ids.json` | Track processed comments (prevent duplicates) |
| `youtube-monitor.log` | Cron execution log |
| `youtube-comments.jsonl` | Complete comment archive (searchable) |

### Documentation

| File | Purpose |
|------|---------|
| `YOUTUBE-MONITOR-GUIDE.md` | Quick reference & commands |
| `youtube-monitor-setup.md` | Detailed setup instructions |
| `YOUTUBE-MONITOR-SUMMARY.md` | This file |

---

## ⚡ Quick Start (30 seconds)

### Step 1: Run the Setup Wizard
```bash
bash ~/.openclaw/workspace/.cache/youtube-monitor-install.sh
```

It will:
- Install Python dependencies
- Ask for Google OAuth credentials
- Ask for your YouTube channel ID
- Run first test (opens Google login)
- Install cron job

### Step 2: Check Status (anytime)
```bash
bash ~/.openclaw/workspace/.cache/youtube-monitor-verify.sh
```

### Step 3: View Reports
```bash
python ~/.openclaw/workspace/.cache/youtube-monitor-report.py
```

---

## 🔑 Key Features

### Auto-Categorization

```
❓ Questions → "How do I...?" → Auto-responds with help
👍 Praise → "Amazing!" → Auto-responds with thank you
🚫 Spam → "Crypto..." → Logged, no response
🚩 Sales → "Partnership..." → Flagged for manual review
ℹ️ Neutral → General comments → Logged only
```

### Smart Keyword Detection

The system recognizes patterns like:
- **Questions:** "how do i", "how to", "cost", "tools", "timeline"
- **Praise:** "amazing", "inspiring", "love", "awesome", "excellent"
- **Spam:** "crypto", "bitcoin", "nft", "mlm", "casino"
- **Sales:** "partnership", "sponsor", "advertise", "business inquiry"

Customize keywords in `youtube-monitor-config.json`.

### Logging Everything

Every comment is logged to `youtube-comments.jsonl` with:
- Timestamp
- Author name
- Comment text
- Detected category
- Auto-response status
- Link to video

Query with `jq`:
```bash
# Recent comments
tail -10 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq '.'

# Sales inquiries
jq 'select(.category == "sales")' ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Count by category
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

---

## 🔐 What It Needs

### 1. Google OAuth Credentials
- Get from: https://console.cloud.google.com
- Enable YouTube Data API v3
- Create OAuth 2.0 Desktop credentials
- Download JSON file → save to `.cache/credentials.json`

### 2. Your Channel ID
- Find at: youtube.com/account (Advanced settings)
- Format: `UCxxxxxxxxxxxxxxxxxxxxxx` (24 characters)
- Add to `youtube-monitor-config.json`

### 3. Python Libraries (auto-installed)
```
google-auth-oauthlib
google-auth-httplib2
google-api-python-client
```

---

## 📊 Reports & Analytics

### Run a Report
```bash
# All-time stats
python ~/.openclaw/workspace/.cache/youtube-monitor-report.py

# Last 2 hours
python ~/.openclaw/workspace/.cache/youtube-monitor-report.py 120

# Last 24 hours
python ~/.openclaw/workspace/.cache/youtube-monitor-report.py 1440
```

### Sample Output
```
📊 YouTube Comment Monitor Report (all time)
============================================================
Total comments: 47
Auto-responses sent: 23
Flagged for review: 3

By Category:
  ❓ questions: 18
  👍 praise: 5
  🚩 sales: 3
  🚫 spam: 15
  ℹ️ neutral: 6

Top Commenters:
  • Alice: 8 comments
  • Bob: 6 comments
  • Charlie: 4 comments

🚩 Sales Inquiries (3):
  • John Doe: We'd like to discuss a partnership...
  • Jane Smith: Are you open to sponsorships?
  • Brand Inc: Collaboration opportunity...
============================================================
```

---

## 🛠️ Common Commands

```bash
# View real-time log
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log

# Run manually (don't wait for cron)
python ~/.openclaw/workspace/.cache/youtube-comment-monitor.py

# Check cron is installed
crontab -l | grep youtube-comment-monitor

# View all comments
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq '.'

# Find comments from specific person
jq 'select(.commenter | contains("Name"))' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Count comments this week
jq 'select(.timestamp > "2026-04-11")' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq -s 'length'

# Verify setup
bash ~/.openclaw/workspace/.cache/youtube-monitor-verify.sh
```

---

## 🧪 Troubleshooting

### "Channel not found"
- Verify channel ID in `youtube-monitor-config.json`
- Must be format: `UCxxxxxxxxxxxxxxxxxxxxxx`

### OAuth token expired
```bash
rm ~/.openclaw/workspace/.cache/youtube-token.json
python ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

### Cron not running
```bash
# Check if installed
crontab -l

# See logs
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log

# Test manually
python ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

### API quota exceeded
- YouTube API allows ~10K requests/day
- Check quotas: console.cloud.google.com → APIs & Services → Quotas
- The monitor uses ~20 requests per run (acceptable)

---

## 🎯 Next Steps

### Immediate
1. Run setup: `bash ~/.openclaw/workspace/.cache/youtube-monitor-install.sh`
2. Wait for first cron run (up to 30 minutes)
3. Check results: `python ~/.openclaw/workspace/.cache/youtube-monitor-report.py`

### First Week
- Review flagged sales inquiries (🚩)
- Adjust keyword detection in config if needed
- Customize response templates

### Ongoing
- Check reports weekly: `python ~/.openclaw/workspace/.cache/youtube-monitor-report.py 10080` (7 days)
- Review top commenters and engagement trends
- Handle flagged sales inquiries manually
- Update templates as your channel grows

---

## 📈 Metrics to Track

- **Total comments/month:** Overall engagement
- **Auto-responses sent:** How many questions you're answering
- **Flagged for review:** Sales opportunities
- **Category breakdown:** What content resonates
- **Top commenters:** Your most engaged audience

---

## 🔄 Customization

All configuration in `youtube-monitor-config.json`:

```json
{
  "channel_id": "UCxxxxxxxxxxxxxxxxxxxxxx",
  "templates": {
    "questions": "Thanks for asking! Check out [LINK] or reply below.",
    "praise": "Your support means the world to us! 🙏"
  },
  "keyword_detection": {
    "questions": ["how to", "cost", "timeline", ...],
    "sales": ["partnership", "sponsor", ...]
  }
}
```

Edit freely—system reloads config every run.

---

## ✅ Deployment Checklist

- [ ] Run setup wizard: `bash youtube-monitor-install.sh`
- [ ] Provide Google OAuth credentials
- [ ] Enter YouTube channel ID
- [ ] First test passes
- [ ] Cron job installed (`crontab -l`)
- [ ] Verify setup: `bash youtube-monitor-verify.sh`
- [ ] Monitor logs for first 24 hours
- [ ] Review and customize templates
- [ ] Set up reporting schedule (weekly review)

---

## 📞 Support

**Quick help:**
```bash
bash ~/.openclaw/workspace/.cache/youtube-monitor-verify.sh
```

**Full documentation:**
- `YOUTUBE-MONITOR-GUIDE.md` — Quick reference
- `youtube-monitor-setup.md` — Detailed guide

**Questions?** Check the guide or review the Python scripts (well-commented).

---

## 📝 File Structure

```
~/.openclaw/workspace/
├── YOUTUBE-MONITOR-GUIDE.md        ← Quick reference
├── YOUTUBE-MONITOR-SUMMARY.md      ← This file
├── youtube-monitor-setup.md        ← Detailed setup
├── youtube-monitor-config.json     ← Configuration
├── .cache/
│   ├── youtube-comment-monitor.py      ← Main script
│   ├── youtube-monitor-report.py       ← Report generator
│   ├── youtube-monitor-install.sh      ← Setup wizard
│   ├── youtube-monitor-verify.sh       ← Verification
│   ├── credentials.json                ← OAuth (you add)
│   ├── youtube-token.json              ← Auth token (auto-created)
│   ├── youtube-comments.jsonl          ← Comment archive
│   ├── seen-comment-ids.json           ← Dedup tracking
│   └── youtube-monitor.log             ← Cron execution log
```

---

**Ready to deploy! 🚀**

Run: `bash ~/.openclaw/workspace/.cache/youtube-monitor-install.sh`
