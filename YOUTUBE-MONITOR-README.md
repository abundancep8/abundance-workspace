# YouTube Comment Monitor for Concessa Obvius

An autonomous Python tool that monitors comments on the Concessa Obvius YouTube channel, categorizes them intelligently, auto-responds to questions and praise, and logs everything for review.

**Status**: Production-ready | **Language**: Python 3.8+ | **Dependencies**: google-api-python-client

---

## What It Does

✅ **Fetches comments** from Concessa Obvius YouTube videos (OAuth2 authenticated)  
✅ **Categorizes** comments by keyword matching (questions, praise, spam, sales)  
✅ **Auto-responds** to questions and praise with template messages  
✅ **Logs everything** to `.cache/youtube-comments.jsonl` for analysis  
✅ **Reports statistics** on each run (processed, responded, flagged)  
✅ **Idempotent** — never processes the same comment twice  
✅ **Graceful error handling** — resumes from last run if interrupted  
✅ **Rate limit aware** — handles API quota limits elegantly  

---

## Quick Start (5 Minutes)

### 1. Install
```bash
pip install -r youtube-monitor-requirements.txt
```

### 2. Get OAuth2 Credentials
```bash
# See YOUTUBE-MONITOR-SETUP.md for detailed steps
# TL;DR: Get client_secret.json from Google Cloud Console, then:
python setup-youtube-credentials.py
# → Opens browser for authentication
# → Saves credentials to ~/.youtube/credentials.json
```

### 3. Run It
```bash
python youtube-monitor.py
```

**Output:**
```
======================================================================
RUN STATISTICS
======================================================================
Total comments processed: 42
  - Questions: 15
  - Praise: 20
  - Spam: 5
  - Sales: 2
Auto-responses sent: 35
Flagged for review (sales): 2
======================================================================
```

### 4. View Results
```bash
# View statistics
python youtube-monitor-query.py stats

# View unanswered questions
python youtube-monitor-query.py unanswered

# View recent comments
python youtube-monitor-query.py recent 20

# View by category
python youtube-monitor-query.py category spam
```

---

## Architecture

### Scripts

| File | Purpose |
|------|---------|
| `youtube-monitor.py` | Main monitor — fetches, categorizes, responds, logs |
| `setup-youtube-credentials.py` | OAuth2 credential setup (run once) |
| `youtube-monitor-query.py` | Query & analyze the comments log |

### Data Files

| Location | Purpose |
|----------|---------|
| `.cache/youtube-comments.jsonl` | All processed comments (append-only log) |
| `.cache/youtube-monitor-state.json` | Last run state (resume point) |
| `.cache/youtube-monitor.log` | Execution logs |
| `~/.youtube/credentials.json` | OAuth2 access tokens |

---

## Comment Categorization

Matches keywords (case-insensitive):

```
┌─────────────┬───────────────────────────────────────────────┐
│ Category    │ Keywords                                      │
├─────────────┼───────────────────────────────────────────────┤
│ Questions   │ how, help, tools, cost, timeline, tutorial    │
│ Praise      │ amazing, inspiring, love, great, awesome      │
│ Spam        │ crypto, bitcoin, mlm, forex, dm me, click here│
│ Sales       │ partnership, collaboration, sponsor, work with│
└─────────────┴───────────────────────────────────────────────┘
```

**Priority**: Spam > Sales > Praise > Questions (first match wins)

---

## Auto-Responses

Only sent for:

- **Questions** → "Thanks for the question! Check out our FAQ at [link] or email support@..."
- **Praise** → "Thank you so much! We love the support 💙"

**No auto-response** for spam or sales (flagged for manual review instead)

---

## Logged Data Format

Each processed comment:
```json
{
  "timestamp": "2026-04-19T12:30:45.123456Z",
  "commenter": "John Doe",
  "text": "How do I get started with Concessa?",
  "category": "questions",
  "response_status": "replied",
  "comment_id": "Ugw_abc123xyz..."
}
```

- **One JSON object per line** (JSONL = JSON Lines)
- **Append-only** — safe to read while writing
- **Deduped** — never logs same comment twice

---

## How to Run

### Manual
```bash
python youtube-monitor.py
```

### Scheduled (Cron)
Every 4 hours:
```bash
0 */4 * * * cd ~/.openclaw/workspace && python youtube-monitor.py >> ~/.openclaw/workspace/.cache/youtube-monitor-cron.log 2>&1
```

### As OpenClaw Cron Task
In OpenClaw, schedule it to run periodically and deliver reports to Discord/Telegram.

---

## Customization

### Change Keywords
Edit `KEYWORDS` dict in `youtube-monitor.py`:
```python
KEYWORDS = {
    "questions": ["how", "help", "tools", ...],
    "praise": ["amazing", "inspiring", ...],
    "spam": ["crypto", "bitcoin", ...],
    "sales": ["partnership", "collaboration", ...],
}
```

### Change Response Templates
Edit `RESPONSES` dict:
```python
RESPONSES = {
    "questions": "Your custom response here",
    "praise": "Your custom response here 💙",
}
```

### Monitor Different Channel
Edit `CHANNEL_NAME`:
```python
CHANNEL_NAME = "Your Channel Name"
```

### Fetch More Videos
In `run_monitor()`:
```python
video_ids = get_video_ids(youtube, uploads_playlist_id, max_results=50)
```

---

## Error Handling

| Error | Behavior |
|-------|----------|
| Missing credentials | Logs error, exits gracefully |
| API quota exceeded | Stops processing, reports stats |
| Comments disabled | Skips video, continues |
| Reply failed | Logs error, continues |
| Network error | Logged with context |

---

## Idempotency

The script guarantees:
- ✅ Never processes the same comment twice (tracked by comment_id)
- ✅ Safe to run multiple times concurrently
- ✅ Resumes from last position on restart
- ✅ No duplicate entries in log file

---

## Monitoring & Queries

### View Statistics
```bash
python youtube-monitor-query.py stats
```

### View Unanswered Questions
```bash
python youtube-monitor-query.py unanswered
```

### Filter by Category
```bash
python youtube-monitor-query.py category questions
python youtube-monitor-query.py category sales
```

### Export to JSON
```bash
python youtube-monitor-query.py export > comments.json
```

### Raw JSONL Access
```bash
# Last 20 comments
tail -20 ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Pretty-print
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .

# Filter sales comments
jq 'select(.category == "sales")' ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

---

## Setup Instructions

**Full setup guide**: See `YOUTUBE-MONITOR-SETUP.md`

TL;DR:
1. Create Google Cloud project
2. Enable YouTube Data API v3
3. Create OAuth2 credentials (Desktop or Web)
4. Download `client_secret.json` to `~/.youtube/`
5. Run `python setup-youtube-credentials.py`
6. Run `python youtube-monitor.py`

---

## API Requirements

The script uses `youtube.force-ssl` scope:

✅ Can:
- Read all comments on channel videos
- Reply to comments
- View channel info
- List videos

❌ Cannot:
- Delete comments or replies
- Modify existing comments
- Access private videos

---

## Rate Limits

- YouTube API: 10,000 units/day (default)
- Each comment list call: ~1 unit
- Each reply insertion: ~1 unit
- The script handles quota exceeded gracefully (stops and reports)

---

## Logs

| Log | Location |
|-----|----------|
| Comments data | `~/.openclaw/workspace/.cache/youtube-comments.jsonl` |
| Execution log | `~/.openclaw/workspace/.cache/youtube-monitor.log` |
| State (resume) | `~/.openclaw/workspace/.cache/youtube-monitor-state.json` |
| Cron log | `~/.openclaw/workspace/.cache/youtube-monitor-cron.log` |

---

## Files in This Package

```
youtube-monitor.py                 - Main script
setup-youtube-credentials.py       - OAuth2 setup
youtube-monitor-query.py           - Query & analysis tool
youtube-monitor-requirements.txt   - Python dependencies
YOUTUBE-MONITOR-README.md          - This file
YOUTUBE-MONITOR-SETUP.md           - Detailed setup guide
```

---

## Next Steps

1. **Setup OAuth2** → `python setup-youtube-credentials.py`
2. **Test it** → `python youtube-monitor.py`
3. **Review logs** → `python youtube-monitor-query.py stats`
4. **Schedule it** → Add to crontab or OpenClaw cron
5. **Customize** → Edit keywords/responses to match your channel

---

**Last Updated**: 2026-04-19  
**Version**: 1.0  
**Status**: Production Ready
