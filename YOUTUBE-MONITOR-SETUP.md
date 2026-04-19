# YouTube Comment Monitor Setup Guide

## Overview
Monitors the Concessa Obvius YouTube channel for new comments every 30 minutes. Auto-responds to questions and praise, flags sales inquiries for review.

## 1. Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## 2. Set Up Google Cloud Credentials

1. **Go to Google Cloud Console:**
   - https://console.cloud.google.com

2. **Create or select a project**

3. **Enable YouTube Data API v3:**
   - Search for "YouTube Data API v3"
   - Click "Enable"

4. **Create OAuth 2.0 Credentials:**
   - Go to "Credentials" → "Create Credentials"
   - Choose "OAuth Client ID"
   - Application type: Desktop application
   - Download the JSON file
   - Save it as: `~/.openclaw/workspace/.cache/credentials.json`

## 3. Configure Channel ID

1. **Get your YouTube channel ID:**
   - Go to youtube.com/account
   - Under "Advanced settings", find "Channel ID"

2. **Edit the config file:**
   ```bash
   open ~/.openclaw/workspace/youtube-monitor-config.json
   ```

3. **Update the channel_id field:**
   ```json
   {
     "channel_id": "UCxxxxxxxxxxxxxxxxxxxxxx",
     ...
   }
   ```

## 4. First Run (Manual)

```bash
python ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

This will:
- Authenticate with Google (opens browser)
- Fetch recent comments
- Categorize them
- Log results to `.cache/youtube-comments.jsonl`
- Show statistics

## 5. Set Up Cron Job

```bash
crontab -e
```

Add this line to run every 30 minutes:

```
*/30 * * * * python ~/.openclaw/workspace/.cache/youtube-comment-monitor.py >> ~/.openclaw/workspace/.cache/youtube-monitor.log 2>&1
```

## 6. Verify Setup

Check the log file:
```bash
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log
```

## Comment Categories

| Category | Auto-Response | Action |
|----------|---------------|--------|
| **questions** | ✅ Yes | Template: "Thanks for your question! 💡..." |
| **praise** | ✅ Yes | Template: "Thank you so much! 🙏..." |
| **spam** | ❌ No | Logged and ignored (crypto, MLM, etc.) |
| **sales** | ❌ No | 🚩 Flagged for manual review |
| **neutral** | ❌ No | Logged, no action |

## Log Files

- **youtube-comments.jsonl** - Complete comment log with categorization
- **seen-comment-ids.json** - IDs of already-processed comments (prevents duplicates)
- **youtube-monitor.log** - Cron execution log
- **youtube-monitor-config.json** - Configuration (channel ID, templates)

## Query the Comment Log

```bash
# Count by category
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Recent comments
tail -20 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq '.'

# Search for specific author
jq 'select(.commenter | contains("AuthorName"))' ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

## Troubleshooting

**"Channel not found" error:**
- Verify channel_id is correct in config
- Make sure it's a valid YouTube channel ID (starts with UC)

**OAuth token expired:**
- Delete `~/.openclaw/workspace/.cache/youtube-token.json`
- Run script again to re-authenticate

**API quota exceeded:**
- YouTube API has rate limits
- Check Google Cloud Console → Quotas
- Default allows ~10K requests/day

**No new comments found:**
- Monitor checks 5 most recent videos
- Comments are sorted by relevance
- May need to wait for channel to receive new comments

## Customization

Edit `youtube-monitor-config.json` to:
- Change auto-response templates
- Add custom keyword detection
- Adjust category thresholds

Example:
```json
{
  "channel_id": "UCxxxxxxxxxxxxxxxxxxxxxx",
  "templates": {
    "questions": "Thanks for asking! Check out [LINK_TO_RESOURCE]",
    "praise": "Your support means everything! 🙌"
  }
}
```

## Next Steps

- Monitor log file for first week
- Manually review flagged sales comments
- Refine category keywords if needed
- Add custom response templates
