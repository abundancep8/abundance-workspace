# YouTube Comment Monitor

Automated system to monitor YouTube comments on the Concessa Obvius channel, categorize them, auto-respond, and log everything.

## What It Does

**Every 30 minutes:**
1. ✅ Fetches new comments from your channel
2. 🏷️ Categorizes each comment into 4 types:
   - **Questions** (how do I start, tools, cost, timeline)
   - **Praise** (amazing, inspiring, thank you)
   - **Spam** (crypto, MLM, suspicious links)
   - **Sales** (partnership, collaboration requests)
3. 📝 Auto-responds to Questions & Praise with templates
4. 🚩 Flags Sales inquiries for your manual review
5. 📊 Logs everything to `youtube-comments.jsonl`
6. 📈 Reports stats: total processed, auto-responses sent, flagged

## Files

```
.cache/
├── youtube-monitor.py              ← Main script
├── youtube-monitor-setup.sh        ← Setup script
├── youtube-monitor-state.json      ← Tracks processed comments
├── youtube-credentials.json        ← YouTube API credentials (you add)
├── youtube-comments.jsonl          ← Comment log (auto-created)
└── youtube-monitor-cron.log        ← Cron execution log
```

## Quick Start

### 1. Run Setup
```bash
cd ~/.openclaw/workspace/.cache
chmod +x youtube-monitor-setup.sh
./youtube-monitor-setup.sh
```

This:
- Makes the monitor script executable
- Installs Python dependencies
- Adds a cron job to run every 30 minutes
- Creates log directories

### 2. Configure YouTube API (for real comments)

**Currently the monitor runs in MOCK MODE** (sample data for testing).

To enable real YouTube monitoring:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Create OAuth 2.0 credentials:
   - Type: **Desktop application**
   - Download as JSON
5. Save to: `~/.openclaw/workspace/.cache/youtube-credentials.json`
6. Update `CHANNEL_ID` in `youtube-monitor.py` with your actual channel

### 3. Customize Responses

Edit the `TEMPLATE_RESPONSES` dict in `youtube-monitor.py`:

```python
TEMPLATE_RESPONSES = {
    "questions": [
        "Your response here...",
        "Alternative response...",
    ],
    "praise": [
        "Your thank you response...",
    ],
}
```

### 4. Test It
```bash
python3 youtube-monitor.py
```

You'll see output like:
```
📺 Fetching comments...
❓ questions     | User1           | auto_responded
👏 praise        | User2           | auto_responded
🚫 spam          | User3           | spam_ignored
🚩 sales         | User4           | flagged_for_review

============================================================
📊 YOUTUBE COMMENT MONITOR REPORT
============================================================
⏱️  Timestamp: 2026-04-17T08:30:00.123456
📝 Total Comments Processed: 4
✅ Auto-Responses Sent: 2
🚩 Flagged for Review: 1
============================================================
```

## Monitoring

### View Logs
```bash
# Real-time cron logs
tail -f ~/.openclaw/workspace/.cache/youtube-monitor-cron.log

# Comment log (JSONL format)
tail ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .

# State tracking
cat ~/.openclaw/workspace/.cache/youtube-monitor-state.json
```

### Comment Log Format (JSONL)
Each line is a JSON object:
```json
{
  "timestamp": "2026-04-17T08:30:15.123456",
  "comment_id": "comment123",
  "commenter": "John Smith",
  "text": "How do I get started?",
  "category": "questions",
  "response_status": "auto_responded",
  "response": "Great question! Check...",
  "published_at": "2026-04-17T08:25:00Z"
}
```

## Categories & Actions

| Category | Detection | Action | Example |
|----------|-----------|--------|---------|
| **Questions** | "how", "what", "cost", "timeline", "tools", "help" | Auto-respond with template | "How do I start?" |
| **Praise** | "amazing", "inspiring", "love", "thank you" | Auto-respond with thanks | "This is incredible!" |
| **Spam** | "crypto", "MLM", "forex", "click link" | Ignore silently | "Bitcoin signals - DM me" |
| **Sales** | "partnership", "collaboration", "sponsor" | Flag for review | "Want to partner?" |
| **Other** | No matches | Log only | Random comment |

## Customization

### Change Detection Patterns
Edit `PATTERNS` dict in `youtube-monitor.py`:
```python
PATTERNS = {
    "questions": [
        r"\bhow\b.*\b(do|can|should)\b",
        r"\byour custom pattern\b",
    ],
    # ... etc
}
```

### Change Auto-Response Behavior
- **Disable auto-responses:** Set `response_status = "none"` for any category
- **Add manual review for praise:** Change to `"flagged_for_review"`
- **Custom logic:** Edit the response decision tree in `process_comments()`

### Change Run Frequency
Edit cron expression (currently `*/30 * * * *` = every 30 minutes):
```bash
crontab -e
# Change to:
# */15 * * * * = every 15 minutes
# 0 * * * * = every hour
# 0 9 * * * = daily at 9 AM
```

## Troubleshooting

### Cron job not running?
```bash
# Check if job exists
crontab -l | grep youtube-monitor

# View system logs
log stream --predicate 'eventMessage contains[cd] "youtube-monitor"' --level debug
```

### "YouTube API not installed"
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Comments not fetching?
- Check `youtube-credentials.json` exists and is valid
- Verify `CHANNEL_ID` in `youtube-monitor.py`
- Check cron log: `tail ~/.openclaw/workspace/.cache/youtube-monitor-cron.log`

### Wrong channel responses?
- Update `CHANNEL_ID` variable with your actual channel ID
- Find it: YouTube Settings → About → "Channel ID: UC..."

## Notes

- **Mock mode** (default): Runs without YouTube API credentials for testing
- **Real mode**: Requires OAuth 2.0 credentials from Google Cloud Console
- **Rate limits**: YouTube API allows ~10K quota units/day; comment fetching uses ~1 unit per comment
- **State tracking**: Uses `youtube-monitor-state.json` to avoid reprocessing comments
- **Template responses**: Randomly picks from your list to vary responses

## Future Enhancements

- [ ] Sentiment analysis (not just keywords)
- [ ] Smarter spam detection (regex + LLM)
- [ ] Reply directly to comments (YouTube API support)
- [ ] Custom filtering by channel section or playlist
- [ ] Email/Slack notifications for flagged comments
- [ ] A/B testing response templates
