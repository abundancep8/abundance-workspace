# YouTube DM Monitor - Complete Setup Guide

## Overview

This system monitors YouTube DMs for the **Concessa Obvius** channel, automatically categorizes messages, sends templated responses, and flags high-value partnership opportunities.

**Location:** `.cache/youtube_dm_monitor.py`

---

## 🚀 Quick Start (5 minutes)

### Test with Mock Data
```bash
cd ~/.openclaw/workspace
python3 .cache/youtube_dm_monitor.py --mock-mode
```

This generates sample DM logs and reports without requiring API credentials.

### View Last Report
```bash
python3 .cache/youtube_dm_monitor.py --report
```

---

## 📋 What Gets Logged

### 1. **youtube-dms.jsonl** - Complete DM Log
JSONL format (one entry per line):
```json
{
  "timestamp": "2026-04-14T06:04:59.538630Z",
  "sender": "Sam Rodriguez",
  "sender_id": "UCsample001",
  "text": "Hi! I've been trying to set this up but I'm stuck on step 3...",
  "category": "setup_help",
  "response_sent": true,
  "partnership_score": null
}
```

**Fields:**
- `timestamp` - When DM was received
- `sender` - Sender's name
- `sender_id` - YouTube channel ID
- `text` - First 500 chars of message
- `category` - Auto-detected category
- `response_sent` - If auto-response was generated
- `partnership_score` - (0-100) for partnership inquiries

### 2. **youtube-flagged-partnerships.jsonl** - High-Priority Partnerships
```json
{
  "timestamp": "2026-04-14T06:04:59.538963Z",
  "sender": "TechVenture Studios",
  "sender_id": "UCTECH_studio",
  "text": "Hi Concessa team! We're a mid-sized digital marketing agency...",
  "partnership_score": 70,
  "signal": "🔴 Contains 'brand' + 🟡 Contains 'co-' + 🟢 Looks like a business + ...",
  "status": "pending_review"
}
```

**Scoring Logic:**
- **High signals (25 pts):** brand, sponsorship, partnership, ambassador
- **Medium signals (15 pts):** collab, affiliate, cross-promotion
- **Other signals (5-10 pts):** company name, message length, intent words
- **Threshold:** Flagged if score ≥ 30

### 3. **youtube-dms-state.json** - Monitoring State
```json
{
  "last_check": "2026-04-14T06:05:00Z",
  "total_dms_processed": 8,
  "auto_responses_sent": 8,
  "partnerships_flagged": 2,
  "processed_hashes": ["abc123def456", ...],
  "status": "success"
}
```

---

## 🎯 DM Categories & Auto-Responses

The script automatically categorizes and responds to:

### 1. **Setup Help** 🔧
**Keywords:** how do i, setup, error, confused, stuck, help, tutorial...
**Response:** Links to setup guide + video tutorial + support email

### 2. **Newsletter** 📧
**Keywords:** subscribe, newsletter, email list, keep me posted, sign up...
**Response:** Newsletter signup link + benefits

### 3. **Product Inquiry** 🛍️
**Keywords:** price, cost, buy, how much, shipping, in stock, deal...
**Response:** Shop link + pricing + shipping info

### 4. **Partnership** 🤝
**Keywords:** partnership, sponsor, collab, brand deal, promote...
**Response:** Interest confirmation + request for details
**Action:** Flagged for manual review if score ≥ 30

---

## 📨 DM Input Methods

Choose one (or combine multiple):

### **Option 1: Email Forwarding** (Recommended)
Forward YouTube DM notifications to a monitored email, then use `youtube-dm-email-parser.py`:
```bash
python3 .cache/youtube-dm-email-parser.py
```

**Setup:**
1. Forward YouTube DM notification emails to a Gmail account
2. Create Gmail credentials:
   - Go to Google Cloud Console
   - Create OAuth credentials (Desktop app)
   - Download JSON → `.secrets/gmail-credentials.json`
3. Run parser (first run will ask for OAuth authorization)
4. Parser appends to `.cache/youtube-dm-inbox.jsonl`
5. Monitor script processes the queue

### **Option 2: Webhook Receiver**
Create a simple webhook that receives DMs from YouTube:
```bash
# Listen on http://localhost:8000/youtube-dm
python3 .cache/youtube-dm-webhook.py &
```

POST JSON to `http://localhost:8000/youtube-dm`:
```json
{
  "sender_name": "John Doe",
  "sender_id": "UCxxxxx",
  "text": "Your message here",
  "received_at": "2026-04-14T12:00:00Z"
}
```

### **Option 3: Manual Queue**
Append DMs directly to `.cache/youtube-dm-inbox.jsonl`:
```bash
cat >> ~/.openclaw/workspace/.cache/youtube-dm-inbox.jsonl << 'EOF'
{"sender_name": "John Doe", "sender_id": "UCxxxxx", "text": "Help!", "received_at": "2026-04-14T12:00:00Z"}
EOF
```

---

## ⏰ Scheduling (Cron Job)

### **Hourly Monitor**
Add to crontab:
```bash
crontab -e
```

Add this line:
```bash
0 * * * * cd /Users/abundance/.openclaw/workspace && python3 .cache/youtube_dm_monitor.py >> .cache/youtube-dms-cron.log 2>&1
```

This runs at the top of every hour (12:00, 1:00, 2:00, etc.)

### **Verify Cron Job**
```bash
crontab -l
```

### **Check Logs**
```bash
tail -f ~/.openclaw/workspace/.cache/youtube-dms-cron.log
```

---

## 🔧 Advanced Usage

### **Mock Mode** (Test without API)
```bash
python3 .cache/youtube_dm_monitor.py --mock-mode
```
Uses sample DM data. Perfect for testing categorization and responses.

### **Queue-Only Mode** (Skip API)
```bash
python3 .cache/youtube_dm_monitor.py --queue-only
```
Processes `.cache/youtube-dm-inbox.jsonl` only.

### **API-Only Mode** (YouTube API, if available)
```bash
python3 .cache/youtube_dm_monitor.py --api-only
```
Attempts to fetch directly from YouTube API (experimental).

### **Verbose Output**
```bash
python3 .cache/youtube_dm_monitor.py -v
```

### **Show Last Report**
```bash
python3 .cache/youtube_dm_monitor.py --report
```

---

## 📊 Sample Output

```
================================================================================
🎥 YOUTUBE DM MONITOR REPORT - Concessa Obvius
================================================================================
⏱️  Report Time: 2026-04-14T06:04:59Z
✅ Status: SUCCESS

📊 THIS RUN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New DMs in Queue:           4
DMs Processed:              4
Auto-Responses Sent:        4
Partnerships Flagged:       1

📈 CUMULATIVE STATS (All Time)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total DMs Processed:        8
Total Auto-Responses:       8
Total Partnerships Flagged: 2

💰 CONVERSION POTENTIAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Product Inquiries (This Run): 1
Estimated Conversion Rate:   25.0%
Revenue Potential:           1 potential customers

📂 CATEGORY BREAKDOWN (This Run)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setup Help 🔧..................... █ 1
Newsletter Signup 📧............ █ 1
Product Inquiries 🛍️........... █ 1
Partnership Opportunities 🤝... █ 1
```

---

## 🔐 Authentication

### YouTube API Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project: "Concessa Obvius"
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials (Desktop app)
5. Download JSON file
6. Save to: `.secrets/youtube-credentials.json`

**First run** will open browser for OAuth authorization and save token to `.secrets/youtube-token.json`.

### Gmail Credentials (For Email Parsing)
1. Same process as YouTube API
2. Select "Gmail API" instead
3. Save to: `.secrets/gmail-credentials.json`

---

## 📁 File Structure

```
.cache/
├── youtube_dm_monitor.py          ← Main script (new)
├── youtube-dms.jsonl              ← All DM logs
├── youtube-flagged-partnerships.jsonl ← High-priority partnerships
├── youtube-dms-state.json         ← Monitoring state
├── youtube-dms-report.txt         ← Last report
├── youtube-dm-inbox.jsonl         ← Input queue (processed & cleared each run)
├── youtube-dm-inbox-backup-*.jsonl ← Queue backups for audit trail
├── youtube-dms-cron.log           ← Cron execution logs
└── YOUTUBE_DM_MONITOR_SETUP.md    ← This file

.secrets/
├── youtube-credentials.json       ← YouTube OAuth config
├── youtube-token.json             ← YouTube OAuth token (auto-created)
├── gmail-credentials.json         ← Gmail OAuth config (optional)
└── gmail-token.json               ← Gmail OAuth token (optional)
```

---

## 🔄 Workflow

```
1. DM Arrives in YouTube
          ↓
2. Email Forwarding / Webhook / Manual Entry
          ↓
3. Appended to .cache/youtube-dm-inbox.jsonl
          ↓
4. Hourly Cron Job Triggers
          ↓
5. youtube_dm_monitor.py Processes Queue
          ├─ Categorize DM (setup, newsletter, product, partnership, other)
          ├─ Generate auto-response if applicable
          ├─ Score partnership potential
          └─ Log to .cache/youtube-dms.jsonl
          ↓
6. If Partnership Score ≥ 30
          └─ Flag to .cache/youtube-flagged-partnerships.jsonl for manual review
          ↓
7. Clear Queue & Generate Report
          └─ Output to .cache/youtube-dms-report.txt
```

---

## ⚠️ Troubleshooting

### **No DMs being processed**
1. Check queue file exists: `.cache/youtube-dm-inbox.jsonl`
2. Verify it has content: `cat .cache/youtube-dm-inbox.jsonl`
3. Ensure proper JSON format (one per line)

### **API authentication fails**
1. Delete `.secrets/youtube-token.json`
2. Re-run script to re-authenticate
3. Check credentials at `.secrets/youtube-credentials.json`

### **Cron job not running**
1. Verify crontab: `crontab -l`
2. Check logs: `tail -f .cache/youtube-dms-cron.log`
3. Test manually: `python3 .cache/youtube_dm_monitor.py`

### **Missing dependencies**
```bash
# For YouTube API support
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# For Gmail email parsing
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## 🎯 Next Steps

1. ✅ **Test:** Run with `--mock-mode` to verify setup
2. ✅ **Choose input method:** Email forwarding, webhook, or manual queue
3. ✅ **Set up cron:** Schedule hourly runs
4. ✅ **Customize templates:** Edit response text in script
5. ✅ **Monitor:** Check `youtube-flagged-partnerships.jsonl` daily
6. ✅ **Integrate:** Connect to CRM/email for customer management

---

## 📞 Support

For issues:
1. Check this guide
2. Review logs: `.cache/youtube-dms-cron.log`
3. Test manually: `python3 .cache/youtube_dm_monitor.py -v`
4. Check JSON format in queue file

---

**Version:** 2.0  
**Last Updated:** 2026-04-14  
**Status:** Production-Ready
