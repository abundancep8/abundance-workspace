# YouTube Comment Monitor

Automated monitoring, categorization, and response system for the Concessa Obvius YouTube channel.

## 📋 Overview

**What it does:**
- ✅ Monitors the Concessa Obvius channel for new comments (every 30 minutes)
- 🏷️ Categorizes comments automatically:
  - **Questions** (how-to, tools, cost, timeline, etc.)
  - **Praise** (positive feedback, appreciation)
  - **Spam** (crypto, MLM, adult content, etc.)
  - **Sales** (partnerships, sponsorships, collaborations)
  - **Other** (uncategorized)
- 💬 Flags comments needing review or response
- 📝 Logs all activity to `.cache/youtube-comments.jsonl`
- 📊 Generates summary reports

## 🚀 Quick Start

### 1️⃣ Get YouTube API Access

**Option A: API Key (Simpler)**
```bash
# 1. Go to Google Cloud Console
#    https://console.cloud.google.com/

# 2. Create new project (or use existing)

# 3. Enable YouTube Data API v3
#    APIs & Services → Search "YouTube Data API v3" → Enable

# 4. Create API Key
#    Credentials → Create Credentials → API Key

# 5. Export the key
export YOUTUBE_API_KEY="your-api-key-here"
```

**Option B: OAuth 2.0 (Better for reply functionality)**
```bash
# Follow YOUTUBE_SETUP.md for detailed instructions
```

### 2️⃣ Verify Channel ID

Open: `https://www.youtube.com/@ConcessaObvius` (or similar)

The channel ID is in the URL or page source. Update the script if needed:
```python
CONFIG = {
    "channel_id": "UCfJJ3FprqTOmJlAp6nYpLXw",  # ← Update this
    ...
}
```

### 3️⃣ Test the Monitor

```bash
cd /Users/abundance/.openclaw/workspace/.cache
python youtube_comment_monitor.py
```

Expected output:
```
🔍 YouTube Comment Monitor - 2026-04-20T04:00:00
📨 Found 3 new comment(s)
   [Q] John: How do I get started...
   [✨] Sarah: This is amazing...
   [💼 SALES] Partner Co: Let's collaborate...

============================================================
📊 REPORT - 2026-04-20T04:00:00
============================================================
  Total comments processed: 3
  Auto-responses sent: 2
  Flagged for review: 1
  Breakdown: {'questions': 1, 'praise': 1, 'sales': 1}
============================================================
```

### 4️⃣ View the Dashboard

```bash
python .cache/youtube-monitor-dashboard.py
```

Displays:
- Total comments logged
- Breakdown by category
- Comments flagged for review
- Quick export commands

## 📂 Files

| File | Purpose |
|------|---------|
| `youtube_comment_monitor.py` | Main monitoring script |
| `youtube-monitor-dashboard.py` | Summary dashboard |
| `youtube-comments.jsonl` | All logged comments (append-only) |
| `youtube-monitor-state.json` | Internal state (processed IDs) |
| `youtube-monitor-config.json` | Configuration (template) |
| `YOUTUBE_SETUP.md` | Detailed API setup guide |

## 🎯 Category Examples

### Questions
```
"How do I get started?"
"What tools do you use?"
"How much does this cost?"
"What's the timeline?"
```

### Praise
```
"This is amazing! 🔥"
"Thank you for this guide!"
"Incredibly inspiring content!"
```

### Spam
```
"Get rich quick with crypto!"
"Join our MLM network!"
"CLICK HERE: [link]"
```

### Sales
```
"Let's partner on this!"
"Interested in sponsorship?"
"Can we collaborate?"
```

## 🔧 Customization

### Edit Response Templates

Edit `TEMPLATES` in `youtube_comment_monitor.py`:
```python
TEMPLATES = {
    "questions": """Thanks for asking! [YOUR_CUSTOM_ANSWER]
    
For more, see: [LINK]""",
    "praise": """Thanks for the love! 🙏 [YOUR_CUSTOM_MESSAGE]""",
}
```

### Add/Modify Categories

Edit `PATTERNS` dict:
```python
PATTERNS = {
    "your_category": [
        r"keyword1",
        r"keyword2",
        r"regex_pattern",
    ],
}
```

### Change Schedule

Edit the cron schedule (currently `*/30 * * * *` = every 30 min):
```python
# Every 15 minutes: */15 * * * *
# Every hour:      0 * * * *
# Daily at 9 AM:   0 9 * * *
```

## 📊 Viewing Results

### All Comments
```bash
cat .cache/youtube-comments.jsonl | jq
```

### Comments Needing Review
```bash
cat .cache/youtube-comments.jsonl | jq 'select(.response_status == "flagged_for_review")'
```

### Export to CSV
```bash
cat .cache/youtube-comments.jsonl | jq -r '[.processed_at, .commenter, .category, .text] | @csv' > comments.csv
```

### Count by Category (Last 24h)
```bash
cat .cache/youtube-comments.jsonl | \
jq -s 'map(select(.processed_at > now - 86400)) | group_by(.category) | map({category: .[0].category, count: length}) | sort_by(-.count)'
```

## 🤖 Enable Auto-Responses

By default, the script **flags** all responses for manual review. To enable auto-replies:

1. Edit `youtube_comment_monitor.py`
2. Find the section handling "questions" and "praise"
3. Change `response_status = "needs_manual_response"` to actually call the YouTube API:

```python
if category == "questions":
    response = self.generate_response(category, comment)
    if response:
        reply_id = self.reply_to_comment(comment['comment_id'], response)
        response_status = "auto_replied" if reply_id else "failed"
```

3. Implement the `reply_to_comment()` method using YouTube API

**⚠️ Warning:** Enable auto-replies carefully! Test thoroughly with template responses first.

## 🧪 Testing

### Dry Run (no logging)
```python
monitor = YouTubeCommentMonitor()
comments = monitor.fetch_recent_comments()
for comment in comments:
    category = monitor.categorize_comment(comment['text'])
    print(f"{category}: {comment['text'][:50]}")
```

### Debug Categorization
```bash
python -c "
import re
text = 'How much does this cost?'
patterns = {'questions': [r'cost', r'price', r'how']}
for cat, pats in patterns.items():
    if any(re.search(p, text.lower()) for p in pats):
        print(f'Matched: {cat}')
"
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `YOUTUBE_API_KEY not set` | `export YOUTUBE_API_KEY="..."` then retry |
| `Channel not found` | Verify `CONFIG["channel_id"]` in the script |
| `API client not installed` | `pip install google-auth-oauthlib google-api-python-client` |
| No comments fetched | Check channel ID, ensure it has videos with comments |
| Categorization too loose | Tighten regex patterns in `PATTERNS` |
| Too many false positives | Add negative patterns or manual review step |

## 📈 Next Steps

1. ✅ Set up YouTube API key
2. ✅ Test the script manually
3. ✅ Review and customize templates
4. ✅ Check the dashboard
5. 📋 Monitor log file for a few days
6. 🔧 Refine categories/patterns based on real comments
7. 🤖 Enable auto-responses (carefully!)
8. 📊 Generate weekly reports for insights

## 🔔 Integration

### Discord Notifications
(To be implemented) Send flagged comments and summaries to Discord:
```python
async def notify_discord(category, comment):
    # Post to #youtube-comments channel
```

### Email Reports
(To be implemented) Daily summary email:
```python
def send_email_report(stats):
    # Send to your email
```

## 📝 Log Format

Each line in `youtube-comments.jsonl` is valid JSON:
```json
{
  "timestamp": "2026-04-20T04:00:00.123456",
  "processed_at": "2026-04-20T04:00:00.123456",
  "comment_timestamp": "2026-04-19T22:30:00Z",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "questions",
  "response_status": "needs_manual_response",
  "comment_id": "abc123def456"
}
```

## 🤝 Support

Need help? Check:
1. `YOUTUBE_SETUP.md` for API setup
2. Script docstrings and inline comments
3. The troubleshooting section above

---

**Last Updated:** 2026-04-20  
**Status:** Ready to deploy  
**Cron Schedule:** Every 30 minutes ⏰
