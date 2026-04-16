# YouTube Monitor - Operations Guide

## Quick Start (5 minutes)

### 1. Get Your Credentials
- YouTube API Key: https://console.cloud.google.com/apis/credentials
- Channel ID: Visit Concessa Obvius channel → view page source → search `channelId`

### 2. Install Dependencies
```bash
cd /Users/abundance/.openclaw/workspace
pip install -r .cache/requirements.txt
```

### 3. Set Environment Variables
```bash
export YOUTUBE_API_KEY="your-key-here"
export YOUTUBE_CHANNEL_ID="UCxxxxx"
```

### 4. Test Run
```bash
python3 .cache/youtube-monitor.py
```

### 5. Install Cron
```bash
bash .cache/install-cron.sh
```

## Daily Operations

### Monitor Status
```bash
bash .cache/youtube-monitor-utils.sh status
```

Shows:
- Cumulative processing statistics
- Last run details
- Any errors from cron execution

### Review Flagged Items (Sales/Partnerships)
```bash
bash .cache/youtube-monitor-utils.sh flagged
```

This shows all comments that need manual review. Action items:
- Email the person about partnership opportunities
- Decline politely or schedule call
- Mark as handled (manual removal from log)

### Check Recent Comments
```bash
bash .cache/youtube-monitor-utils.sh recent 20
```

See latest comments and their categorization. Useful for:
- Quality checking the categorization algorithm
- Spotting false positives (spam marked as questions)
- Finding interesting discussions

### Search for Specific Topics
```bash
bash .cache/youtube-monitor-utils.sh search "timeline"
bash .cache/youtube-monitor-utils.sh search "tools"
bash .cache/youtube-monitor-utils.sh search "how to"
```

Find common questions or topics to address in future content.

### View by Category
```bash
bash .cache/youtube-monitor-utils.sh category questions
bash .cache/youtube-monitor-utils.sh category praise
bash .cache/youtube-monitor-utils.sh category spam
```

### Get Detailed Stats
```bash
bash .cache/youtube-monitor-utils.sh stats
```

Shows:
- Comments by category (breakdown)
- Response status distribution
- Top commenters
- Engagement metrics (likes)

## Weekly Routine

### 1. Review This Week's Flagged Items
```bash
bash .cache/youtube-monitor-utils.sh flagged | head -20
```

### 2. Check Question Trends
```bash
bash .cache/youtube-monitor-utils.sh category questions | tail -15
```

Use these to:
- Identify FAQ topics for content
- Spot knowledge gaps
- Plan tutorial videos

### 3. Monitor Spam/Bots
```bash
bash .cache/youtube-monitor-utils.sh spam
```

If spam rate exceeds 20%, consider:
- Reporting to YouTube
- Enabling comment moderation
- Blocking certain keywords

### 4. Review Stats
```bash
bash .cache/youtube-monitor-utils.sh stats
```

Track trends:
- Is engagement growing?
- Are questions increasing?
- Spam increasing (signal of reach)?

## Real-World Examples

### Scenario 1: High-Value Lead Arrives
**Comment:** "Love your work! We'd love to discuss a partnership for our B2B platform."

**System Action:**
- Categorized as: `sales`
- Status: `flagged_for_review`
- Appears in: `flagged` command output

**Your Action:**
1. Check sender's channel/profile
2. Evaluate fit for partnership
3. Respond via YouTube comment or DM
4. Log outcome in separate notes

### Scenario 2: FAQ Question Arrives
**Comment:** "How do I get started with your platform? What's the cost?"

**System Action:**
- Categorized as: `questions`
- Status: `auto_response_queued`
- Auto-response not yet sent (requires OAuth setup)

**Your Action:**
1. Monitor tracks this was asked
2. Run `search "cost"` to find patterns
3. Create FAQ video if asked 5+ times
4. Update documentation

### Scenario 3: Spam Comment
**Comment:** "GET RICH QUICK with CRYPTO NFT MLM! DM me now!"

**System Action:**
- Categorized as: `spam`
- Status: `none` (logged only)
- Ignored in auto-response queue

**Your Action:**
- Nothing required (auto-ignored)
- Report to YouTube if pattern continues

### Scenario 4: Genuine Praise
**Comment:** "This completely changed how I approach my business. Amazing content!"

**System Action:**
- Categorized as: `praise`
- Status: `auto_response_queued`
- Template response ready

**Your Action:**
- System sends thank you (when OAuth enabled)
- Builds relationship with engaged audience

## Advanced Usage

### Export Data for Analysis
```bash
# Export as CSV for spreadsheet analysis
bash .cache/youtube-monitor-utils.sh export csv

# Open in Excel/Sheets
open youtube-comments-export.csv
```

### Find Comments from Specific Person
```bash
bash .cache/youtube-monitor-utils.sh by-user "John Smith"
```

### Create Custom Filters
```bash
# Find all unanswered questions about "pricing"
grep '"category":"questions"' .cache/youtube-comments.jsonl | \
  grep -i "pric" | \
  grep '"response_status":"auto_response_queued"'
```

### Monitor Comment Velocity
```bash
# See comments per hour
jq '.timestamp' .cache/youtube-comments.jsonl | \
  cut -d'T' -f2 | cut -d':' -f1 | sort | uniq -c
```

## Troubleshooting

### Cron Not Running
**Symptom:** No new log entries, but manual runs work

**Fix:**
```bash
# Check cron is enabled
launchctl list | grep cron

# View cron logs
log stream --predicate 'process == "cron"' --level debug

# Verify crontab entry
crontab -l | grep youtube
```

### API Quota Exceeded
**Symptom:** Error messages in `.cache/youtube-monitor.log` about quota

**Fix:**
- Check quota in Google Cloud Console
- YouTube API has 10,000 units/day free
- Current script uses ~50 units per run (efficient)
- At 30-min intervals: ~48 runs/day = ~2,400 units
- Safe to run every 30 mins

### Wrong Channel Being Monitored
**Symptom:** Comments from different channel

**Fix:**
```bash
# Verify your Channel ID
echo $YOUTUBE_CHANNEL_ID

# Get correct ID from channel about page
open "https://www.youtube.com/c/CHANNEL_NAME/about"
# View page source → search "channelId"
```

### Comments Not Categorized Correctly
**Symptom:** Questions marked as praise, etc.

**Current behavior:** Pattern-based categorization (keyword matching)

**To improve:**
- Add more keywords to `CATEGORIES` dict in youtube-monitor.py
- Or implement ML-based categorization (see "Advanced Enhancements" below)

## Advanced Enhancements

### 1. Enable Actual Auto-Responses
Currently responses are queued but not sent. To enable:

1. Switch to OAuth authentication:
```python
from google.oauth2 import service_account
# Load service account key
credentials = service_account.Credentials.from_service_account_file(
    'youtube-service-account.json'
)
```

2. Implement reply sending:
```python
youtube.comments().insert(
    part="snippet",
    body={
        "snippet": {
            "parentId": comment_id,
            "textOriginal": response_text
        }
    }
).execute()
```

3. Get OAuth credentials from Google Cloud Console (Service Account)

### 2. Machine Learning Categorization
Replace keyword matching with ML:

```python
from transformers import pipeline

classifier = pipeline("zero-shot-classification")
labels = ["question", "praise", "spam", "sales", "other"]
result = classifier(text, labels)
category = result['labels'][0]
```

This handles nuance better (sarcasm, context, etc.)

### 3. Sentiment Analysis
```python
from transformers import pipeline

sentiment = pipeline("sentiment-analysis")
result = sentiment(text)
print(f"Sentiment: {result[0]['label']} ({result[0]['score']:.2%})")
```

### 4. Duplicate Detection
```python
from difflib import SequenceMatcher

def is_duplicate(text1, text2, threshold=0.85):
    ratio = SequenceMatcher(None, text1, text2).ratio()
    return ratio > threshold
```

### 5. Integration with Discord
Notify leadership in Discord when flagged items arrive:

```python
from discord import Webhook, AsyncWebhook
import aiohttp

async def notify_discord(comment, category):
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(DISCORD_WEBHOOK_URL, session=session)
        await webhook.send(f"New {category}: {comment['author']}\n{comment['text']}")
```

### 6. Email Notifications
```python
import smtplib
from email.mime.text import MIMEText

def email_flagged_items():
    # Collect flagged comments since last email
    flagged = get_flagged_since_last_email()
    
    if flagged:
        send_email(
            to="you@example.com",
            subject=f"{len(flagged)} flagged YouTube comments",
            body=format_as_email(flagged)
        )
```

## Performance & Costs

### API Usage
- **Current:** ~50 API units per 30-min run
- **Daily:** ~2,400 units at 48 runs/day
- **Free quota:** 10,000 units/day
- **Status:** ✅ Well within free tier

### Storage
- **Per comment:** ~400 bytes in JSONL
- **Monthly:** ~1,200 comments × 400b = ~480 KB
- **Yearly:** ~5.8 MB
- **Status:** ✅ Negligible

### Compute
- **Per run:** <1 second
- **Daily:** <1 minute total
- **Status:** ✅ Negligible

## Maintenance Checklist

**Weekly:**
- [ ] Review flagged sales inquiries
- [ ] Check stats for trends
- [ ] Verify cron is running (check logs)

**Monthly:**
- [ ] Export and archive comments.jsonl
- [ ] Review top commenters for VIP treatment
- [ ] Analyze question trends for content planning
- [ ] Check API quota usage

**Quarterly:**
- [ ] Review and refine categorization keywords
- [ ] Evaluate enhancements (ML, notifications, etc.)
- [ ] Clean up old logs (archive)

## Support & Resources

- **YouTube API Docs:** https://developers.google.com/youtube/v3
- **Google Cloud Console:** https://console.cloud.google.com
- **OpenClaw Docs:** https://docs.openclaw.ai
- **Script Issues:** Check `.cache/youtube-monitor.log`

---

**Last Updated:** 2026-04-16  
**Script Version:** 1.0  
**Status:** Production Ready
