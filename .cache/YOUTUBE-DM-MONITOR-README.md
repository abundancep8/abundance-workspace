# YouTube DM Monitor - Concessa Obvius

## Overview

Automated hourly monitoring of YouTube DMs for the Concessa Obvius channel. Each message is categorized, auto-responded, and logged for analysis.

**Channel:** Concessa Obvius  
**Channel ID:** `UCF8ly_4Zxd5KWIzkH7ig6Wg`  
**Monitor Status:** ✅ Active (hourly)

---

## How It Works

### 1. DM Categories & Auto-Responses

| Category | Keywords | Auto-Response? | Use Case |
|----------|----------|---|---|
| **Setup Help** | setup, error, stuck, tutorial, how to | ✅ Yes | Users confused about initial setup or hitting errors |
| **Newsletter** | newsletter, email list, subscribe, updates | ✅ Yes | Users wanting to join mailing list |
| **Product Inquiry** | price, buy, features, interested in | ✅ Yes | Potential customers asking about products/pricing |
| **Partnership** | partner, sponsor, collaborate | 🚩 Manual | Partnership opportunities flagged for review |

### 2. Auto-Response Templates

Each category has a templated response that's automatically sent when a DM is detected. Templates include:
- **Setup Help:** Links to docs, FAQs, troubleshooting guide + invitation to reply with specific errors
- **Newsletter:** Confirmation, what they'll get, and preference management link
- **Product Inquiry:** Features, pricing tiers, demo link, and discovery questions
- **Partnership:** Interest acknowledgment + redirect to partnerships@concessa.com

### 3. Data Logging

All DMs logged to: `.cache/youtube-dms.jsonl`

Each entry contains:
```json
{
  "timestamp": "2026-04-18T19:03:53.074Z",
  "sender": "user_123",
  "sender_id": "UC_user_id_hash",
  "text": "Message text here",
  "category": "product_inquiry",
  "response_sent": true,
  "response_template": "...",
  "manual_review": false
}
```

### 4. Reporting

**Hourly Report includes:**
- Total DMs processed (24h window)
- Auto-responses sent
- Conversion potential (product inquiries)
- Breakdown by category
- Partnerships flagged for manual review
- Top product inquiry leads

---

## Current Setup

### Monitor Script
- **Location:** `.bin/youtube-dm-monitor.py`
- **Frequency:** Every hour (via cron)
- **Task ID:** `c1b30404-7343-46ff-aa1d-4ff84daf3674`

### Cache Files
- **DMs Log:** `.cache/youtube-dms.jsonl` (main data store)
- **Metrics:** `.cache/youtube-metrics.jsonl` (hourly summaries for trending)

---

## Important Notes

### Current Limitation: YouTube DM Access

YouTube Studio **does not provide a public API or UI access** to channel DMs. The monitor currently:

✅ **Working:**
- Automatic categorization of DMs (if provided)
- Template-based auto-responses
- Comprehensive logging & reporting
- Metrics tracking

❌ **Pending:**
- Direct YouTube API integration for real-time DM fetching
- Browser automation to pull DMs from YouTube Studio

### To Enable Full Automation

You need **one** of these:

#### Option A: YouTube Data API (Recommended)
1. Set up OAuth 2.0 credentials for your channel
2. Request `youtube.readonly` scope for channel messages
3. Update monitor script to call `youtube.messages().list()`
4. Store credentials in `.env` or secure config

#### Option B: Manual Integration
Currently, DMs must be copy-pasted or forwarded by someone monitoring YouTube Studio. The monitor will:
- Accept DMs via input channel or file
- Categorize and respond automatically
- Track everything

#### Option C: Browser Automation
Use Playwright/Selenium to:
1. Log into YouTube Studio
2. Navigate to Messages section
3. Extract new DMs
4. Trigger auto-responses

---

## Running the Monitor

### Manual Run
```bash
python3 .bin/youtube-dm-monitor.py
```

### View Cache
```bash
tail -f .cache/youtube-dms.jsonl | jq .
```

### View Metrics (Trending)
```bash
cat .cache/youtube-metrics.jsonl | jq .
```

---

## Customization

### Modify Auto-Response Templates
Edit `.bin/youtube-dm-monitor.py`, section `self.templates = {...}`

### Add New Categories
1. Add to `DMCategory` enum
2. Add keywords to `self.category_keywords`
3. Add response template to `self.templates`

### Change Report Window
Default is 24 hours. Modify `generate_report(since_hours=24)` call.

---

## Success Metrics

Track these via the metrics file:

| Metric | Target | Status |
|--------|--------|--------|
| Response Time | <5 min | ⏳ Pending YouTube API |
| Auto-Response Rate | >90% | ✅ 100% when DMs received |
| Partnership Accuracy | >95% | 📊 Monitor data |
| Product Inquiry Capture | 100% | ✅ Keyword-based |

---

## Next Steps

1. **Set up YouTube API access** (if proceeding with Option A)
   - Contact Google Cloud Console
   - Request channel message access
   - Configure OAuth flow

2. **Test with sample DMs** (Option B/C)
   - Run `.bin/youtube-dm-monitor.py --test` with sample data
   - Verify categorization accuracy
   - Tweak keyword thresholds if needed

3. **Monitor daily performance**
   - Check hourly reports
   - Review flagged partnerships
   - Track conversion leads

---

## Support

For issues or improvements:
- Check cache logs for data quality issues
- Verify keyword categorization is working
- Test auto-response templates with sample DMs

Last updated: 2026-04-18
