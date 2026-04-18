# YouTube Comment Monitor

Automated YouTube comment monitoring, classification, and auto-response system for the "Concessa Obvius" channel.

## Overview

This system:
- ✅ Fetches new comments from a YouTube channel
- 🏷️ Classifies comments into: QUESTION, PRAISE, SPAM, SALES
- 💬 Auto-responds to QUESTION & PRAISE comments
- 🚩 Flags SALES inquiries for manual review
- 📝 Logs all comments to JSONL for auditing
- 📊 Tracks state and reports statistics

## Files

### Scripts

- **`youtube_monitor.py`** - Main monitoring script. Run every 30 minutes via cron.
- **`youtube_helper.py`** - Helper module with classification, templating, and logging functions.

### Data Files

- **`youtube-comments.jsonl`** - Append-only log of all processed comments (JSONL format).
- **`youtube-monitor-state.json`** - State tracking: last check time, processed count.

## Running the Monitor

### Basic Usage (Test Mode)
```bash
cd /Users/abundance/.openclaw/workspace
python3 .cache/youtube_monitor.py --test
```

### Real YouTube API (when configured)
```bash
# Set API key
export YOUTUBE_API_KEY="your-youtube-api-key-here"

# Run monitor
python3 .cache/youtube_monitor.py --channel "Concessa Obvius"
```

### Cron Setup (Every 30 Minutes)

The cron job should invoke the monitor like this:

```bash
0,30 * * * * cd /Users/abundance/.openclaw/workspace && python3 .cache/youtube_monitor.py >> .cache/youtube_monitor.log 2>&1
```

This runs at :00 and :30 minutes of every hour.

**Cron ID:** `114e5c6d-ac8b-47ca-a695-79ac31b5c076`

## Comment Classification

Comments are classified using keyword matching:

### QUESTION
Keywords: "how", "tools", "cost", "timeline", "where", "what", "can i", "do i", "should i", "help", "?"
- **Auto-response:** YES
- **Template:** "Thanks for the great question! Check our FAQ or feel free to ask for specifics. We're here to help! 🙌"

### PRAISE
Keywords: "amazing", "inspiring", "love", "great", "awesome", "incredible", "thank you", "thanks", "brilliant", "excellent"
- **Auto-response:** YES
- **Template:** "Thank you so much! We're thrilled this resonated with you. Your support means everything! 🙏"

### SPAM
Keywords: "crypto", "nft", "bitcoin", "mlm", "affiliate", "click here", "link in bio", "casino", "poker", "forex"
- **Auto-response:** NO
- **Action:** Skipped (not logged for response, but recorded in history)

### SALES
Keywords: "partnership", "collaboration", "sponsorship", "promote", "interested in working", "brand deal", "sponsor"
- **Auto-response:** NO
- **Action:** Flagged for manual review

## Data Format

### youtube-comments.jsonl

Each line is a valid JSON object:

```json
{
  "timestamp": "2026-04-18T04:00:00Z",
  "comment_id": "ABC123",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "QUESTION",
  "response_status": "sent",
  "response_text": "Thanks for the great question!..."
}
```

**Fields:**
- `timestamp` - ISO 8601 timestamp (UTC)
- `comment_id` - Unique YouTube comment ID
- `commenter` - YouTube username of commenter
- `text` - Full comment text
- `category` - QUESTION | PRAISE | SPAM | SALES
- `response_status` - sent | skipped | flagged | pending
- `response_text` - The auto-response text sent (null if no response)

### youtube-monitor-state.json

Tracks monitor state:

```json
{
  "last_check": "2026-04-18T04:00:00Z",
  "last_comment_id": "XYZ789",
  "processed_count": 42
}
```

**Fields:**
- `last_check` - ISO 8601 timestamp of last monitor run
- `last_comment_id` - ID of most recent comment processed
- `processed_count` - Total comments processed (cumulative)

## Configuration

### Setting YouTube API Key

```bash
# Add to your shell profile (~/.zshrc or ~/.bash_profile)
export YOUTUBE_API_KEY="your-api-key-here"

# Or set inline
YOUTUBE_API_KEY="your-key" python3 .cache/youtube_monitor.py
```

To get a YouTube API key:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create credentials (API key or OAuth 2.0)
5. Set the environment variable

### Customizing Keywords

Edit `youtube_helper.py`:

```python
KEYWORDS = {
    "QUESTION": [...],
    "PRAISE": [...],
    "SPAM": [...],
    "SALES": [...]
}
```

### Customizing Auto-Response Templates

Edit `youtube_helper.py`:

```python
RESPONSE_TEMPLATES = {
    "QUESTION": "Your custom question response...",
    "PRAISE": "Your custom praise response...",
}
```

## Output & Reporting

Each run generates a report like:

```
============================================================
📊 YOUTUBE COMMENT MONITOR - RUN REPORT
============================================================

✅ Comments processed this run: 5
  • Questions: 1
  • Praise: 2
  • Sales inquiries: 1
  • Spam: 1

📝 Auto-responses sent: 3
   (1 QUESTION + 2 PRAISE)

🚩 Flagged for review (SALES): 1

🚫 Spam skipped: 1

📊 Cumulative statistics (all-time):
  • Total comments processed: 5
  • Questions: 1
  • Praise: 2
  • Sales: 1
  • Spam: 1
  • Total responses sent: 3

⏰ Last check: 2026-04-18T04:01:27Z
🔄 Run time: 2026-04-18T04:01:27Z

============================================================
```

## Logging

By default, the monitor logs to stdout. For cron jobs, redirect to a log file:

```bash
python3 .cache/youtube_monitor.py >> .cache/youtube_monitor.log 2>&1
```

View recent logs:
```bash
tail -f .cache/youtube_monitor.log
```

## Idempotency

All files are designed to be idempotent — safe to run multiple times:
- Comments are deduplicated by `comment_id`
- State tracking prevents reprocessing
- JSONL is append-only

## Troubleshooting

### No comments found
- Channel name might be wrong (check `--channel` parameter)
- API key might be invalid or lacking permissions
- Comment fetching endpoint might need adjustment

### Comments not classified correctly
- Review keywords in `youtube_helper.py`
- Check if comment text contains exact keyword match (case-insensitive)
- Consider adding new keywords

### API quota exceeded
- YouTube API has quotas. Monitor your usage in Google Cloud Console.
- Reduce check frequency or use pagination offsets.

### State file corruption
- Delete `.cache/youtube-monitor-state.json` to reset
- Monitor will restart from scratch on next run

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Cron Job (every 30 min)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
    ┌────────────────────────────────┐
    │   youtube_monitor.py (main)    │
    │  • Fetch comments              │
    │  • Filter by timestamp         │
    └────────────┬───────────────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
    ┌──────────────────────────────────────┐
    │  youtube_helper.py (utilities)       │
    │  • classify_comment()                │
    │  • get_response_text()               │
    │  • log_comment()                     │
    │  • load/save state                   │
    │  • get_stats()                       │
    └────────┬───────────────────┬────────┘
             │                   │
        ┌────▼──────┐      ┌─────▼──────────────┐
        ▼            ▼      ▼                   ▼
    ┌─────────────────────────────────────────────────────┐
    │         Persistent Data Layer                       │
    │  • youtube-comments.jsonl (audit log)              │
    │  • youtube-monitor-state.json (state)              │
    └─────────────────────────────────────────────────────┘
```

## Future Enhancements

- [ ] YouTube API integration (currently uses mock data for testing)
- [ ] Custom response templates per comment type
- [ ] Reply threading (respond to specific comment threads)
- [ ] Rate limiting (max responses per hour)
- [ ] Dashboard/web UI for monitoring
- [ ] Email notifications for SALES comments
- [ ] Machine learning classification refinement
- [ ] Multi-channel support

## Support & Debugging

For detailed logs, enable verbose mode (edit `youtube_monitor.py` to add `--verbose` flag):

```bash
python3 .cache/youtube_monitor.py --verbose --test
```

Check state at any time:
```bash
cat .cache/youtube-monitor-state.json
```

Count comments by category:
```bash
grep -o '"category":"[^"]*"' .cache/youtube-comments.jsonl | sort | uniq -c
```

View all flagged comments awaiting review:
```bash
grep '"response_status":"flagged"' .cache/youtube-comments.jsonl
```

---

**Created:** 2026-04-18  
**Last Updated:** 2026-04-18  
**Version:** 1.0.0
