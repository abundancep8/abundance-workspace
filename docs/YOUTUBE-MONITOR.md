# YouTube Comment Monitor

Automated monitoring of the Concessa Obvius YouTube channel with intelligent comment categorization, auto-responses, and logging.

## Features

✅ **Auto-categorization**: Questions, Praise, Spam, Sales
✅ **Auto-response**: Templates for questions and praise
✅ **Review queue**: Sales inquiries flagged for manual review  
✅ **Complete logging**: All comments + metadata to JSONL
✅ **Stats tracking**: Running totals of comments, responses, flags
✅ **30-min polling**: Efficient monitoring via cron

## Architecture

```
youtube-monitor.py          Main script
  ├─ Authenticate          OAuth2 with YouTube API
  ├─ Fetch recent videos   From channel uploads
  ├─ Get comments          On each video (newest first)
  ├─ Categorize           ML-free keyword matching
  ├─ Auto-respond         Only if we haven't already
  ├─ Log to JSONL         All comments + metadata
  └─ Report stats         New counts + cumulative

Config: .config/youtube-monitor.json
  - channel_id (cached)
  - last_comment_id (pagination)
  - stats (totals)

Token: .secrets/youtube-token.json
  - OAuth2 refresh token (auto-managed)

Log: .cache/youtube-comments.jsonl
  - timestamp, comment_id, video_id, commenter, text, category, response_status
```

## Setup (One-Time)

### 1. Get YouTube API Credentials

```bash
# Go to https://console.cloud.google.com/
# 1. Create new project (or use existing)
# 2. Enable YouTube Data API v3
# 3. Credentials → Create → OAuth 2.0 Client ID (Desktop app)
# 4. Download JSON
# 5. Save to: .secrets/youtube-credentials.json
```

### 2. Run Setup Script

```bash
chmod +x scripts/youtube-monitor-setup.sh
./scripts/youtube-monitor-setup.sh
```

This will:
- Check for credentials file
- Install Python dependencies
- Run initial authentication (browser login)
- Create config file
- Show cron instructions

### 3. Set Up Cron Job

```bash
crontab -e

# Add this line (runs every 30 minutes):
*/30 * * * * /usr/bin/python3 /Users/abundance/.openclaw/workspace/scripts/youtube-monitor.py >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log 2>&1
```

Verify it's scheduled:
```bash
crontab -l | grep youtube-monitor
```

## Usage

### Manual Run
```bash
python3 scripts/youtube-monitor.py
```

### View Logs
```bash
# Real-time stream
tail -f .cache/youtube-comments.jsonl

# Pretty-print latest 10 comments
tail -10 .cache/youtube-comments.jsonl | jq .

# Filter by category
grep '"category": "question"' .cache/youtube-comments.jsonl

# Count by category
grep '"category":' .cache/youtube-comments.jsonl | jq -r '.category' | sort | uniq -c

# Find flagged comments
grep '"response_status": "flagged_review"' .cache/youtube-comments.jsonl | jq .
```

### Check Cron Activity
```bash
log stream --predicate 'process == "cron"' --level debug

# Or check output log
tail -50 .cache/youtube-monitor.log
```

## Comment Categories

### 1. **Question** — Auto-respond
Keywords: how, what, where, when, why, cost, price, timeline, tools, start, help, tutorial

Template:
```
Thanks for the question! Here's how you can get started:
1. Check our getting started guide (link in bio)
2. Watch our intro video
3. Join our community Discord for live support

Feel free to reply with more questions!
```

### 2. **Praise** — Auto-respond
Keywords: amazing, inspiring, incredible, love, awesome, great, excellent, wonderful, thanks, appreciate

Template:
```
Thank you so much for the kind words! 🙏 This means a lot to us and motivates us to keep creating.
Feel free to reach out anytime — we love hearing from our community!
```

### 3. **Spam** — Skip (not logged as actionable)
Keywords: crypto, bitcoin, ethereum, mlm, get rich, guaranteed, click here

### 4. **Sales** — Flag for Review
Keywords: partnership, collaboration, sponsor, advertise, work with us

No auto-response. Logged with `response_status: "flagged_review"` for manual handling.

### 5. **Other** — No action
Everything else. Logged as-is.

## Configuration

Edit `.config/youtube-monitor.json`:

```json
{
  "channel_id": "UCxxxxxx...",
  "last_comment_id": "xxxxxxxx...",
  "stats": {
    "total": 42,
    "auto_responded": 15,
    "flagged": 3
  }
}
```

- **channel_id**: Cached after first run. Override to switch channels.
- **last_comment_id**: Pagination marker. Delete to re-process all comments.
- **stats**: Cumulative totals (updated after each run).

## JSONL Log Format

One JSON object per line:

```json
{
  "timestamp": "2026-04-19T04:00:00.123456",
  "comment_id": "Uxxxxxxxx...",
  "video_id": "dQw4w9WgXcQ",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "question",
  "response_status": "sent_question"
}
```

**response_status** values:
- `"pending"` — Logged but not actioned (category = other)
- `"sent_question"` — Auto-response sent (question)
- `"sent_praise"` — Auto-response sent (praise)
- `"flagged_review"` — Sales inquiry, needs manual review
- `"already_responded"` — We already replied to this thread

## Troubleshooting

### OAuth Token Expired
Token auto-refreshes. If you see auth errors, delete `.secrets/youtube-token.json` and run:
```bash
python3 scripts/youtube-monitor.py
```
It will re-authenticate.

### API Rate Limit
YouTube API quota: 10,000 units/day. Each comment read = 1 unit, each reply = ~200 units.
- 30-min interval with ~50 videos = ~5,000 units/day (safe)
- If hitting limits, increase interval to 60+ minutes

### No Comments Found
- Verify channel ID in `.config/youtube-monitor.json`
- Make sure channel has videos with comments enabled
- Check cron log: `tail .cache/youtube-monitor.log`

### Responses Not Sending
- Verify OAuth credentials have YouTube write scope (already in setup)
- Check video/comment still exists (old comments deleted)
- Check for duplicate responses (script prevents this)

## Advanced Customization

### Modify Response Templates
Edit `RESPONSE_TEMPLATES` dict in `youtube-monitor.py`:

```python
RESPONSE_TEMPLATES = {
    "question": "Your custom question response...",
    "praise": "Your custom praise response..."
}
```

### Add Custom Categories
Edit `CATEGORY_KEYWORDS`:

```python
CATEGORY_KEYWORDS = {
    "custom_topic": [
        r"\bkeyword1\b",
        r"\bkeyword2\b"
    ]
}
```

### Change Monitoring Frequency
In crontab, change `*/30` to desired minutes:
```bash
# Every 15 minutes
*/15 * * * * /usr/bin/python3 ...

# Every hour
0 * * * * /usr/bin/python3 ...

# Daily at 9 AM
0 9 * * * /usr/bin/python3 ...
```

## Stats & Reporting

After each run, the script prints:

```
============================================================
REPORT
============================================================
Timestamp: 2026-04-19T04:00:00.123456
New comments processed: 7
Auto-responses sent: 3
Flagged for review: 1

Cumulative stats:
  Total comments: 42
  Auto-responses: 15
  Flagged: 3
  Log file: /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl
============================================================
```

Query cumulative stats:
```bash
cat .config/youtube-monitor.json | jq .stats
```

## Security Notes

- ⚠️ **Credentials file** (`.secrets/youtube-credentials.json`) — Never commit or share
- ⚠️ **Token file** (`.secrets/youtube-token.json`) — Auto-generated, treat as secret
- ✅ `.cache/youtube-comments.jsonl` — Safe to share (public comment text only)
- ✅ `.config/youtube-monitor.json` — Safe to share (no secrets)

## Maintenance

### Weekly
- Check flagged comments: `grep "flagged_review" .cache/youtube-comments.jsonl | jq .`
- Review stats: `cat .config/youtube-monitor.json`

### Monthly
- Archive log: `cp .cache/youtube-comments.jsonl .cache/youtube-comments-2026-04.jsonl`
- Reset if needed: `rm .cache/youtube-comments.jsonl` (keeps config)

## Integration with OpenClaw

This monitor runs as a cron job. To integrate with OpenClaw alerts:

Edit `.cache/youtube-monitor.log` to capture flagged comments and pipe to OpenClaw message tool:

```bash
# In the monitor script, after logging flagged comment:
openai-message send --channel discord "🚩 Flagged: [commenter] - [text]"
```

Or use OpenClaw's native cron + message integration for reporting.

---

**Ready to go!** Run `./scripts/youtube-monitor-setup.sh` to start. 🚀
