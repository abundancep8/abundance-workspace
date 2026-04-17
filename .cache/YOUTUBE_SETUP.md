# YouTube Comment Monitor Setup

## Prerequisites

### 1. Install Dependencies

```bash
pip install google-api-python-client
```

### 2. Get YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable **YouTube Data API v3**:
   - Search for "YouTube Data API v3"
   - Click "Enable"
4. Create credentials:
   - Go to "Credentials" → "Create Credentials"
   - Choose "API Key" (restrict later for production)
   - Copy the key

### 3. Set Environment Variable

Add to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.):

```bash
export YOUTUBE_API_KEY="your-api-key-here"
```

Then reload:
```bash
source ~/.zshrc  # or ~/.bashrc
```

### 4. Test the Script

```bash
python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py
```

### 5. Set Up Cron Job (Every 30 Minutes)

Edit your crontab:
```bash
crontab -e
```

Add this line:
```
*/30 * * * * source ~/.zshrc && python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log 2>&1
```

## Output Files

- **youtube-comments.jsonl** — Log of all comments, categories, and responses
- **youtube-last-check.json** — Timestamp of last check (prevents duplicates)
- **youtube-monitor.log** — Cron execution log

## Monitoring Logs

View recent runs:
```bash
tail -f /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log
```

View logged comments:
```bash
tail -20 /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl | jq '.'
```

## Customization

Edit `youtube-monitor.py` to:

1. **Change templates** — Update `RESPONSE_TEMPLATES` dict
2. **Adjust patterns** — Modify `PATTERNS` dict for better categorization
3. **Change channel** — Update `CHANNEL_NAME` variable
4. **Modify categories** — Add/remove categories as needed

## Limitations

- **Read-only mode**: Current implementation only reads comments. To auto-post responses, you'd need:
  - OAuth2 authentication (instead of API key)
  - Channel owner's authorization
  - Additional Google API scopes
  
- **Rate limits**: YouTube API has quota limits (~10,000 units/day for free tier)

## Troubleshooting

**"Could not find channel"**
- Double-check channel name spelling
- Channel must be public

**"Permission denied" when posting**
- You need OAuth2 auth + channel owner authorization
- Current setup is read-only

**"Quota exceeded"**
- YouTube API has rate limits
- Increase monitoring interval to 1+ hour
- Consider upgrading to paid YouTube API tier

## Next Steps

For **auto-posting responses**, we'd need to:
1. Switch to OAuth2 authentication
2. Add `youtube` scope for comment writing
3. Implement comment reply logic using `commentThreads().insert()`
4. Store refresh tokens securely

Ask if you want to enable that feature.
