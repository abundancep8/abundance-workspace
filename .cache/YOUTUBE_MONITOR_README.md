# YouTube Comment Monitor - Setup & Usage

## What It Does

Monitors the **Concessa Obvius** YouTube channel for new comments every 30 minutes. Each comment is automatically:

1. **Categorized** into one of four types:
   - **Questions** (how-to, pricing, tools, timeline)
   - **Praise** (compliments, inspiration)
   - **Spam** (crypto, MLM, suspicious links)
   - **Sales** (partnerships, sponsorships, B2B inquiries)

2. **Actioned**:
   - Questions & Praise → Auto-responded with template message
   - Sales & Spam → Flagged for manual review

3. **Logged** to `youtube-comments.jsonl` with:
   - Timestamp, commenter name, text, category
   - Response status and template used

## Setup

### 1. Enable YouTube API

You need a YouTube API key and OAuth credentials for auto-replying:

```bash
# Go to Google Cloud Console
https://console.cloud.google.com/

# Create project → Enable YouTube Data API v3
# Create OAuth 2.0 credentials (Desktop application)
# Download JSON and save as:
mkdir -p /Users/abundance/.openclaw/workspace/.secrets
# Save credentials to: .secrets/youtube-credentials.json

# OR for simple comment fetching (read-only):
# Create an API key and set environment variable:
export YOUTUBE_API_KEY="your-api-key-here"
```

### 2. Configure Cron Job

Add to your OpenClaw cron configuration:

```yaml
- name: youtube-comment-monitor
  interval: "*/30 * * * *"  # Every 30 minutes
  command: "python3 /Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor.py"
  env:
    YOUTUBE_API_KEY: "${YOUTUBE_API_KEY}"
```

Or run manually:

```bash
python3 /Users/abundance/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

### 3. Current Status

**Log file:** `.cache/youtube-comments.jsonl`

Each run appends new comments. You can query it:

```bash
# Count comments
wc -l .cache/youtube-comments.jsonl

# View latest entries
tail -5 .cache/youtube-comments.jsonl | jq .

# Filter by category
grep '"category": "spam"' .cache/youtube-comments.jsonl | jq .
```

## Customization

Edit `youtube-comment-monitor.py` to:

- **Change templates**: Modify `CATEGORY_PATTERNS[category]["template"]`
- **Add patterns**: Add regex patterns to detect new keywords
- **Change channel**: Replace "Concessa Obvius" in `fetch_youtube_comments()`
- **Adjust category thresholds**: Modify pattern matching logic

## Note on Auto-Responses

The script is configured to log what _would_ be responded with template messages. Actual YouTube API replies require full OAuth authentication setup. When enabled, the responses will be posted directly to YouTube comments.

## Next Steps

- [ ] Set up YouTube API credentials in `.secrets/youtube-credentials.json`
- [ ] Test live comment fetching
- [ ] Configure cron job for every 30 minutes
- [ ] Review flagged comments periodically
- [ ] Adjust category patterns based on real comment trends
