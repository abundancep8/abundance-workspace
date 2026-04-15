# YouTube Comment Monitor - Setup & Configuration

## Requirements

- YouTube Data API v3 enabled
- OAuth2 credentials (client ID, client secret, refresh token)
- Node.js with `googleapis` package

## Setup Steps

### 1. YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable **YouTube Data API v3**
4. Create OAuth2 credentials (Desktop application)
5. Download credentials as JSON

### 2. Get Refresh Token

Run the auth flow once to get a refresh token:

```bash
npm install googleapis google-auth-library --save
node scripts/youtube-auth.js
```

This will prompt you to authorize the application and save tokens to `~/.youtube-credentials.json`

### 3. Update Response Templates

Edit the `TEMPLATES` object in `scripts/youtube-monitor.js`:

```javascript
const TEMPLATES = {
  questions: `Your custom response for questions...`,
  praise: `Your custom response for praise...`
};
```

### 4. Configure Cron

Add to your crontab (runs every 30 minutes):

```bash
*/30 * * * * cd /Users/abundance/.openclaw/workspace && node scripts/youtube-monitor.js >> logs/youtube-monitor.log 2>&1
```

## Outputs

- **Log file:** `.cache/youtube-comments.jsonl` — one JSON object per line
- **State file:** `.cache/youtube-monitor-state.json` — tracks processed comments
- **Cron log:** `logs/youtube-monitor.log` — execution history

## Monitoring

```bash
# Watch real-time
tail -f logs/youtube-monitor.log

# View recent comments
tail -20 .cache/youtube-comments.jsonl | jq .

# Count by category today
jq 'select(.timestamp | startswith("2026-04-14")) | .category' .cache/youtube-comments.jsonl | sort | uniq -c
```

## Categorization Rules

- **Questions:** Contains `?`, "how", "what", "cost", "tools", "timeline", "where to start"
- **Praise:** Contains "amazing", "inspiring", "love", "awesome", "thank you", "life-changing"
- **Spam:** Contains "crypto", "bitcoin", "mlm", "work from home", "discord server"
- **Sales:** Contains "partnership", "collaboration", "sponsor", "brand deal", "affiliate"

Flagged for manual review only.

## Troubleshooting

**"Channel not found"** → Check channel name spelling in script
**"Credentials invalid"** → Refresh token may have expired; re-run auth flow
**"Rate limited"** → YouTube API has quotas; script respects them automatically

---

Ready to activate? Provide your YouTube API credentials and I'll integrate them.
