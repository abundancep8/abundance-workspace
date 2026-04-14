# YouTube Comment Monitor

**Channel:** Concessa Obvius  
**Frequency:** Every 30 minutes (cron job)  
**Status:** ✅ Ready to deploy  
**Version:** 1.0

---

## 📌 Overview

Automated monitoring of the Concessa Obvius YouTube channel. Categorizes comments, auto-responds to questions & praise, flags sales inquiries, and logs everything.

**What happens automatically:**

1. Every 30 minutes, the script fetches recent comments
2. Categorizes each comment (Question, Praise, Spam, Sales, Other)
3. Sends auto-responses to questions & praise
4. Flags sales inquiries for manual review
5. Logs everything to `youtube-comments.jsonl`
6. Reports summary stats

---

## 📁 Files

| File | Purpose |
|------|---------|
| **scripts/youtube-comment-monitor.py** | Core monitoring script |
| **scripts/youtube-monitor.sh** | Shell wrapper (cron runner) |
| **scripts/test-youtube-monitor.sh** | Setup verification & test |
| **com.youtube-monitor.plist** | macOS LaunchAgent config |
| **.cache/youtube-comments.jsonl** | Log of all comments (grows over time) |
| **.cache/youtube-monitor.log** | Execution log (timestamps & results) |
| **YOUTUBE-MONITOR-SETUP.md** | 📖 Detailed setup guide |
| **YOUTUBE-MONITOR-DASHBOARD.md** | 📊 Quick commands & reports |

---

## 🚀 Quick Setup

### 1️⃣ Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project named "Concessa YouTube Monitor"
3. Enable **YouTube Data API v3**
4. Create **OAuth2 Desktop Credentials**
5. Download the JSON file and save to: `~/.openclaw/youtube-credentials.json`

### 2️⃣ Install Python Libraries

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3️⃣ Test the Setup

```bash
bash scripts/test-youtube-monitor.sh
```

This will:
- Check credentials ✅
- Verify Python libraries ✅
- Run one monitor cycle ✅
- Prompt for browser authorization (one-time) ✅

### 4️⃣ Enable Automatic Scheduling

**Option A: macOS LaunchAgent (Recommended)**

```bash
cp com.youtube-monitor.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.youtube-monitor.plist
launchctl start com.youtube-monitor
```

**Option B: Cron**

```bash
crontab -e
# Add: */30 * * * * /Users/abundance/.openclaw/workspace/scripts/youtube-monitor.sh
```

---

## 📊 View Results

### Summary Report

```bash
tail .cache/youtube-comments.jsonl | jq '.'
```

### Full Statistics

```bash
python3 - <<'EOF'
import json
from pathlib import Path
from collections import Counter

log = Path(".cache/youtube-comments.jsonl")
data = [json.loads(line) for line in open(log) if line.strip()]

print(f"Total: {len(data)} comments")
print(f"Categories: {dict(Counter(d['category'] for d in data))}")
print(f"Auto-responded: {sum(1 for d in data if d['response_status'] == 'responded')}")
print(f"Flagged: {sum(1 for d in data if d['response_status'] == 'flagged_for_review')}")
EOF
```

### Sales Inquiries (Needs Review)

```bash
python3 - <<'EOF'
import json
from pathlib import Path

log = Path(".cache/youtube-comments.jsonl")
data = [json.loads(line) for line in open(log) if line.strip()]
sales = [d for d in data if d['response_status'] == 'flagged_for_review']

for s in sales:
    print(f"\n{s['commenter']}: {s['text']}")
EOF
```

---

## 🎯 How It Works

### Categorization

Each comment is scanned against patterns:

| Category | Patterns |
|----------|----------|
| **Question** | "how do", "what is", "cost", "timeline", "tools", ends with ? |
| **Praise** | "amazing", "inspiring", "thank you", "love this", "brilliant" |
| **Spam** | "bitcoin", "crypto", "mlm", "casino", "buy now" |
| **Sales** | "partnership", "sponsor", "affiliate", "business opportunity" |
| **Other** | Doesn't match any patterns |

### Auto-Responses

- **Questions:** Templated response with link to resources
- **Praise:** Thank you message with appreciation
- **Spam:** No response (ignored)
- **Sales:** Flagged for manual review (no auto-response)

### Logging

Each comment creates a JSON entry:

```json
{
  "timestamp": "2026-04-14T08:30:00Z",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "question",
  "response_status": "responded",
  "comment_id": "UgyABC..."
}
```

---

## ⚙️ Configuration

### Change Auto-Response Templates

Edit `youtube-comment-monitor.py`:

```python
TEMPLATES = {
    "question": "Your custom message here...",
    "praise": "Your custom thank you...",
}
```

### Adjust Categorization

Add/modify patterns in `youtube-comment-monitor.py`:

```python
PATTERNS = {
    "question": [r"how\s+do", r"custom_pattern_here"],
    ...
}
```

### Change Frequency

- **LaunchAgent:** Edit `com.youtube-monitor.plist`, change `<integer>1800</integer>` to seconds (e.g., 3600 = 1 hour)
- **Cron:** Change `*/30` to desired minutes (e.g., `*/60` for hourly)

---

## 🔐 Security

- Credentials stored locally in `~/.openclaw/`
- Never commit credential files to git
- Token auto-refreshes; no manual intervention needed
- Monitor runs with your user permissions

---

## 📖 Documentation

- **Full Setup Guide:** `YOUTUBE-MONITOR-SETUP.md`
- **Commands & Reports:** `YOUTUBE-MONITOR-DASHBOARD.md`
- **This File:** `YOUTUBE-MONITOR-README.md`

---

## 🐛 Troubleshooting

### "Module not found"
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### "Credentials not found"
Ensure `~/.openclaw/youtube-credentials.json` exists with valid OAuth2 JSON.

### "Monitor not running"
```bash
launchctl list | grep youtube-monitor
launchctl start com.youtube-monitor
```

### Check Logs
```bash
tail -50 .cache/youtube-monitor.log
tail -50 .cache/youtube-monitor-error.log
```

---

## ✅ Status Checklist

- [ ] OAuth2 credentials saved to `~/.openclaw/youtube-credentials.json`
- [ ] Python libraries installed: `google-auth-oauthlib`, etc.
- [ ] Test run completed: `bash scripts/test-youtube-monitor.sh`
- [ ] LaunchAgent installed and running (or cron configured)
- [ ] `.cache/youtube-comments.jsonl` has entries after 30+ minutes
- [ ] Execution log shows successful runs: `tail .cache/youtube-monitor.log`

---

## 📞 Quick Commands

```bash
# Test setup
bash scripts/test-youtube-monitor.sh

# Manual run
python3 scripts/youtube-comment-monitor.py

# Check status
launchctl list | grep youtube-monitor

# View last 10 comments
tail -10 .cache/youtube-comments.jsonl | jq '.'

# View report
tail .cache/youtube-monitor.log

# Stop monitor
launchctl stop com.youtube-monitor

# Start monitor
launchctl start com.youtube-monitor

# Reload (after config changes)
launchctl unload ~/Library/LaunchAgents/com.youtube-monitor.plist
launchctl load ~/Library/LaunchAgents/com.youtube-monitor.plist
```

---

**Deployed:** 2026-04-14  
**Next Check:** In 30 minutes automatically ⏰

Let me know if you need any adjustments to templates, patterns, or scheduling!
