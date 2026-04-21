# 📺 YouTube Comment Monitor

Automated system to monitor the **Concessa Obvius** YouTube channel, categorize comments, and send intelligent auto-responses.

**Status:** ✅ Ready to deploy (requires Google API setup)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google API credentials (5 minutes to set up)

### 1️⃣ Get YouTube API Access

```bash
# Follow the setup guide
cat docs/youtube-monitor-setup.md

# OR go directly to Google Cloud Console:
# https://console.cloud.google.com/apis/credentials
```

Download your OAuth 2.0 JSON file and save it to:
```
.cache/youtube-credentials.json
```

### 2️⃣ Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3️⃣ Run First Time (Authenticate)

```bash
python3 scripts/youtube-monitor.py
```

This will:
- Open your browser to authorize access
- Save the token for future runs
- Fetch and process existing comments
- Generate your first report

### 4️⃣ Set Up Cron Job (Every 30 Minutes)

The cron system will automatically run this every 30 minutes. No additional setup needed!

To run manually at any time:
```bash
./scripts/youtube-monitor.sh
```

## 📊 How It Works

### Comment Categorization

| Category | Triggers | Auto-Response |
|----------|----------|---------------|
| **Question** | "how", "what", "cost", "timeline", "start" | ✅ Yes |
| **Praise** | "amazing", "inspiring", "love", "great" | ✅ Yes |
| **Spam** | "crypto", "mlm", "bitcoin", "scheme" | ❌ No |
| **Sales** | "partnership", "sponsor", "collaboration" | 📌 Flag for review |

### Data Flow

```
YouTube Channel
       ↓
Fetch Recent Videos & Comments
       ↓
Categorize Each Comment
       ↓
Auto-respond (Questions/Praise)
       ↓
Flag Sales for Review
       ↓
Log to .cache/youtube-comments.jsonl
       ↓
Generate Report & Stats
```

## 📋 Files & Structure

```
workspace/
├── scripts/
│   ├── youtube-monitor.py      # Main monitoring script
│   ├── youtube-monitor.sh      # Cron wrapper
│   └── youtube-stats.py        # Stats dashboard
├── .cache/
│   ├── youtube-comments.jsonl  # All processed comments (log file)
│   ├── youtube-credentials.json # OAuth credentials (you provide)
│   ├── youtube-token.json      # Auth token (auto-generated)
│   └── youtube-state.json      # Last check state (auto-generated)
├── .youtube-monitor.config.json # Configuration file
├── docs/
│   └── youtube-monitor-setup.md # Detailed setup guide
└── YOUTUBE_MONITOR.md           # This file
```

## 🔧 Configuration

Edit `.youtube-monitor.config.json` to customize:

### Channel to Monitor
```json
"channel_name": "Concessa Obvius"
```

### Auto-Response Templates
```json
"auto_responses": {
  "question": "Custom response for questions...",
  "praise": "Custom response for praise..."
}
```

### Categorization Keywords
```json
"categorization": {
  "question_keywords": ["how", "what", "cost", ...],
  "praise_keywords": ["amazing", "inspiring", ...],
  "spam_keywords": ["bitcoin", "crypto", ...],
  "sales_keywords": ["partnership", "sponsor", ...]
}
```

### Behavior
```json
"check_interval_minutes": 30,
"max_videos_per_check": 5,
"max_comments_per_video": 20
```

## 📈 View Statistics

### Dashboard (Current Stats)
```bash
python3 scripts/youtube-stats.py
```

Sample output:
```
========================================================================
YouTube Comment Monitor - Statistics Dashboard
========================================================================

📊 Overall Stats
  Total comments processed: 42
  Auto-responses sent: 28
  Flagged for review: 3
  Latest activity: 2026-04-21 (5 comments)

📂 Breakdown by Category
  Question         12 (28.6%)
  Praise           16 (38.1%)
  Spam              8 (19.0%)
  Sales             3 (7.1%)
  Other             3 (7.1%)

📅 Last 7 Days Activity
  2026-04-21:   5 comments (3 auto-responses)
  2026-04-20:   8 comments (6 auto-responses)
  2026-04-19:  12 comments (9 auto-responses)
```

### View Raw Logs
```bash
# Pretty-print all comments
tail -100 .cache/youtube-comments.jsonl | jq

# Filter by category
cat .cache/youtube-comments.jsonl | jq 'select(.category=="sales")'

# Count by status
cat .cache/youtube-comments.jsonl | jq -r '.response_status' | sort | uniq -c
```

## 🛡️ Safety & Limits

### YouTube API Quotas
- Default quota: **10,000 units/day**
- Per-comment cost: ~2-3 units
- At current 30-min interval: ~48 checks/day × 2 units = **96 units/day** ✅ Well under limit

### Deduplication
- Script tracks processed comment IDs
- Won't re-respond to same comment
- State saved in `.cache/youtube-state.json`

### Rate Limiting
- Respects YouTube API rate limits
- Automatic backoff on 429 responses
- Retry logic in place

## 🔍 Monitoring & Alerts

### Check Logs for Errors
```bash
# Watch live logs (if running manually)
tail -f .cache/youtube-comments.jsonl

# Check for failed responses
cat .cache/youtube-comments.jsonl | jq 'select(.response_status=="failed")'

# See all sales inquiries for manual review
cat .cache/youtube-comments.jsonl | jq 'select(.response_status=="flagged")'
```

### Last Check Time
```bash
# When was the monitor last run?
jq '.last_check' .cache/youtube-state.json
```

## 🐛 Troubleshooting

### "Credentials not found"
```bash
# Make sure you have the JSON file from Google Cloud
ls -la .cache/youtube-credentials.json

# If missing, download from:
# https://console.cloud.google.com/apis/credentials
```

### "Channel not found"
- Check spelling of channel name in config or script
- Use exact channel name: "Concessa Obvius"
- Try with channel handle if available: "@ConcessaObvious"

### "Token expired"
```bash
# Delete the token and re-authenticate
rm .cache/youtube-token.json

# Next run will prompt for auth again
python3 scripts/youtube-monitor.py
```

### "Rate limit exceeded"
- YouTube quota exceeded for the day
- Check usage: https://console.cloud.google.com/apis/dashboard
- Wait until next day (quota resets at midnight UTC)
- Or reduce check frequency

## 📝 Log Entry Format

```json
{
  "timestamp": "2026-04-21T06:30:00.123456",
  "video_id": "abcd1234",
  "comment_id": "xyz789",
  "author": "Jane Doe",
  "text": "How do I get started with this?",
  "published": "2026-04-21T05:00:00Z",
  "category": "question",
  "response_status": "auto_sent",
  "response_id": "reply123"
}
```

### Status Values
- `none` - No response sent (spam/other)
- `auto_sent` - Automated response posted successfully
- `failed` - Response attempt failed (check logs)
- `flagged` - Marked for manual review (sales inquiries)

## 🔄 Workflow

### For Questions
1. Monitor detects comment with "how", "what", "cost", etc.
2. Categorizes as "question"
3. Posts auto-response template
4. Logs with `response_status: "auto_sent"`

### For Praise
1. Monitor detects comment with "amazing", "love", etc.
2. Categorizes as "praise"
3. Posts auto-response template
4. Logs with `response_status: "auto_sent"`

### For Sales Inquiries
1. Monitor detects comment with "partnership", "sponsor", etc.
2. Categorizes as "sales"
3. Does NOT post response
4. Logs with `response_status: "flagged"`
5. You review and respond manually

### For Spam
1. Monitor detects comment with "bitcoin", "crypto", "mlm", etc.
2. Categorizes as "spam"
3. Does NOT post response
4. Logs with `response_status: "none"`

## ✨ Advanced Usage

### Custom Categorization
Edit the `categorize_comment()` function in `scripts/youtube-monitor.py`:

```python
def categorize_comment(text):
    text_lower = text.lower()
    
    # Add your own patterns
    if 'your_keyword' in text_lower:
        return 'custom_category'
    
    # ... rest of function
```

### Batch Processing Historical Comments
```bash
# Script tracks processed IDs, so it won't re-process
# But you can force reset if needed:
rm .cache/youtube-state.json
python3 scripts/youtube-monitor.py
```

### Export Data for Analysis
```bash
# Convert JSONL to CSV
cat .cache/youtube-comments.jsonl | jq -r \
  '[.timestamp, .author, .category, .response_status] | @csv' \
  > comments.csv

# Analyze with pandas, Excel, etc.
python3 -c "
import pandas as pd
df = pd.read_json('.cache/youtube-comments.jsonl', lines=True)
print(df.groupby('category').size())
"
```

## 📞 Support

**Setup help:** See `docs/youtube-monitor-setup.md`

**Questions?** Check the logs:
```bash
# See all errors
cat .cache/youtube-comments.jsonl | jq 'select(.response_status=="failed")'

# See full state
cat .cache/youtube-state.json | jq
```

---

**Monitor Status:** ✅ Active  
**Last Check:** Run `python3 scripts/youtube-stats.py` to see  
**Next Run:** In ~30 minutes (via cron)

Happy monitoring! 🚀
