# 🎥 YouTube Comment Monitor System

**Status:** Ready to deploy | **Version:** 1.0.0 | **Run Interval:** Every 30 minutes

## What This Does

Monitors the **Concessa Obvius** YouTube channel for new comments, automatically categorizes them, and responds to legitimate inquiries while flagging sales pitches for review.

### Automatic Processing

Each comment is categorized into:

1. **Questions** (40 comment templates for how-to, pricing, timeline, tools)
   - ✅ Auto-responds with helpful resources
   - 📝 Logged with response status

2. **Praise** (amazing, inspiring, awesome, etc.)
   - ✅ Auto-responds with appreciation message
   - 📝 Logged with response status

3. **Spam** (crypto, MLM, schemes, etc.)
   - ⏭️ Skipped (not logged by default, can be enabled)
   - 📝 Labeled for easy filtering

4. **Sales** (partnerships, sponsorships, collaborations)
   - 🚩 Flagged for manual review
   - 📝 Logged separately for action

5. **Other**
   - 📝 Logged only, no response

## Files

### Core Scripts

- **`youtube-monitor.py`** — Main monitoring script
  - Fetches latest comments from channel
  - Categorizes each using pattern matching
  - Logs results to JSONL
  - Generates reports
  
- **`setup-youtube-monitor.sh`** — One-click setup
  - Installs dependencies
  - Validates API key
  - Tests configuration
  - Provides cron instructions

### Configuration & Docs

- **`YOUTUBE_SETUP.md`** — Detailed setup guide
  - API key creation
  - Environment variables
  - Cron configuration
  - Troubleshooting

- **`YOUTUBE_MONITOR_README.md`** — This file
  - Overview and usage
  - Output format
  - Customization

### Data Files

- **`youtube-comments.jsonl`** — All comments log
  ```json
  {
    "timestamp": "2026-04-17T01:30:00",
    "commenter": "Jane Doe",
    "text": "How do I get started?",
    "category": "questions",
    "response_status": "auto_responded (questions)",
    "video_id": "abc123"
  }
  ```

- **`youtube-last-check.json`** — Last run timestamp (prevents re-processing)

- **`youtube-monitor.log`** — Cron execution log (when running via cron)

## Quick Start

### 1. Run Setup

```bash
bash /Users/abundance/.openclaw/workspace/.cache/setup-youtube-monitor.sh
```

### 2. Set API Key

```bash
export YOUTUBE_API_KEY="your-key-from-google-cloud-console"
```

Add to `~/.zshrc` or `~/.bashrc` to persist.

### 3. Test

```bash
python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py
```

Expected output:
```
🔍 Looking up 'Concessa Obvius' channel...
✓ Found channel: UC...
📝 Checking for comments since: 2026-04-17T01:00:00
✓ Found 3 new comment(s)
  ✓ Auto-response queued: Questions
  ✓ Auto-response queued: Praise
  ⚠️  Flagged for review: Sales

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 YouTube Comment Monitor Report
...
```

### 4. Schedule (Cron)

Edit crontab:
```bash
crontab -e
```

Add:
```
*/30 * * * * source ~/.zshrc && python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log 2>&1
```

This runs every 30 minutes.

## Viewing Results

### Recent Comments

```bash
tail -20 /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl | jq '.'
```

### Cron Log

```bash
tail -f /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log
```

### Stats

```bash
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl
```

## Customization

### Change Response Templates

Edit `youtube-monitor.py`, find `RESPONSE_TEMPLATES`:

```python
RESPONSE_TEMPLATES = {
    "questions": """Your custom question response here...""",
    "praise": """Your custom praise response here..."""
}
```

### Adjust Categorization Patterns

Edit `PATTERNS` dict to match different phrases:

```python
PATTERNS = {
    "questions": [
        r"how\s+(do\s+i|can\s+i)",  # Add your patterns
    ],
    ...
}
```

### Monitor Different Channel

Change `CHANNEL_NAME`:

```python
CHANNEL_NAME = "Your Channel Name"
```

### Change Run Interval

In crontab, change `*/30` to:
- `*/5` — Every 5 minutes
- `0 * * * *` — Hourly (top of hour)
- `0 9 * * *` — Daily at 9 AM

## Limitations & Known Issues

### Current Limitations

1. **Read-only mode** — Script only reads comments, doesn't post yet
2. **No reply threading** — Logs responses but doesn't post them (requires OAuth2)
3. **Rate limits** — YouTube API has quotas
4. **Simple categorization** — Pattern matching only (no ML/NLP)

### To Enable Auto-Posting

Requires:
- OAuth2 authentication (instead of API key)
- YouTube channel owner authorization
- Storing refresh tokens
- Adding `youtube` scope

Ask to enable this feature — I can upgrade the script.

## Monitoring & Alerts

### Check Status

```bash
echo "Last check:" && jq .last_check /Users/abundance/.openclaw/workspace/.cache/youtube-last-check.json
```

### Count Categories

```bash
echo "By category:" && jq -r '.category' /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl | sort | uniq -c
```

### Filter by Category

```bash
# Show all sales inquiries (flagged for review)
jq 'select(.category=="sales")' /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl
```

## Troubleshooting

### "Could not find channel"
- Check spelling of `CHANNEL_NAME`
- Ensure channel is public
- Wait a few minutes and try again

### "Permission denied"
- Your API key needs YouTube Data API enabled
- Go to Google Cloud Console → APIs & Services
- Search "YouTube Data API v3" and enable it

### "Quota exceeded"
- YouTube API has daily limits (~10,000 units)
- Reduce monitoring frequency
- Consider upgrading API tier

## API Key Security

### Best Practices

1. **Never commit to git** — Keep in environment variables only
2. **Use Application Restrictions** — In Google Cloud Console:
   - Set to "IP addresses" (your home IP)
   - Or "HTTP referrers" (localhost)
3. **Rotate regularly** — Delete old keys, create new ones
4. **Monitor usage** — Check Google Cloud Console for unusual activity

### Production Setup

For production:
```bash
# Use secrets manager
export YOUTUBE_API_KEY=$(aws secretsmanager get-secret-value --secret-id youtube-api-key --query SecretString --output text)
```

## Success Metrics

This system tracks:
- ✅ Total comments processed
- ✅ Auto-responses sent
- ✅ Items flagged for review
- ✅ Categorization accuracy
- ✅ Response coverage (% with auto-reply)

Check `youtube-monitor.log` for each run's report.

## Next Steps

1. ✅ Run `setup-youtube-monitor.sh`
2. ✅ Set `YOUTUBE_API_KEY`
3. ✅ Test with `python youtube-monitor.py`
4. ✅ Add to crontab for every 30 minutes
5. 📊 Monitor with `tail -f youtube-monitor.log`
6. 🎯 Customize templates and patterns as needed

---

**Need help?** Check `YOUTUBE_SETUP.md` for detailed troubleshooting.
