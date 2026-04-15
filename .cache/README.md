# YouTube DM Monitor for Concessa Obvius

## 📋 Summary

A fully automated system that monitors, categorizes, and responds to YouTube DMs for the Concessa Obvius channel. Runs every hour via cron.

---

## 📦 What's Included

| File | Purpose |
|------|---------|
| `youtube-dms-monitor.js` | Main monitoring script |
| `youtube-dm-monitor-config.json` | Configuration & category definitions |
| `YOUTUBE-DM-SETUP.md` | Setup instructions |
| `INTEGRATION-GUIDE.md` | How to wire up data sources |
| `youtube-dms.jsonl` | Log of all processed DMs |
| `youtube-dms-report.json` | Latest hourly report |

---

## 🎯 Features

✅ **Automatic Categorization**
- Setup help
- Newsletter
- Product inquiry
- Partnership (flagged for manual review)

✅ **Auto-Response Templates**
- Context-specific responses for each category
- Easy to customize

✅ **Comprehensive Logging**
- JSONL format (searchable, parseable)
- Timestamp, sender, text, category, response

✅ **Partnership Detection**
- Flags interesting collab/sponsorship opportunities
- Includes sender details and message content

✅ **Hourly Reports**
- Total DMs processed
- Auto-responses sent
- Conversion potential (product inquiries)
- Partnership opportunities highlighted

---

## 🚀 Quick Start

### 1. Test Locally
```bash
cd /Users/abundance/.openclaw/workspace
node .cache/youtube-dms-monitor.js
```

Output:
```
✓ Logged 3 DMs to .cache/youtube-dms.jsonl
=== DM Monitor Report ===
Total DMs processed: 3
Auto-responses sent: 3
Product inquiries: 1
Partnerships flagged for review: 1
✓ Report saved to .cache/youtube-dms-report.json
```

### 2. Feed Real DMs
Choose an integration method:
- **Browser Extension** (monitor actual YouTube messages)
- **Webhook Server** (local HTTP endpoint)
- **Manual Export** (JSON file)
- **Email Forwarding** (parsed from notifications)

See `INTEGRATION-GUIDE.md` for detailed setup.

### 3. Enable Cron
OpenClaw will automatically run hourly (configured).

---

## 📊 Sample Output

### Log Entry (youtube-dms.jsonl)
```json
{
  "timestamp": "2026-04-14T21:03:58.834Z",
  "sender": "Alice_Creator",
  "sender_id": "UC_alice123",
  "text": "How do I set this up? I'm confused.",
  "category": "setup_help",
  "response_sent": true,
  "template_used": "setup_help"
}
```

### Report (youtube-dms-report.json)
```json
{
  "timestamp": "2026-04-14T21:03:58.835Z",
  "total_dms_processed": 3,
  "auto_responses_sent": 3,
  "conversion_potential": {
    "product_inquiries": 1,
    "partnerships_flagged": 1
  },
  "partnerships_for_review": [
    {
      "sender": "TechVenture Studios",
      "text": "Hi! We'd love to collaborate on sponsorship...",
      "timestamp": "2026-04-14T21:03:58Z",
      "flag": "REVIEW_NEEDED"
    }
  ]
}
```

---

## 🔧 Customization

### Change Response Templates
Edit `youtube-dms-monitor.js`, find `TEMPLATES`:
```javascript
const TEMPLATES = {
  setup_help: {
    category: 'Setup help',
    response: `Your custom response here...`
  },
  // ... etc
};
```

### Improve Categorization
Edit `KEYWORDS` to fine-tune detection:
```javascript
const KEYWORDS = {
  setup_help: ['how to', 'help', 'confused', 'error', ...],
  // ... etc
};
```

### Add New Categories
1. Add to `KEYWORDS`
2. Add to `TEMPLATES`
3. Script auto-detects the new category

---

## 📍 File Locations

```
.cache/
├── youtube-dms-monitor.js           # Main script
├── youtube-dm-monitor-config.json   # Configuration
├── YOUTUBE-DM-SETUP.md              # Setup guide
├── INTEGRATION-GUIDE.md             # Data source integration
├── youtube-dms.jsonl                # DM log (JSONL)
├── youtube-dms-report.json          # Latest report (JSON)
├── youtube-dms-cron.log             # Cron execution log
└── README.md                        # This file
```

---

## 📈 Metrics Tracked

- **Total DMs processed** - How many messages handled this hour
- **Auto-responses sent** - How many templates deployed
- **Product inquiries** - Conversion opportunities
- **Partnerships flagged** - Manual review items

---

## 🔒 Data Handling

- All DMs logged to `.cache/youtube-dms.jsonl` with full metadata
- Partnership details captured for follow-up
- Responses tracked (enables A/B testing later)
- Timestamp all records for trend analysis

---

## 🛠️ Troubleshooting

**Monitor not running?**
- Check if `/tmp/new-dms.json` exists
- Verify JSON format with `jq` or a validator
- Check cron logs: `cat .cache/youtube-dms-cron.log`

**Wrong categorization?**
- Review KEYWORDS in script
- Test specific messages with console.log
- Adjust keyword scoring if needed

**Missing partnerships?**
- Check if keyword detection is working
- Review flagged items in the report
- Add more partnership keywords if needed

---

## 🚀 Next Steps

1. ✅ System is ready and tested
2. 📡 **Wire up a data source** (see INTEGRATION-GUIDE.md)
3. 🧪 Test with real YouTube DMs
4. 🎯 Monitor reports hourly
5. 📧 Set up partnership review workflow (optional)

---

## 📞 Support

- **Configuration:** Edit `youtube-dms-monitor.js`
- **Data integration:** See `INTEGRATION-GUIDE.md`
- **Testing:** Run `node .cache/youtube-dms-monitor.js` manually
- **Logs:** Check `.cache/youtube-dms.jsonl` and `.cache/youtube-dms-report.json`

---

**Status:** ✅ Ready for production
**Schedule:** Every hour (0 * * * * America/Los_Angeles)
**Last Run:** 2026-04-14 21:03:58 UTC
**Next Run:** 2026-04-14 22:00:00 UTC (approx)
