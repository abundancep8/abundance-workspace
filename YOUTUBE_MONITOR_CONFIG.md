# YouTube Comment Monitor Setup

## Configuration

### Prerequisites

1. **Get YouTube API Key**
   ```bash
   # Visit https://console.cloud.google.com
   # Create project → Enable YouTube Data API v3 → Create API key
   ```

2. **Set Environment Variable**
   ```bash
   export YOUTUBE_API_KEY="your-api-key-here"
   ```

3. **Optional: OAuth Token (for higher quotas)**
   ```bash
   # Place token at ~/.youtube-oauth-token.json
   ```

## Channel Configuration

- **Channel:** Concessa Obvius
- **Monitor Interval:** Every 30 minutes
- **Log File:** `.cache/youtube-comments.jsonl`
- **State File:** `.cache/youtube-monitor-state.json`

## Comment Categories

### 1. Questions (Auto-respond ✅)
Detected patterns:
- How to start, use tools, pricing
- Cost, timeline, getting started
- Question marks at end of comment

**Template:** Provides links to FAQ + getting started guide

### 2. Praise (Auto-respond ✅)
Detected patterns:
- "amazing", "inspiring", "love this"
- "great", "awesome", engagement emojis (❤️, 🔥, 💯)

**Template:** Thank you + acknowledgment

### 3. Spam (Auto-flag ⚠️)
Detected patterns:
- Crypto/Bitcoin mentions
- MLM references
- Adult content links
- Sketchy TLDs (.tk, .ml, .ga)

**Action:** Logged but not responded to

### 4. Sales/Partnerships (Manual review 👁️)
Detected patterns:
- "partnership", "collaboration"
- "sponsor", "affiliate", "work together"

**Action:** Flagged in log + stats report

### 5. Other
Doesn't fit above categories — logged but not responded to

## Logging Format

Each comment is logged as JSON with:
```json
{
  "timestamp": "2026-04-20T15:30:00...",
  "comment_timestamp": "2026-04-20T14:25:00...",
  "video_id": "aBcDeFgHiJk",
  "commenter": "John Doe",
  "text": "This is amazing! How do I get started?",
  "category": "questions",
  "confidence": 0.95,
  "reply_count": 2,
  "response_status": "auto_responded"
}
```

**response_status values:**
- `auto_responded` — Template auto-response sent (categories 1 & 2)
- `flagged` — Flagged for manual review (category 4)
- `none` — Comment logged but no action (spam, other)

## Reports

After each run, you'll see:
- Total comments processed
- Breakdown by category
- Auto-responses sent count
- Manual review flagged count
- Log file location

## Monitoring the Log

```bash
# View recent comments
tail -20 .cache/youtube-comments.jsonl | jq .

# Filter by category
cat .cache/youtube-comments.jsonl | jq 'select(.category=="questions")'

# Count by category
cat .cache/youtube-comments.jsonl | jq -s 'group_by(.category) | map({category: .[0].category, count: length})'

# Find flagged items
cat .cache/youtube-comments.jsonl | jq 'select(.response_status=="flagged")'
```

## Testing

```bash
# Dry run (requires API key)
YOUTUBE_API_KEY="your-key" python3 scripts/youtube-comment-monitor.py

# View state
cat .cache/youtube-monitor-state.json | jq .
```

## Troubleshooting

**"No videos found for channel 'Concessa Obvius'"**
- Verify channel name spelling
- Channel may be private or have a different display name

**"Failed to initialize YouTube API"**
- Check YOUTUBE_API_KEY environment variable is set
- Verify API is enabled in Google Cloud console

**No comments being found**
- Channel may have comments disabled
- Comments may be older than 1-hour lookback window
- Check STATE_FILE to see last_run timestamp

## Customization

### Change Response Templates

Edit `TEMPLATES` dict in `youtube-comment-monitor.py`:
```python
TEMPLATES = {
    "question": "Your custom question response...",
    "praise": "Your custom praise response...",
}
```

### Add Categorization Patterns

Edit `CATEGORY_PATTERNS` in the script:
```python
CATEGORY_PATTERNS = {
    "questions": [
        r'\byour.custom.pattern\b',
        # ... more patterns
    ],
}
```

### Change Monitoring Interval

In `.cron/youtube-comment-monitor`, adjust the schedule (currently every 30 minutes).

## Schedule

This script is configured to run as a cron job every 30 minutes automatically via OpenClaw.

To manually trigger:
```bash
./scripts/youtube-comment-monitor.py
```
