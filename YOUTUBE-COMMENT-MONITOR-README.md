# YouTube Comment Monitor for Concessa Obvius

A production-ready automated comment monitoring system for YouTube that categorizes, responds, and logs all channel comments.

## 🎯 What It Does

**Monitors new comments** on Concessa Obvius channel videos and automatically:

1. **Categorizes** each comment into 4 types:
   - **Category 1:** Questions (how, what, start, tools, cost, timeline)
   - **Category 2:** Praise (amazing, inspiring, love, thank you, etc.)
   - **Category 3:** Spam (crypto, MLM, suspicious links)
   - **Category 4:** Sales (partnership, collaboration, sponsorship)

2. **Auto-responds** to categories 1-2:
   - Questions → "Thanks for the question! Check our FAQ or reach out to support@concessa.com for detailed help."
   - Praise → "Thank you so much! We really appreciate your support 🙏"

3. **Flags category 4** (sales) for manual review

4. **Filters category 3** (spam) silently

5. **Logs everything** to JSONL format with metadata

6. **Tracks processed IDs** to avoid duplicate responses

## 📊 System Architecture

```
YouTube API
    ↓
youtube-comment-monitor.py
    ├─ Fetch videos from channel
    ├─ Fetch comments from each video
    ├─ Categorize using keyword regex
    ├─ Auto-post replies (if OAuth enabled)
    ├─ Log to JSONL
    └─ Save state
    
Output:
  ~/.cache/youtube-comments.jsonl ── All comments + actions
  ~/.cache/youtube-comments-processed.json ── Processed IDs (dedup)
  ~/.cache/.youtube-monitor-state.json ── Last run stats
```

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.8+
python3 --version

# Install dependencies
cd ~/.openclaw/workspace
python3 -m venv .venv
source .venv/bin/activate
pip install google-api-python-client
```

### 2. Setup YouTube API

**Option A: Using API Key (Read-Only, Recommended)**

Get an API key from [Google Cloud Console](https://console.cloud.google.com):

```bash
# Set environment variable
export YOUTUBE_API_KEY="your-api-key-here"

# Or save to file (more convenient)
echo "your-api-key-here" > ~/.youtube-api-key
```

**Option B: Using OAuth2 (Read + Write)**

For auto-responding with your account:

1. Download OAuth2 credentials from Google Cloud Console
2. Save to: `~/.openclaw/youtube-credentials.json`
3. First run will open browser for authentication

### 3. Run the Monitor

```bash
cd ~/.openclaw/workspace
source .venv/bin/activate

# Test version (mock data, no API key needed)
python3 youtube-comment-monitor-test.py

# Production version (requires YouTube API)
python3 youtube-comment-monitor.py
```

### 4. Verify Output

```bash
# View recent comments
tail -5 ~/.cache/youtube-comments.jsonl | jq .

# View state
cat ~/.cache/.youtube-monitor-state.json

# View processed IDs
cat ~/.cache/youtube-comments-processed.json
```

## 📋 Output Files

### `youtube-comments.jsonl`
JSON Lines format (one JSON object per line). Each entry contains:

```json
{
  "timestamp": "2026-04-20T12:02:37.855934",
  "comment_id": "test_q1",
  "video_id": "demoVid1",
  "author": "Sarah Chen",
  "text": "How do I get started building automation...",
  "category": 1,
  "category_label": "questions",
  "response_status": "auto_responded",
  "response_text": "Thanks for the question! Check our FAQ..."
}
```

### `youtube-comments-processed.json`
Tracks processed comment IDs for deduplication:

```json
{
  "processed": ["test_q1", "test_q2", "test_p1"],
  "updated": "2026-04-20T12:02:37.855882"
}
```

### `.youtube-monitor-state.json`
Summary statistics from last run:

```json
{
  "last_run": "2026-04-20T12:02:37.855934",
  "channel": "Concessa Obvius",
  "channel_id": "UCa_mZVVqV5Aq48a0MnIjS-w",
  "status": "operational",
  "videos_checked": 3,
  "total_comments": 8,
  "auto_responded": 4,
  "flagged_for_review": 2,
  "spam_filtered": 2,
  "by_category": {
    "1_questions": 2,
    "2_praise": 2,
    "3_spam": 2,
    "4_sales": 2
  }
}
```

## 🔧 Configuration

### Customize Template Responses

Edit `youtube-comment-monitor.py`, line ~40:

```python
TEMPLATES = {
    "questions": "Your custom question response...",
    "praise": "Your custom praise response..."
}
```

### Adjust Categorization Keywords

Edit `KEYWORDS` dict (lines ~47-89):

```python
KEYWORDS = {
    "questions": {
        "how": r'\bhow\b',
        "what": r'\bwhat\b',
        "cost": r'\bcost|price\b',
        # Add more keywords...
    },
    # ...
}
```

### Change Channel

Edit channel ID (line ~36):

```python
CHANNEL_ID = "UCa_mZVVqV5Aq48a0MnIjS-w"  # Replace with target channel
```

## ⏰ Automation (Cron)

Run every 30 minutes automatically:

```bash
# Edit crontab
crontab -e

# Add this line
*/30 * * * * cd /Users/abundance/.openclaw/workspace && source .venv/bin/activate && python3 youtube-comment-monitor.py >> .cache/youtube-monitor.log 2>&1
```

Check it's working:

```bash
# View cron jobs
crontab -l

# View logs
tail -20 ~/.cache/youtube-monitor.log
```

## 📈 Monitoring & Reporting

### Check Recent Activity

```bash
# Last 10 comments
tail -10 ~/.cache/youtube-comments.jsonl

# Summary of last 24 hours
grep "2026-04-20" ~/.cache/youtube-comments.jsonl | jq '.response_status' | sort | uniq -c

# All flagged-for-review comments
grep "flagged_review" ~/.cache/youtube-comments.jsonl
```

### Generate Report

```python
import json
from pathlib import Path

log_file = Path.home() / ".openclaw/workspace/.cache/youtube-comments.jsonl"

with open(log_file) as f:
    comments = [json.loads(line) for line in f]

report = {
    'total': len(comments),
    'by_category': {},
    'by_status': {}
}

for comment in comments:
    cat = comment['category_label']
    status = comment['response_status']
    report['by_category'][cat] = report['by_category'].get(cat, 0) + 1
    report['by_status'][status] = report['by_status'].get(status, 0) + 1

print(json.dumps(report, indent=2))
```

## 🔐 Security & Rate Limits

### YouTube API Quotas

- Default quota: 10,000 units/day
- Comments fetch: ~3 units per request
- Reply posting: ~50 units per request
- At 30-min intervals: Safe within quota

Monitor usage: [Google Cloud Console Dashboard](https://console.cloud.google.com/apis/dashboard)

### Best Practices

✅ Use API key for read-only operations  
✅ Use OAuth2 for auto-responses (with proper scopes)  
✅ Track processed IDs to prevent duplicates  
✅ Log all activity for audit trail  
✅ Review flagged sales comments manually  
⚠️ Don't expose API key in version control  

## 🐛 Troubleshooting

### "YOUTUBE_API_KEY not set"
```bash
export YOUTUBE_API_KEY="your-key"
# or
echo "your-key" > ~/.youtube-api-key
```

### "API error: 403 Forbidden"
- Verify API key is valid
- Check YouTube Data API v3 is enabled
- Check quota not exceeded in Cloud Console

### "No comments found"
- Verify channel ID is correct
- Check if channel has recent comments
- Verify API key has read access

### "Cron job not running"
```bash
# Test manually
cd ~/.openclaw/workspace && source .venv/bin/activate && python3 youtube-comment-monitor.py

# Check system logs
log stream --predicate 'eventMessage contains[cd] "youtube-comment"'

# Verify cron is scheduled
crontab -l
```

## 📊 Example Usage

### Test Run with Mock Data

```bash
python3 youtube-comment-monitor-test.py
```

Output:
```
============================================================
📺 YouTube Comment Monitor - TEST VERSION
   (Using mock data for demonstration)
============================================================

📝 Previously processed: 0 comment IDs
📹 Mock videos: 3
💬 New comments found: 8

🏷️  Categorizing and processing comments...
  ✅ Q&A: Sarah Chen... → auto-reply sent
  ✅ Q&A: Marcus Johnson... → auto-reply sent
  👏 Praise: Emma Watson... → thank you sent
  👏 Praise: David Park... → thank you sent
  🚫 Spam: CryptoGuy88... → filtered
  🚫 Spam: MLMQueen... → filtered
  🚩 Sales: BusinessGuy... → flagged for manual review
  🚩 Sales: SalesRep... → flagged for manual review

============================================================
📊 SUMMARY REPORT
============================================================
Channel:                Concessa Obvius
Videos checked:         3
Total new comments:     8

Comment Breakdown:
  ❓ Questions (Cat 1):  2
  👏 Praise (Cat 2):     2
  🚫 Spam (Cat 3):       2
  💼 Sales (Cat 4):      2

Actions Taken:
  ✅ Auto-responses sent: 4
  🚩 Flagged for review:  2
  🚫 Spam filtered:       2
```

### Deduplication Test

Run again to verify no duplicate processing:

```bash
python3 youtube-comment-monitor-test.py

# Output:
📝 Previously processed: 8 comment IDs
💬 New comments found: 0
✨ All comments already processed
```

## 🎯 Real-World Workflow

1. **Setup** (once)
   - Get YouTube API key
   - Configure templates
   - Test with mock data

2. **Deploy** (once)
   - Set cron job for every 30 minutes
   - Monitor logs for first week

3. **Maintain**
   - Review flagged sales comments
   - Adjust keywords based on false positives
   - Monitor quota usage monthly

4. **Report**
   - Weekly summary of comment volume
   - Monthly trends
   - Auto-response effectiveness

## 📚 Advanced Features

### Custom Categorization Logic

Modify `categorize_comment()` function to use ML models:

```python
def categorize_comment(text: str) -> Tuple[int, str, float]:
    # Replace regex logic with ML classifier
    prediction = model.predict(text)
    return (prediction.category, prediction.label, prediction.confidence)
```

### Integration with Support Tickets

Route flagged comments to your support system:

```python
if response_status == "flagged_review":
    create_support_ticket(
        title=f"Sales inquiry from {comment['author']}",
        description=comment['text'],
        priority='high'
    )
```

### Sentiment Analysis

Add sentiment detection:

```python
from textblob import TextBlob

sentiment = TextBlob(comment['text']).sentiment.polarity
if sentiment < 0:
    # Potentially upset customer
    flag_for_manual_review(comment)
```

## 📞 Support

For issues:
1. Check logs: `tail -50 ~/.cache/youtube-monitor.log`
2. Test manually: `python3 youtube-comment-monitor.py`
3. Review API dashboard: [Google Cloud Console](https://console.cloud.google.com)

## 📝 License & Notes

- Uses YouTube Data API v3
- Requires YouTube API credentials
- Respects YouTube's terms of service
- All data logged locally in your workspace
- Deduplication ensures no spam responses

---

**Last Updated:** 2026-04-20  
**Channel:** Concessa Obvius  
**Channel ID:** UCa_mZVVqV5Aq48a0MnIjS-w
