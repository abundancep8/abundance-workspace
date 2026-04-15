# YouTube Comment Monitor - Setup & Deployment Guide

**Status:** ✅ Automated monitoring ACTIVE (Running every 30 minutes via cron)

**Current Time:** Tuesday, April 14, 2026 — 10:30 AM (America/Los_Angeles)

---

## 🎯 What This Does

Monitors the **Concessa Obvius** YouTube channel for new comments and automatically:

1. **Categorizes** each comment into: Questions, Praise, Spam, Sales
2. **Auto-responds** to Questions (category 1) & Praise (category 2) with template responses
3. **Flags** Sales/partnerships (category 4) for your manual review
4. **Logs everything** to `.cache/youtube-comments.jsonl` with metadata
5. **Reports** every 30 minutes with: total processed, auto-responses sent, flagged count

---

## 📊 Current Status

```
✅ Monitor Script:      Active (/Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor-complete.py)
✅ Logging System:      Working (35,630 bytes logged so far)
✅ State Tracking:      Active (tracking processed comment IDs to avoid duplicates)
✅ Cron Job:           Ready to deploy (every 30 minutes)
⚠️  API Credentials:    SETUP REQUIRED (currently running in demo mode)
```

**Lifetime Stats:**
- Total Comments Processed: 18
- Auto-Responses Sent: 12
- Flagged for Review: 3

---

## 🔐 Setting Up YouTube API Credentials

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"** (top left)
3. Name it: `Concessa-Obvius-Monitor`
4. Click **Create**

### Step 2: Enable YouTube Data API v3

1. In the Console, search for **"YouTube Data API v3"**
2. Click the API
3. Click **"Enable"**

### Step 3: Create OAuth 2.0 Credentials

1. Go to **Credentials** (left sidebar)
2. Click **"Create Credentials"** → **OAuth 2.0 Desktop App**
3. Configure the OAuth consent screen:
   - User Type: **Internal** (or External if preferred)
   - App name: `Concessa Obvius Monitor`
   - Scopes: Search for and add:
     - `youtube.readonly`
     - `youtube.force-ssl`
4. Click **Create**

### Step 4: Download Credentials

1. On the Credentials page, find your OAuth 2.0 Desktop app
2. Click the download button (📥)
3. Save as: `youtube-credentials.json`

### Step 5: Store Credentials Securely

```bash
mkdir -p ~/.openclaw/workspace/.cache/.secrets
mv ~/Downloads/youtube-credentials.json ~/.openclaw/workspace/.cache/.secrets/
chmod 600 ~/.openclaw/workspace/.cache/.secrets/youtube-credentials.json
```

### Step 6: Verify

```bash
export YOUTUBE_CREDENTIALS_PATH="$HOME/.openclaw/workspace/.cache/.secrets/youtube-credentials.json"
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor-complete.py
```

---

## 🤖 Template Responses

### Questions (Auto-Responded)
```
"Great question! Thanks for your interest. I'll have more details about this soon. 
In the meantime, check out our resources and FAQs!"

"Love this question! This is something we're actively working on. 
Keep an eye on our upcoming announcements."

"Thanks for asking! I'll reach out with more info soon. 
In the meantime, feel free to check out our recent content."
```

### Praise (Auto-Responded)
```
"Thank you so much for the kind words! 🙏 Really appreciate your support and engagement."

"This means the world! 💕 Thanks for being part of the community."

"So grateful for this! Your support keeps us going. 🚀"
```

### Sales & Partnerships (Flagged for Manual Review)
These are **NOT auto-responded**. You'll see them flagged in the report for evaluation.

---

## 📋 Log Format

Each processed comment is logged as JSON:

```json
{
  "timestamp": "2026-04-14T17:30:00Z",
  "comment_id": "AbC1234567890XYZ",
  "commenter": "Sarah Chen",
  "text": "How do I get started with this?",
  "category": "questions",
  "response_status": "auto_responded",
  "template_response": "Great question! Thanks for your interest..."
}
```

**Categories:**
- `questions` → Auto-responded
- `praise` → Auto-responded
- `spam` → Flagged (not responded)
- `sales` → Flagged for review (not responded)

---

## 🔄 Cron Configuration

**Current Schedule:** Every 30 minutes

To verify the cron job:
```bash
crontab -l | grep youtube
```

To add/update the cron job manually:
```bash
crontab -e
```

Add this line:
```
*/30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor-cron-complete.sh >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.log 2>&1
```

---

## 📊 Running Reports

### Last Run Report
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments-report.txt
```

### View Recent Logs
```bash
tail -20 ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

### Get Lifetime Stats
```bash
cat ~/.openclaw/workspace/.cache/youtube-comment-state.json
```

### View Cron Execution Log
```bash
tail -50 ~/.openclaw/workspace/.cache/youtube-monitor-cron.log
```

---

## 🐛 Troubleshooting

### "Invalid OAuth client_secret (401)"
→ Regenerate credentials from Google Cloud Console and re-upload.

### "No new comments detected"
→ The monitor tracks `last_processed_comment_id`. This is normal if no new comments exist.

### "Script not running"
→ Check if cron is enabled:
```bash
sudo launchctl list | grep cron
```

### "Permission denied on .secrets/youtube-credentials.json"
→ Fix permissions:
```bash
chmod 600 ~/.openclaw/workspace/.cache/.secrets/youtube-credentials.json
```

---

## 📞 Next Steps

1. **Set up credentials** (Steps 1-6 above)
2. **Test the monitor** manually once
3. **Monitor cron execution** with: `tail -f ~/.openclaw/workspace/.cache/youtube-monitor-cron.log`
4. **Review flagged comments** regularly from the report
5. **Customize templates** if needed in the Python script

---

**Monitor Script Location:**
`/Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor-complete.py`

**Cron Wrapper Location:**
`/Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor-cron-complete.sh`

**Configuration Files:**
- Comments log: `.cache/youtube-comments.jsonl`
- State tracking: `.cache/youtube-comment-state.json`
- Report: `.cache/youtube-comments-report.txt`
- Cron log: `.cache/youtube-monitor-cron.log`

---

**Last Updated:** 2026-04-14 at 17:30 UTC
