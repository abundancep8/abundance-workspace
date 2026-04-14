# YouTube Comment Monitor Setup

Automated monitoring and auto-response system for Concessa Obvius YouTube channel.

## Quick Start

### 1. Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Get YouTube API Credentials

**Option A: API Key (Read-Only, No Replies)**
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create new project or select existing
- Enable YouTube Data API v3
- Create API key (Credentials → Create Credentials → API Key)
- Save to file:

```bash
echo "YOUTUBE_API_KEY=your-api-key-here" > ~/.openclaw/workspace/.cache/.youtube-env
chmod 600 ~/.openclaw/workspace/.cache/.youtube-env
```

**Option B: OAuth 2.0 (Can Auto-Reply)**
- Go to Google Cloud Console
- Enable YouTube Data API v3
- Create OAuth 2.0 Credentials (Desktop application)
- Download `credentials.json`
- Save to `~/.openclaw/workspace/.cache/youtube-credentials.json`
- First run will prompt to authenticate
- Token will be saved to `~/.openclaw/workspace/.cache/youtube_token.json`

### 3. Set Up Cron Job (Every 30 Minutes)

Make script executable:
```bash
chmod +x ~/.openclaw/workspace/.cache/youtube-monitor.sh
```

Edit crontab:
```bash
crontab -e
```

Add line:
```
*/30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.sh
```

Verify cron job:
```bash
crontab -l
```

### 4. Test the Monitor

Run manually:
```bash
python3 ~/.openclaw/workspace/.cache/youtube-monitor.py
```

Check logs:
```bash
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log
```

View comments processed:
```bash
tail ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

## How It Works

### Comment Categorization

1. **Questions** (Category 1): "How do I...", "What is...", "cost", "timeline", etc.
   - Auto-response: Helpful resource pointer

2. **Praise** (Category 2): "Amazing", "Inspiring", "Love this", etc.
   - Auto-response: Thank you message

3. **Spam** (Category 3): "Crypto", "Bitcoin", "MLM", "Get rich quick", etc.
   - Action: Logged, no response (can manually delete)

4. **Sales/Partnership** (Category 4): "Partnership", "Collaboration", "Brand deal", etc.
   - Action: Flagged for manual review (no auto-response)

### Files Created

- `youtube-comments.jsonl` - All comments with metadata (timestamp, author, category, response status)
- `youtube-monitor-state.json` - Persistent state (last check time, running totals)
- `youtube-monitor.log` - Script logs and errors

## Monitoring

View current stats:
```bash
cat ~/.openclaw/workspace/.cache/youtube-monitor-state.json | jq
```

Search comments (e.g., all questions):
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq 'select(.category == 1)'
```

Find flagged sales pitches:
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq 'select(.response_status == "flagged")'
```

## Configuration

### Change Channel

Edit `youtube-monitor.py`:
```python
CHANNEL_ID = "YOUR_CHANNEL_ID_HERE"  # Replace this
```

Find channel ID:
1. Go to YouTube channel
2. Look at URL: `youtube.com/@username` or `youtube.com/channel/UCxxxxxx`
3. Use the `UCxxxxxx` part

### Customize Response Templates

Edit `RESPONSES` dict in `youtube-monitor.py`:
```python
RESPONSES = {
    1: "Your custom question response here",
    2: "Your custom praise response here",
}
```

### Adjust Category Keywords

Edit `CATEGORY_PATTERNS` dict to add or remove keywords that trigger each category.

## Troubleshooting

**"YOUTUBE_API_KEY environment variable not set"**
- Run: `source ~/.openclaw/workspace/.cache/.youtube-env`
- Or add to `.zshrc`: `export YOUTUBE_API_KEY="your-key"`

**"No videos found"**
- Verify channel ID is correct
- Check API key has YouTube Data API access
- Ensure channel has public videos

**"Failed to reply to comment"**
- OAuth credentials may have expired (delete `youtube_token.json` and re-authenticate)
- YouTube account may lack channel management permissions
- API quota may be exceeded (YouTube Data API has daily limits)

**Cron not running**
- Check cron is enabled: `sudo launchctl list | grep cron`
- Verify script path is absolute (not relative)
- Check logs: `log stream --predicate 'process == "cron"'`
- Test manually: Run the script directly from terminal

## API Quotas

YouTube Data API free tier allows 10,000 quota units/day:
- `search.list`: 100 units
- `commentThreads.list`: 1 unit per comment thread
- `comments.insert`: 50 units per reply

With this monitor running every 30 minutes (~48x/day) on a channel with 5 videos:
- Estimate: ~200 units/day (well under limit)

## Logs and History

Keep recent comments for analytics:
```bash
# Get comments from last 7 days
jq 'select(.timestamp > now - (7 * 24 * 3600) | todate)' ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

Archive old logs:
```bash
gzip ~/.openclaw/workspace/.cache/youtube-monitor.log
```
