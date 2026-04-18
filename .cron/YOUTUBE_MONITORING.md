# YouTube Comment Monitor - Complete Documentation

## Overview

Automated system that monitors the Concessa Obvius YouTube channel for new comments every 30 minutes, categorizes them, and takes action:

- **Category 1 (Questions)** → Auto-reply with template
- **Category 2 (Praise)** → Auto-reply with thank you
- **Category 3 (Spam)** → Log and ignore
- **Category 4 (Sales)** → Flag for manual review

## System Components

### 1. Main Monitor Script
**File:** `.cron/youtube-comment-monitor.py`

**What it does:**
- Fetches new comments from channel since last check
- Categorizes each comment using keyword matching
- Auto-replies to questions and praise
- Flags sales inquiries for review
- Logs all activity to `.cache/youtube-comments.jsonl`
- Tracks state to avoid reprocessing

**Runs:** Every 30 minutes via cron

### 2. Categorization Logic

#### Category 1: Questions
Detected by: "how", "what", "when", "where", "why", "can i", "how do i", "tool", "cost", "price", "timeline", "start", "begin", "?"

**Examples:**
- "How do I get started?"
- "What tools do you recommend?"
- "How much does this cost?"
- "Can I use this for X?"

**Action:** Auto-reply with questions template

#### Category 2: Praise
Detected by: "amazing", "inspiring", "great", "love", "awesome", "fantastic", "incredible", "brilliant", "thank you", "appreciate", "well done", "impressed"

**Examples:**
- "This is amazing!"
- "Love your content, very inspiring"
- "You're doing fantastic work"

**Action:** Auto-reply with thank you template

#### Category 3: Spam
Detected by: "crypto", "bitcoin", "ethereum", "mlm", "business opportunity", "work from home", "make money fast", "click here", "free money"

**Examples:**
- "Crypto is the future, get rich now!"
- "Join my MLM"
- "Free money - click here"

**Action:** Log and ignore

#### Category 4: Sales
Detected by: "partnership", "collaboration", "brand deal", "sponsorship", "work together", "let's collaborate", "business inquiry", "investment"

**Examples:**
- "Interested in partnership"
- "Let's collaborate on a project"
- "Brand sponsorship opportunity"

**Action:** Flag for manual review (logged with status="flagged")

## Data Storage

### Comment Log: `.cache/youtube-comments.jsonl`
Each line is a JSON entry:

```json
{
  "comment_id": "UgzU7j_K8Hj9vK3U3n9",
  "thread_id": "UgzU7j_K8Hj9vK3U3n9.16819284...",
  "timestamp": "2026-04-17T23:30:45.123456+00:00",
  "commenter": "John Doe",
  "text": "How do I get started with this?",
  "category": "questions",
  "response_status": "sent"
}
```

**response_status values:**
- `sent` - Auto-reply was successfully posted
- `pending` - Ready to reply but not yet sent (rare)
- `flagged` - Requires manual review (sales inquiries)

### State File: `.cache/youtube-monitor-state.json`
Tracks last check timestamp to avoid reprocessing:

```json
{
  "last_check": "2026-04-17T23:30:00.000000"
}
```

### Log File: `.cache/youtube-monitor.log`
Script output and errors logged here by cron runner.

## Reporting

### View Latest Report
```bash
python .cron/youtube-report.py
```

Output includes:
- Total comments processed
- Breakdown by category
- Response status summary
- Flagged items for review
- Recent activity timeline
- Activity by date (last 7 days)

### View Comments from Last N Days
```bash
python .cron/youtube-report.py 7  # Last 7 days
```

### Query Log Directly
```bash
# View all flagged comments
cat .cache/youtube-comments.jsonl | jq 'select(.response_status == "flagged")'

# View comments by category
cat .cache/youtube-comments.jsonl | jq 'select(.category == "questions")'

# Count by category
cat .cache/youtube-comments.jsonl | jq -s 'group_by(.category) | map({category: .[0].category, count: length})'

# Find comments from specific user
cat .cache/youtube-comments.jsonl | jq 'select(.commenter | contains("John"))'
```

## Setup Steps

### 1. Install Dependencies
```bash
cd /Users/abundance/.openclaw/workspace
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Configure YouTube API
See `.cron/YOUTUBE_SETUP.md` for detailed instructions.

### 3. Test Manually
```bash
python .cron/youtube-comment-monitor.py
```

Expected output:
```
[2026-04-17T23:30:00] YouTube Comment Monitor starting...
Monitoring channel: UCxxxxxxxxxxxx
  [questions] Jane Doe: How do I start...
  [praise] Bob Smith: Amazing content...

📊 Report:
  Processed: 2
  Auto-responses sent: 2
  Flagged for review: 0
  Log: .cache/youtube-comments.jsonl
```

### 4. Schedule Cron Job

**Option A: System Cron**
```bash
crontab -e
# Add:
*/30 * * * * cd /Users/abundance/.openclaw/workspace && python .cron/youtube-comment-monitor.py >> .cache/youtube-monitor.log 2>&1
```

**Option B: OpenClaw Runner**
(If OpenClaw has native cron support, use the YAML config)

### 5. Verify Running
```bash
# Check last execution
tail -20 .cache/youtube-monitor.log

# View latest stats
python .cron/youtube-report.py

# Monitor live
watch -n 60 'python .cron/youtube-report.py'  # Updates every 60 seconds
```

## Customization

### Change Channel
Edit `.cron/youtube-comment-monitor.py`:
```python
CHANNEL_HANDLE = "YourChannelHandle"  # Change this
```

### Modify Response Templates
Edit `.cron/youtube-comment-monitor.py`:
```python
RESPONSE_TEMPLATES = {
    "questions": "Your custom response for questions...",
    "praise": "Your custom thank you message..."
}
```

### Add/Remove Categorization Keywords
Edit the `categorize_comment()` function:
```python
def categorize_comment(text: str) -> CommentCategory:
    text_lower = text.lower()
    
    spam_keywords = ["crypto", "bitcoin", ...]  # Add/remove
    sales_keywords = ["partnership", ...]        # Add/remove
    # etc.
```

### Change Run Frequency
Update cron schedule:
- `*/30 * * * *` = every 30 minutes
- `0 * * * *` = every hour
- `0 */4 * * *` = every 4 hours

## Troubleshooting

### No comments detected
- Check if `CHANNEL_HANDLE` is correct
- Verify YouTube API credentials are valid
- Ensure channel has comments enabled

### Auto-replies not posting
- Verify YouTube account is channel owner
- Check API quota (YouTube Data API has limits)
- Review `.cache/youtube-monitor.log` for errors

### Duplicate replies
- Script tracks processed comment IDs to prevent duplicates
- If you see duplicates, check if comment_id is unique

### Token expired
- Delete `.cache/youtube_token.json`
- Run script manually to re-authorize
- Cron job will automatically use refreshed token

## Rate Limits & Quotas

YouTube Data API limits:
- **Default quota:** 10,000 units per day
- **Cost per run:** ~50-100 units (fetch comments + optional replies)
- **Max replies per run:** 2-3 (to stay within quotas)

For high-comment channels, consider:
- Increasing run interval (less frequent checking)
- Disabling auto-replies (manual review only)
- Using API quota monitoring dashboard

## Security Notes

- **Credentials:** Stored in `.cache/youtube_token.json` (OAuth token)
- **Access:** OAuth scopes limited to comment reading/replying only
- **Logging:** Comments stored in plaintext JSONL (no encryption)
- **Channel:** Requires channel owner account for auto-replies

## Future Enhancements

Potential improvements:
- [ ] AI-based categorization (instead of keyword matching)
- [ ] Sentiment analysis for praise detection
- [ ] Custom category rules per comment type
- [ ] Bulk reply templates with variable substitution
- [ ] Dashboard UI for browsing flagged comments
- [ ] Discord notifications on flagged items
- [ ] Spam auto-deletion after flagging
- [ ] Rate-limit adaptive scheduling

---

**Last Updated:** 2026-04-17
**Version:** 1.0
