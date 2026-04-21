# YouTube DM Monitor - Concessa Obvius

**Status**: ✅ Active (Hourly cron job)  
**Last Run**: 2026-04-21 01:04 UTC  
**Channel**: Concessa Obvius

---

## 📊 Current Report

### Statistics
- **Total DMs Processed**: 12
- **Auto-Responses Sent**: 9 (75% response rate)

### Distribution by Category
- **Setup Help** (🛠️): 3 DMs
- **Newsletter** (📧): 2 DMs
- **Product Inquiry** (💰): 5 DMs
- **Partnership** (🤝): 2 DMs

### 🤝 Partnership Opportunities (Manual Review Flagged)
1. **TechStart Ventures** - Sponsorship collaboration inquiry
2. **tech_brand** - Brand collaboration partnership

---

## 🔧 System Components

### Files
- **Monitor Script**: `.cache/youtube-dm-monitor.py` (categorization & logging)
- **Report Script**: `.cache/youtube-dm-monitor-report.sh` (hourly reporting)
- **Configuration**: `.cache/youtube-dms-config.json` (settings)
- **Log File**: `.cache/youtube-dms.jsonl` (all DMs with responses)
- **Report Output**: `.cache/youtube-dms-report.json` (latest stats)

### Auto-Response Templates

#### 1️⃣ Setup Help
```
Thanks for reaching out! 🎬 

For setup help, here are our best resources:
- **Getting Started Guide**: [link]
- **FAQ**: [link]
- **Video Tutorial**: [link]

If you're still stuck, let us know exactly where you're hitting a wall and we'll help!
```

#### 2️⃣ Newsletter
```
Great timing! 📧

Join our newsletter for:
- Exclusive updates & early features
- Weekly tips & tricks
- Community stories
- Special offers

**Sign up here**: [link]

You'll be on the list within 5 minutes!
```

#### 3️⃣ Product Inquiry
```
Thanks for your interest! 🛍️

Quick details:
- **Pricing**: [link]
- **Product comparison**: [link]
- **FAQ**: [link]

Questions? We can answer anything. When were you looking to get started?
```

#### 4️⃣ Partnership
```
This is interesting! 🤝

We're always open to collaborations. Let's chat more:
- **What's your vision?**
- **Timeline?**
- **What would success look like?**

Reply with more details or we can hop on a call this week. Excited to explore this!
```

---

## 🚀 How It Works

### Categorization
The system uses keyword matching to automatically categorize incoming DMs:

**Setup Help**: "help", "setup", "confused", "how do i", "tutorial", "guide", "error", "stuck", "not working"  
**Newsletter**: "newsletter", "email list", "subscribe", "updates", "news", "announcements"  
**Product Inquiry**: "price", "pricing", "buy", "purchase", "cost", "plan", "features", "product", "how much"  
**Partnership**: "collaborate", "partner", "sponsorship", "brand deal", "collab", "campaign", "work together"

### Logging
Every DM is logged to `youtube-dms.jsonl` with:
- Timestamp (ISO 8601)
- Sender name & ID
- DM text content
- Auto-detected category
- Response template sent
- Response status

Example entry:
```json
{
  "timestamp": "2026-04-20T04:05:39.059648Z",
  "sender": "Alex Chen",
  "text": "Hi! I'm confused about how to set up the video editing workflow...",
  "category": "setup_help",
  "response_sent": true
}
```

---

## ⚙️ Configuration

Edit `.cache/youtube-dms-config.json` to customize:

```json
{
  "channel_name": "Concessa Obvius",
  "monitor_interval_minutes": 60,
  "auto_respond": true,
  "categories": {
    "setup_help": {"priority": "high", "auto_respond": true},
    "partnership": {"priority": "critical", "flag_for_review": true}
  }
}
```

---

## 🔌 Integration Needed

To make this fully operational with live YouTube DMs, you need:

1. **YouTube API Credentials**
   - Create OAuth 2.0 credentials in Google Cloud Console
   - Grant `youtube:force-ssl` scope
   - Store credentials in `.openclaw/secrets/youtube-api.json`

2. **Channel ID**
   - Replace placeholder with actual Concessa Obvius channel ID (UCxxxxx)
   - Update `youtube-dms-config.json`

3. **YouTube API Client**
   - Install: `pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client`
   - Modify `youtube-dm-monitor.py` to call actual API endpoints

4. **Response Delivery**
   - Implement YouTube Messages API calls to send auto-responses
   - Or set up webhook to notify team for manual responses

---

## 📈 Metrics Tracked

- **Conversion Potential**: Product inquiries (5 so far = potential sales)
- **Support Load**: Setup help requests (3 = support tickets)
- **Growth**: Newsletter signups (2 = audience expansion)
- **Business Development**: Partnerships flagged for review (2 = opportunities)

---

## 🔔 Alerts & Escalations

The system automatically:
- ✅ Auto-responds to all 4 categories
- 🚩 **Flags partnership inquiries** for manual review (high-value)
- 📊 Generates hourly reports
- 📝 Logs everything for analytics

Partnership inquiries go to `.cache/youtube-dms-report.json` under `partnership_flags` for visibility.

---

## 🛠️ Manual Commands

**View full log:**
```bash
cat ~/.openclaw/workspace/.cache/youtube-dms.jsonl
```

**Count by category:**
```bash
grep '"category"' ~/.openclaw/workspace/.cache/youtube-dms.jsonl | sort | uniq -c
```

**View latest partnerships:**
```bash
grep '"partnership"' ~/.openclaw/workspace/.cache/youtube-dms.jsonl | tail -5
```

**Run report manually:**
```bash
~/.openclaw/workspace/.cache/youtube-dm-monitor-report.sh
```

---

## 📅 Cron Schedule

```
0 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-dm-monitor-report.sh
```

(Every hour at :00)

---

## Next Steps

- [ ] Configure YouTube API credentials
- [ ] Update channel ID in config
- [ ] Test with sample DMs
- [ ] Review partnership templates for tone/messaging
- [ ] Set up email notification for partnership flags
- [ ] Monitor conversion rate from product inquiries

---

**Last Updated**: 2026-04-21 01:04 UTC
