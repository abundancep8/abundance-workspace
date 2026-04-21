# YouTube Comment Monitor - Setup Guide

## What It Does

Monitors the Concessa Obvius YouTube channel every 30 minutes for new comments:

- **Categories:** Questions | Praise | Spam | Sales
- **Auto-responds** to Questions and Praise with templates
- **Flags Sales inquiries** for manual review
- **Logs all comments** to `.cache/youtube-comments.jsonl`
- **Reports** statistics on each run

## Prerequisites

### 1. YouTube API Access

You need:
- **YouTube Data API v3** enabled on Google Cloud
- **API Key** (public key for read-only access)
- **Channel ID** for Concessa Obvius

#### Get Your YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable **YouTube Data API v3**:
   - Search "YouTube Data API v3"
   - Click "Enable"
4. Create API Key:
   - Go to **Credentials** → **Create Credentials** → **API Key**
   - Copy the key (looks like `AIza...`)

#### Get Channel ID

Visit the Concessa Obvius channel:
- URL: `https://www.youtube.com/channel/UC...`
- The `UC...` part is your Channel ID

**OR** use your channel's custom URL:
- Settings → Basic Info → Channel URL

### 2. Python Dependencies

```bash
pip install google-api-python-client
```

## Setup Steps

### Step 1: Create Config File

Copy the template and fill in your credentials:

```bash
cp .cache/youtube-monitor-config.json.template .cache/youtube-monitor-config.json
```

Edit `.cache/youtube-monitor-config.json`:

```json
{
  "api_key": "AIza_YOUR_ACTUAL_API_KEY",
  "channel_id": "UCxxx_YOUR_ACTUAL_CHANNEL_ID"
}
```

### Step 2: Test the Script

```bash
cd /Users/abundance/.openclaw/workspace
python3 .cache/youtube-monitor.py
```

Expected output:

```
============================================================
YouTube Comment Monitor Report
============================================================
Run Time: 2026-04-21T03:30:00.123456
Total Comments Processed: 5
Auto-Responses Sent: 2
Flagged for Review: 1

Breakdown by Category:
  Question: 2
  Praise: 1
  Sales: 1
  Spam: 0
  Neutral: 1
============================================================
```

### Step 3: Set Up Cron Job

#### Option A: Using `crontab` (Mac/Linux)

```bash
crontab -e
```

Add this line (runs every 30 minutes):

```
*/30 * * * * cd /Users/abundance/.openclaw/workspace && /usr/bin/python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1
```

Verify it's installed:

```bash
crontab -l | grep youtube-monitor
```

#### Option B: Using OpenClaw Cron

If your OpenClaw has cron support, register it via the UI or config file (see your OpenClaw docs).

## Output Files

### `.cache/youtube-comments.jsonl`

Each line is a JSON object with one comment:

```json
{
  "timestamp": "2026-04-21T03:30:45.123456",
  "comment_id": "Ugw...",
  "video_id": "dQw4w9WgXcQ",
  "author": "John Doe",
  "text": "How do I get started with this?",
  "published": "2026-04-21T03:15:00Z",
  "likes": 2,
  "category": "question",
  "response_status": "auto_responded"
}
```

### `.cache/youtube-monitor-last-check.json`

Tracks last run time to avoid duplicate processing:

```json
{
  "last_check": "2026-04-21T03:30:00.123456Z"
}
```

### `.cache/youtube-monitor.log`

Standard output log (if using crontab method).

## Auto-Response Templates

### Questions
```
Thanks for the question! 🎯 Check out our resources: [RESOURCE_LINK]. Feel free to reach out if you need more help!
```

### Praise
```
Thank you so much! 💜 We appreciate your support and excitement. Looking forward to what you build!
```

### Spam
❌ No auto-response (filtered out)

### Sales
❌ Flagged for manual review (requires human touch)

## Customizing Templates

Edit the `CATEGORIES` dict in `.cache/youtube-monitor.py`:

```python
'question': {
    'keywords': ['how', 'cost', 'price', 'timeline', ...],
    'response': "Your custom response here"
}
```

## Monitoring & Troubleshooting

### Check Logs

```bash
tail -f .cache/youtube-monitor.log
```

### View Recent Comments

```bash
tail -20 .cache/youtube-comments.jsonl | jq
```

### Count by Category

```bash
cat .cache/youtube-comments.jsonl | jq -r '.category' | sort | uniq -c
```

### Manual Test Run

```bash
python3 .cache/youtube-monitor.py
```

### Common Issues

| Issue | Fix |
|-------|-----|
| `401 Unauthorized` | Check API key in config |
| `404 Channel not found` | Verify Channel ID is correct |
| `No module named googleapiclient` | Run `pip install google-api-python-client` |
| Script doesn't run via cron | Check cron log: `log stream --predicate 'eventMessage contains[cd] cron'` |

## Rate Limits

YouTube API free tier:
- **10,000 quota units per day**
- Each comment thread list: ~1-2 units
- Each channel lookup: ~1 unit

Running every 30 minutes (~48 times/day) should stay well under limits.

## Security Notes

- **Never commit** `.cache/youtube-monitor-config.json` to git
- API key is public-read-only (can't modify comments)
- Auto-replies post as the channel owner account (requires OAuth to enable)

---

**Next Step:** Fill in `youtube-monitor-config.json` and test!
