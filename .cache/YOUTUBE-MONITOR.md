# YouTube Comment Monitor

Automatically monitor, categorize, and respond to comments on the Concessa Obvius YouTube channel.

## Overview

- **Runs:** Every 30 minutes (via cron)
- **Monitors:** Concessa Obvius channel comments
- **Categorizes:** Questions, Praise, Spam, Sales
- **Auto-responds:** To Questions & Praise with templates
- **Flags:** Sales inquiries for manual review
- **Logs:** All comments to `youtube-comments.jsonl` with metadata

## Setup

### Option 1: Using YouTube Data API (Recommended)

1. **Get API credentials:**
   - Visit [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable YouTube Data API v3
   - Create an OAuth 2.0 API key
   - Copy your API key

2. **Configure:**
   ```bash
   export YOUTUBE_API_KEY="your-api-key-here"
   ```
   
   Or add to your shell profile (`.zshrc`, `.bashrc`):
   ```bash
   echo 'export YOUTUBE_API_KEY="your-api-key-here"' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Install dependencies:**
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

### Option 2: Using yt-dlp (No API Key Required)

```bash
pip install yt-dlp
```

This works without authentication but has rate limits.

## Usage

### Run Monitor Now
```bash
python3 ~/.openclaw/workspace/.cache/youtube-monitor.py
```

### View Report
```bash
python3 ~/.openclaw/workspace/.cache/youtube-report.py
```

### View Flagged Comments Only
```bash
python3 ~/.openclaw/workspace/.cache/youtube-report.py --flagged
```

## Schedule (30-minute intervals)

Add to crontab:
```bash
crontab -e
```

Add this line:
```
*/30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.sh >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log 2>&1
```

Or use OpenClaw's cron integration (already configured for this task).

## Files & Logging

- **Monitor script:** `.cache/youtube-monitor.py`
- **Shell wrapper:** `.cache/youtube-monitor.sh`
- **Report tool:** `.cache/youtube-report.py`
- **Comments log:** `.cache/youtube-comments.jsonl` (JSONL format, one per line)
- **State file:** `.cache/youtube-monitor-state.json` (tracks processed comments)

### Log Entry Format
```json
{
  "timestamp": "2026-04-21T05:00:00",
  "comment_id": "Ugx...",
  "author": "Username",
  "text": "Comment text...",
  "category": "questions|praise|spam|sales|other",
  "confidence": 0.75,
  "response_status": "auto_responded|flagged_for_review|spam_filtered|none",
  "response_text": "Auto-response or null",
  "youtube_timestamp": "2026-04-21T04:55:00Z"
}
```

## Categories & Rules

### Questions (Auto-Respond)
Keywords: how, what, where, when, why, start, learn, cost, timeline, tool, tutorial, help, guide, resource

Example:
> "How do I get started with this? Are there any free resources?"

Response: Template message with guidance and resources

### Praise (Auto-Respond)
Keywords: amazing, awesome, great, love, inspiring, helpful, thanks, best, life-changing, game changer

Example:
> "This is amazing! Really inspiring stuff. Thank you!"

Response: Thank you + encouragement message

### Spam (Filter)
Keywords: crypto, bitcoin, MLM, gambling, forex, "click here", "buy now", casino, lottery

Status: `spam_filtered` — not logged separately, just filtered

### Sales (Flag for Review)
Keywords: partnership, collaborate, sponsor, affiliate, contact me, reach out, business opportunity, let's work

Status: `flagged_for_review` — logged and reported

Example:
> "Hey, would love to explore a partnership. Let's DM!"

Action: Flagged in report, awaits manual review

## Auto-Response Templates

### Question Template
```
Thanks for the great question! 🙌 

I appreciate your interest. Here are some resources that might help:
- Check our FAQ/Knowledge Base for common questions
- Feel free to reach out directly if you need specific guidance

Looking forward to seeing you succeed!
```

### Praise Template
```
Thank you so much! 🙏 Your support means everything to us. We're excited to continue sharing insights and helping our community grow.

Stay tuned for more!
```

**Customize these** in `.cache/youtube-monitor.py` → `TEMPLATES` dict.

## Monitoring & Troubleshooting

### Check if running properly
```bash
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log
```

### Test run
```bash
python3 ~/.openclaw/workspace/.cache/youtube-monitor.py
```

### Check state
```bash
cat ~/.openclaw/workspace/.cache/youtube-monitor-state.json | python3 -m json.tool
```

### Common Issues

**"Channel not found"**
- Verify `CHANNEL_NAME` and `CHANNEL_HANDLE` in `youtube-monitor.py`
- Update to match actual channel name/handle

**"No API key or yt-dlp"**
- Install one: `pip install yt-dlp` OR set `YOUTUBE_API_KEY`

**"Rate limited"**
- Using yt-dlp? Try YouTube API key instead (higher limits)
- Using API? Check quota in Google Cloud Console

**Cron not running**
- Check: `crontab -l` 
- Verify path is correct
- Check logs: `tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log`

## Customization

### Edit Channel
In `.cache/youtube-monitor.py`:
```python
CHANNEL_NAME = "Your Channel Name"
CHANNEL_HANDLE = "@YourHandle"
```

### Edit Keywords
In `.cache/youtube-monitor.py` → `CATEGORIES` dict:
```python
"questions": {
    "keywords": [
        "how", "what", "where",  # Add your keywords
        # ...
    ]
}
```

### Edit Response Templates
In `.cache/youtube-monitor.py` → `TEMPLATES` dict

### Change Logging Location
Update `LOG_FILE` and `STATE_FILE` paths in both `.py` files

## Reports & Stats

Run report tool to see:
- ✅ Total comments processed
- ✅ Auto-responses sent
- 🚩 Flagged for review
- 📊 Category breakdown
- 🚫 Spam examples
- ⏱️ Recent activity

```bash
python3 ~/.openclaw/workspace/.cache/youtube-report.py
```

## Manual Response

When you see flagged comments (sales inquiries), you can:
1. Review in report: `python3 ~/.openclaw/workspace/.cache/youtube-report.py --flagged`
2. Reply manually on YouTube
3. Update response status in log if needed

---

**Questions?** Check the logs or run a test: `python3 ~/.openclaw/workspace/.cache/youtube-monitor.py`
