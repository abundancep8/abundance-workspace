# YouTube Comment Monitor Setup Guide

## Overview
Monitors the Concessa Obvius YouTube channel for new comments every 30 minutes.
- Categorizes comments (Questions, Praise, Spam, Sales)
- Auto-responds to Questions & Praise
- Flags Sales inquiries for manual review
- Logs all activity to `.cache/youtube-comments.jsonl`

## Prerequisites

### 1. YouTube Data API v3 Credentials

#### Step 1: Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project"
3. Name it "YouTube Comment Monitor"
4. Wait for it to initialize

#### Step 2: Enable YouTube Data API v3
1. In the left sidebar, go to **APIs & Services** → **Library**
2. Search for "YouTube Data API v3"
3. Click it and press **Enable**

#### Step 3: Create an API Key
1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **API Key**
3. Copy the key (you'll see a popup)
4. Save it somewhere safe — you'll need this next

#### Step 4: Set Environment Variable
```bash
# Add to your shell profile (~/.zshrc or ~/.bash_profile)
export YOUTUBE_API_KEY="YOUR_API_KEY_HERE"

# Then reload:
source ~/.zshrc
```

### 2. Get the Concessa Obvius Channel ID

Option A: Look it up manually
1. Go to the Concessa Obvius YouTube channel
2. Click "About"
3. Copy the channel ID from the URL (or from the right sidebar)

Option B: Script will auto-lookup (slower, uses API quota)
- If `YOUTUBE_CHANNEL_ID` is not set, the script will search for the channel by name

Then set:
```bash
export YOUTUBE_CHANNEL_ID="UCxxxxxxxxxxxx"  # Replace with actual ID
```

## Customization

### Edit Response Templates

The script uses template responses for auto-replies. Edit these in `.cache/youtube-monitor.py`:

```python
TEMPLATES = {
    "question": {
        "snippet.replyText": """Thanks for your question! Here are resources:
• FAQ: [your-link]
• Guides: [your-link]
• Reply if you need more help!"""
    },
    "praise": {
        "snippet.replyText": """Thank you! 🙏 Your support means everything. More content coming soon!"""
    }
}
```

### Adjust Category Keywords

Edit the `CATEGORIES` dict to fine-tune detection:

```python
CATEGORIES = {
    "question": ["how do i", "how to", "help", ...],
    "praise": ["amazing", "love", "great", ...],
    "spam": ["crypto", "mlm", ...],
    "sales": ["partnership", "sponsor", ...]
}
```

## Running the Monitor

### Test Run (Manual)
```bash
cd /Users/abundance/.openclaw/workspace
python3 .cache/youtube-monitor.py
```

Expected output:
```
📊 YouTube Comment Monitor Report
Time: 2026-04-15T04:30:00.000000
Total comments processed: 5
Auto-responses sent: 2
Flagged for review (sales): 1

Breakdown by category:
  question: 2
  praise: 2
  spam: 0
  sales: 1
  other: 0
```

### Cron Setup (Every 30 Minutes)

Make script executable:
```bash
chmod +x /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.sh
```

Add to crontab:
```bash
crontab -e
```

Add this line:
```
*/30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.sh >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log 2>&1
```

This runs at :00 and :30 of every hour.

### View Logs

**Last run output:**
```bash
tail -20 .cache/youtube-monitor.log
```

**Comments log (JSONL format):**
```bash
# View all comments
cat .cache/youtube-comments.jsonl | jq .

# View only flagged (sales) comments
cat .cache/youtube-comments.jsonl | jq 'select(.response_status=="flagged_for_review")'

# View auto-responses sent
cat .cache/youtube-comments.jsonl | jq 'select(.response_status=="auto_replied")'
```

## Troubleshooting

### "YOUTUBE_API_KEY not set"
- Make sure the environment variable is exported: `export YOUTUBE_API_KEY="..."`
- Check it's set: `echo $YOUTUBE_API_KEY`

### "Channel not found"
- Verify the channel name is correct (case-sensitive)
- Or set `YOUTUBE_CHANNEL_ID` explicitly to skip lookup

### API Quota Issues
- YouTube Data API has daily quotas (10K units/day for free tier)
- Each comment read = 1 unit, each reply = 50 units
- Monitor your [API quotas here](https://console.cloud.google.com/apis/dashboard)

### Cron Not Running
- Check crontab: `crontab -l`
- View cron logs: `log stream --predicate 'process=="cron"'`
- Make sure environment variables are set in crontab (or in the shell script)

## File Structure

```
.cache/
├── youtube-monitor.py           # Main script
├── youtube-monitor.sh           # Cron wrapper
├── youtube-comments.jsonl       # Comment log (append-only)
├── youtube-monitor-state.json   # Last checked timestamp
├── youtube-monitor.log          # Cron output
└── YOUTUBE_MONITOR_SETUP.md     # This file
```

## What Gets Logged

Each comment in `youtube-comments.jsonl`:

```json
{
  "timestamp": "2026-04-15T04:30:00Z",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "question",
  "response_status": "auto_replied",
  "comment_id": "Ugxxxxxxxxxx",
  "author_channel_url": "http://www.youtube.com/channel/UCxxxx"
}
```

### Response Status Values:
- `"auto_replied"` - Auto-response sent successfully
- `"failed"` - Auto-response failed (will still be attempted next run)
- `"flagged_for_review"` - Sales inquiry flagged (manual action needed)
- `"none"` - No response (spam, other)

## Manual Review

For flagged sales comments:
```bash
cat .cache/youtube-comments.jsonl | jq 'select(.response_status=="flagged_for_review")' | jq -r '.commenter, .text'
```

Then manually reply to the comment in YouTube or update the script if it's a legitimate partnership inquiry.

---

Questions? Check the script comments or reach out!
