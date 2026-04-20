# YouTube Comment Monitor Setup

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install google-auth-oauthlib google-api-python-client
   ```

2. **Set up YouTube API credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials (Desktop application)
   - Download credentials JSON as `~/.openclaw/youtube-credentials.json`

3. **Find your channel ID:**
   - Go to channel "About" tab
   - Copy the channel ID (starts with `UC`)
   - Update `CHANNEL_ID` in `youtube-monitor.py`

## Configuration

Edit `youtube-monitor.py`:
- **CHANNEL_ID**: Your target channel ID (Concessa Obvius)
- **TEMPLATES**: Customize auto-response messages
- **CATEGORIES**: Add/modify comment patterns

## Run Manually

```bash
cd /Users/abundance/.openclaw/workspace
python3 .cache/youtube-monitor.py
```

## Set Up Cron (Every 30 minutes)

Add to crontab (`crontab -e`):
```cron
*/30 * * * * cd /Users/abundance/.openclaw/workspace && python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1
```

Or use OpenClaw's native cron integration.

## Output Files

- **`.cache/youtube-comments.jsonl`** - Full comment log (JSONL format)
- **`.cache/youtube-monitor-state.json`** - State tracking (processed IDs, last run)
- **`.cache/youtube-monitor.log`** - Execution log (if using cron)

## Log Format

Each line in `youtube-comments.jsonl`:
```json
{
  "timestamp": "2026-04-20T06:30:00",
  "comment_timestamp": "2026-04-19T22:15:00Z",
  "commenter": "User Name",
  "text": "Comment text here",
  "category": "questions|praise|spam|sales|other",
  "response_status": "none|sent|flagged",
  "likes": 5,
  "video_id": "abc123"
}
```

## Sample Query: Get All Flagged Sales Comments

```bash
cat .cache/youtube-comments.jsonl | jq 'select(.category == "sales" and .response_status == "flagged")'
```

## Monitoring the Monitor

To check latest activity:
```bash
tail -20 .cache/youtube-comments.jsonl | jq .
```

Count by category:
```bash
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' .cache/youtube-comments.jsonl
```

## Troubleshooting

**"YouTube credentials file not found"**
- Ensure OAuth credentials are saved to `~/.openclaw/youtube-credentials.json`

**"Channel not found"**
- Verify CHANNEL_ID is correct
- Make sure you're using the channel ID, not username

**Rate limits**
- YouTube API has quotas; monitor usage in Cloud Console
- Running every 30 minutes should be safe for a single channel

## Rate Limiting

Default YouTube API quota: **10,000 units/day**
This script uses ~50-100 units per run, so 30-min intervals = ~1,400-2,800 units/day. Safe.
