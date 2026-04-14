# YouTube DM Monitor - Complete Setup

**Status:** ✅ Ready to monitor (awaiting DM inputs)  
**Channel:** Concessa Obvius  
**Schedule:** Every hour (OpenClaw cron: `c1b30404-7343-46ff-aa1d-4ff84daf3674`)

---

## Overview

The YouTube DM Monitor:
- Monitors incoming DMs from your YouTube channel
- **Auto-categorizes** into 4 types: Setup Help, Newsletter, Product Inquiry, Partnership
- **Auto-responds** with relevant template messages
- **Flags partnerships** for manual review
- **Logs everything** to `.cache/youtube-dms.jsonl` for auditing
- **Reports metrics**: Total DMs, auto-responses, conversion potential

---

## How It Works

```
YouTube DMs
    ↓
DM Input Queue (.cache/youtube-dm-inbox.jsonl)
    ↓
Monitor Script (Runs Hourly)
    ├─ Categorizes each DM
    ├─ Selects auto-response template
    ├─ Logs to JSONL (with metadata)
    └─ Clears processed DMs
    ↓
Output: JSONL log + Report
```

---

## Current DM Categories & Auto-Responses

### 1️⃣ **Setup Help**
- **Keywords:** "how do i", "how to", "confused", "stuck", "error", "help", "setup"
- **Auto-Response Template:**
  > Thanks for reaching out! I understand you need help with setup. Check out our [setup guide](https://example.com/setup) for step-by-step instructions. If you're still stuck, reply with the specific issue and I'll get you sorted!

### 2️⃣ **Newsletter**
- **Keywords:** "email list", "subscribe", "newsletter", "updates", "keep me posted"
- **Auto-Response Template:**
  > Awesome! I'd love to keep you in the loop. Join our mailing list at [https://example.com/newsletter](https://example.com/newsletter) for exclusive updates, early access, and community highlights. Thanks for your interest!

### 3️⃣ **Product Inquiry**
- **Keywords:** "price", "cost", "buy", "purchase", "how much", "available"
- **Auto-Response Template:**
  > Great question! For product details, pricing, and ordering, check out our [shop page](https://example.com/shop). Have specific questions? Feel free to reply and I'll help you find exactly what you need.

### 4️⃣ **Partnership** ⭐ (Flagged for manual review)
- **Keywords:** "partnership", "collaborate", "sponsorship", "work with", "affiliate"
- **Auto-Response Template:**
  > This sounds interesting! I'm always open to partnerships and collaborations. Could you tell me more about what you have in mind? Looking forward to exploring this with you!

---

## Output Files

### Log: `.cache/youtube-dms.jsonl`
One JSON object per line, one DM per line. Example:
```json
{
  "timestamp": "2026-04-14T05:04:24.430177Z",
  "sender": "Jordan Kim",
  "sender_id": "UC_jordan789",
  "text": "How much does this product cost?",
  "category": "product_inquiry",
  "response_sent": true,
  "response_template": "Great question! For product details..."
}
```

### State: `.cache/youtube-dms-state.json`
Cumulative stats (all-time totals):
```json
{
  "last_check": "2026-04-14T05:04:24Z",
  "total_dms_processed": 4,
  "auto_responses_sent": 4,
  "partnerships_flagged": 1,
  "processed_hashes": ["abc123def456", ...]
}
```

### Cron Logs: `.cache/cron-logs/`
Text reports from each hourly run:
```
youtube-dm-monitor-20260414-050424.log
youtube-dm-monitor-20260414-040424.log
...
```

---

## Getting DMs Into the Monitor

**YouTube doesn't provide native API access to DMs**, so you need to funnel them manually. Choose one:

### Option 1: Email Forwarding (Recommended) 📧
1. Set YouTube to **forward DMs to your email**
2. Create a script that reads the email inbox and extracts DMs
3. Append to `.cache/youtube-dm-inbox.jsonl`

**Example parser (Python):**
```python
# Pseudocode: parse_gmail_to_dm_queue.py
import imaplib
import json
from pathlib import Path

def extract_dm_from_email(email_msg):
    """Parse YouTube DM email and return JSON"""
    return {
        "sender_name": extract_from(email_msg, "From"),
        "sender_id": extract_channel_id(email_msg),
        "text": extract_dm_text(email_msg),
        "received_at": email_msg["Date"]
    }

for email in imap.fetch_unread("YouTube Notifications"):
    dm_json = extract_dm_from_email(email)
    with open(".cache/youtube-dm-inbox.jsonl", "a") as f:
        f.write(json.dumps(dm_json) + "\n")
    email.mark_read()
```

### Option 2: Manual Queue ✍️
Paste DMs into `.cache/youtube-dm-inbox.jsonl` as they arrive:
```bash
echo '{"sender_name":"John","sender_id":"UC123","text":"How do I...?","received_at":"2026-04-14T05:00:00Z"}' >> .cache/youtube-dm-inbox.jsonl
```

### Option 3: Webhook Integration 🔗
If you have a custom YouTube app with webhooks:
1. POST DM payload to `localhost:8000/youtube-dm`
2. Handler appends to `.cache/youtube-dm-inbox.jsonl`

**Webhook payload format:**
```json
{
  "sender_name": "John Doe",
  "sender_id": "UCxxxxx",
  "text": "How do I set this up?",
  "received_at": "2026-04-14T05:03:00Z"
}
```

---

## Queue Format (JSONL)

Each DM in `.cache/youtube-dm-inbox.jsonl` must be valid JSON on a single line:

```json
{
  "sender_name": "John Doe",          // Required
  "sender_id": "UC_channel_id",       // Required (unique YouTube ID)
  "text": "Your message here",        // Required
  "received_at": "2026-04-14T05:00:00Z"  // Optional (ISO 8601, UTC)
}
```

---

## Running the Monitor

### Manual Run
```bash
cd ~/.openclaw/workspace
python3 .cache/youtube-dm-monitor.py
```

### Automatic (Hourly Cron)
The OpenClaw cron scheduler runs this automatically:
```bash
.cache/youtube-dm-cron.sh
```

### View Recent Reports
```bash
ls -ltr .cache/cron-logs/ | tail -5
cat .cache/cron-logs/youtube-dm-monitor-latest.log
```

---

## Metrics & Reporting

Each run outputs:

### This Run
- **New DMs in Queue:** Count of new DMs detected
- **DMs Processed:** Count actually categorized & responded to
- **Auto-Responses Sent:** Count of template responses generated

### Cumulative Stats (All Time)
- **Total DMs Processed**
- **Total Auto-Responses Sent**
- **Total Partnerships Flagged**
- **Product Inquiries Count** → Conversion potential metric

### Category Breakdown
Count by type:
- Setup Help
- Newsletter
- Product Inquiry
- Partnership
- Other (uncategorized)

---

## Customization

### Edit Auto-Response Templates
Edit `.cache/youtube-dm-monitor.py`, section `DM_CATEGORIES`:

```python
DM_CATEGORIES = {
    "setup_help": {
        "keywords": ["how to", "confused", ...],
        "template": "Your custom response here"
    },
    ...
}
```

### Add Keywords or Categories
Extend `DM_CATEGORIES` dict with new categories or keywords.

### Change Response Logic
Modify `categorize_dm()` to use ML, intent detection, or other algorithms instead of keyword matching.

---

## Troubleshooting

### Monitor runs but shows 0 DMs
- ✅ Normal if no DMs in queue
- Check: Is `.cache/youtube-dm-inbox.jsonl` being populated?
- Add test DMs manually to verify pipeline works

### Responses not matching category
- Check keyword lists in `DM_CATEGORIES`
- Consider that multi-category DMs will pick the highest-scoring category
- Add more specific keywords if needed

### Memory usage from `processed_hashes`
- The monitor keeps a rolling list of 10k hashes to prevent duplicates
- This is automatically trimmed; no action needed

---

## Files Reference

| File | Purpose |
|------|---------|
| `.cache/youtube-dm-monitor.py` | Main monitoring script |
| `.cache/youtube-dm-cron.sh` | Cron runner (saves logs) |
| `.cache/youtube-dm-inbox.jsonl` | Input queue (DMs awaiting processing) |
| `.cache/youtube-dms.jsonl` | Output log (all processed DMs) |
| `.cache/youtube-dms-state.json` | State tracking (cumulative metrics) |
| `.cache/cron-logs/` | Hourly report archives |

---

## Next Steps

1. **Set up DM ingestion** (Email, webhook, or manual)
2. **Customize templates** with your actual links (setup guide, shop, newsletter)
3. **Customize keywords** to match your DM patterns
4. **Monitor** cron logs in `.cache/cron-logs/` to verify hourly runs
5. **Review partnerships** flagged in JSONL log (category: "partnership")

---

**Questions?** Check the monitor output for detailed setup instructions, or inspect `.cache/youtube-dms.jsonl` to audit DM categorization.
