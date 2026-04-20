# YouTube Comment Monitor - Setup Guide

## Installation

### 1. Install Dependencies
```bash
pip install google-auth-oauthlib google-api-python-client
```

### 2. Get YouTube API Key

#### Option A: Simple API Key (Read-Only, No Replies)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Create an **API Key** credential
5. Set environment variable:
```bash
export YOUTUBE_API_KEY="your-api-key-here"
```

#### Option B: OAuth 2.0 (For Auto-Replying)
If you need the script to post replies:
1. In Google Cloud Console, create an **OAuth 2.0 Client ID** (Desktop app)
2. Download the credentials JSON
3. Follow the OAuth flow when the script runs
4. Store the token in `.cache/youtube-token.json`

### 3. Get Channel ID

Find your YouTube channel ID:
- Visit your channel on YouTube
- URL: `https://www.youtube.com/channel/UCxxxxxxxxxx`
- Copy the `UCxxxxxxxxxx` part

Set environment variable:
```bash
export YOUTUBE_CHANNEL_ID="UCyourChannelIdHere"
```

### 4. Create `.env` File (Optional)

Create `.env` in workspace root:
```bash
YOUTUBE_API_KEY=your-api-key-here
YOUTUBE_CHANNEL_ID=UCyourChannelIdHere
```

Then load it before running:
```bash
set -a; source .env; set +a
python scripts/youtube-comment-monitor.py
```

## Running the Monitor

### Manual Run
```bash
export YOUTUBE_API_KEY="your-key"
export YOUTUBE_CHANNEL_ID="your-channel"
python scripts/youtube-comment-monitor.py
```

### Automated (Every 30 Minutes)
Add to crontab:
```bash
*/30 * * * * cd /Users/abundance/.openclaw/workspace && python scripts/youtube-comment-monitor.py >> .cache/monitor.log 2>&1
```

## Output Files

- **`.cache/youtube-comments.jsonl`** - All comments (append-only log)
- **`.cache/youtube-review.txt`** - Sales/partnerships flagged for manual review
- **`.cache/youtube-monitor.json`** - State file (tracks processed comments)
- **`.cache/monitor.log`** - Cron execution log

## Comment Categories

| # | Category | Keywords | Action |
|---|----------|----------|--------|
| 1 | Questions | how, start, tools, cost, timeline | Auto-reply with Q template |
| 2 | Praise | amazing, inspiring, great, love | Auto-reply with praise template |
| 3 | Spam | crypto, MLM, forex, gambling | Filter (no action) |
| 4 | Sales | partnership, collaboration, sponsor | Flag for manual review |
| 0 | Uncategorized | None match | Log only |

## Customizing Responses

Edit the `CATEGORIES` dict in the script to modify templates:

```python
2: {
    "name": "Praise",
    "keywords": ["amazing", "inspiring", ...],
    "template": "Your custom praise response here"
}
```

## Troubleshooting

### "YOUTUBE_API_KEY not set"
```bash
export YOUTUBE_API_KEY="your-key"
# Verify:
echo $YOUTUBE_API_KEY
```

### "Permission denied" when replying
- API Key doesn't support write operations
- Need to use OAuth 2.0 flow instead
- Or: Remove `auto_respond()` calls if replies aren't needed

### Rate Limited (429)
- YouTube API has rate limits
- Wait 24 hours or upgrade to higher quota
- Script will log and skip on rate limit

### Channel not found
- Verify `YOUTUBE_CHANNEL_ID` is correct
- Make sure it's a public channel

## Viewing Results

```bash
# View all comments (last 10)
tail -10 .cache/youtube-comments.jsonl

# View flagged for review
cat .cache/youtube-review.txt

# View logs
tail .cache/monitor.log
```

## Notes

- **Initial run**: Monitors last 1 hour of comments
- **Subsequent runs**: Only new comments since last check
- **Deduplication**: Uses comment IDs to avoid processing twice
- **Rate limiting**: 10,000 requests/day limit on YouTube API (usually sufficient)
