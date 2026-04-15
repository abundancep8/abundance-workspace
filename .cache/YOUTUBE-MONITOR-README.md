# 🎬 YouTube Comment Monitor — Complete Setup

**Cron Job:** Monitor Concessa Obvius YouTube channel for new comments every 30 minutes.

## What I Built ✅

### Core Components

1. **`youtube-monitor.py`** (13.6 KB)
   - Fetches recent comments from Concessa Obvius channel
   - Categorizes comments into: Question / Praise / Spam / Sales
   - Auto-replies to Questions & Praise with template responses
   - Flags Sales/Partnership inquiries for manual review
   - Logs all activity to `.cache/youtube-comments.jsonl` with full metadata
   - Generates summary report on each run

2. **`YOUTUBE-SETUP.md`** (5 KB)
   - Complete configuration guide
   - 3 authentication options (API Key, Service Account, OAuth2)
   - Cron setup instructions
   - Troubleshooting guide
   - Usage examples for querying logs

3. **`youtube-monitor-cron.sh`** (Wrapper)
   - Runs the monitor and logs output
   - Appends timestamped results to `youtube-monitor.log`

## Quick Start

### 1️⃣ Set up YouTube API Access (Choose One)

**Option A: API Key (Recommended for testing)**
```bash
export YOUTUBE_API_KEY="your-api-key-here"
```

**Option B: Service Account (Full access)**
```bash
# Download from Google Cloud Console, save to:
~/.config/youtube-credentials.json
```

See `YOUTUBE-SETUP.md` for detailed steps.

### 2️⃣ Test the Monitor

```bash
cd ~/.openclaw/workspace/.cache
python3 youtube-monitor.py
```

Expected output:
```
🎬 YouTube Comment Monitor started...
📝 Found 5 new comments
✓ Auto-replied to User1 (question)
✓ Auto-replied to User2 (praise)
🚩 Flagged for review: User3 (sales inquiry)
📌 Logged: User4 (other)

============================================================
📊 YOUTUBE COMMENT MONITOR REPORT
============================================================
Total comments processed: 4
New comments this cycle: 4
Auto-responses sent: 2
Flagged for review: 1
============================================================
```

### 3️⃣ Set up Cron Job (Every 30 Minutes)

**Via OpenClaw:**
```bash
openclaw cron --label youtube-monitor \
  --interval 30m \
  --task "cd ~/.openclaw/workspace && python3 .cache/youtube-monitor.py"
```

**Via native crontab:**
```bash
crontab -e
# Add this line:
*/30 * * * * /bin/bash ~/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

## How It Works

### Comment Categorization

| Category | Keywords | Action |
|----------|----------|--------|
| **Question** | "how to", "cost", "tools", "timeline", "where", "help" | Auto-reply with guidance |
| **Praise** | "amazing", "inspiring", "love", "thanks", "excellent" | Auto-reply with gratitude |
| **Spam** | "crypto", "bitcoin", "mlm", "passive income", "click here" | Skip (not logged) |
| **Sales** | "partnership", "collaboration", "sponsor", "brand deal" | Flag for manual review |
| **Other** | Everything else | Log without action |

### Auto-Response Templates

Questions get:
```
Thanks so much for the question! 🎯 {name}

I'd be happy to help! Please check out our full resources 
or DM for personalized guidance.

Feel free to reach out if you need more details!
```

Praise gets:
```
Thank you so much, {name}! 🙏 Your support means everything.

Your kind words fuel our mission!
```

(Edit templates in `youtube-monitor.py` lines 94-100)

## Logging & Reporting

### Log File: `youtube-comments.jsonl`

Each comment stored as JSON, one per line:

```json
{
  "timestamp": "2026-04-15T06:30:15.123456",
  "comment_id": "Zx_K8j9...",
  "video_id": "dQw4w9...",
  "commenter": "Alice Smith",
  "text": "How do I get started?",
  "category": "question",
  "response_status": "auto_replied",
  "response_text": "Thanks so much for the question! Alice..."
}
```

### Useful Queries

**See all comments:**
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .
```

**Comments needing review:**
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | \
  jq 'select(.response_status=="flagged_for_review")'
```

**Count by category:**
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | \
  jq -r '.category' | sort | uniq -c
```

**Today's activity:**
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | \
  jq "select(.timestamp | startswith(\"$(date '+%Y-%m-%d')\"))"
```

### Monitor Log: `youtube-monitor.log`

Full stdout/stderr with timestamps from each cron run:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Run: 2026-04-15 06:30:15 PDT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 YouTube Comment Monitor started at 2026-04-15T06:30:15...
✓ Auto-replied to User (question)
...
```

## Configuration

### Change Channel
Edit line in `youtube-monitor.py`:
```python
CHANNEL_ID = "UCjJb8TxwgXHNL5e-4PGh_IA"  # Concessa Obvius
```

### Adjust Lookback Window
Currently 35 minutes (slightly longer than 30-min cron interval). Edit:
```python
LOOKBACK_MINUTES = 35
```

### Customize Response Templates
Edit `TEMPLATES` dict in `youtube-monitor.py` (lines 94-105).

## Stats Tracked

Per run report includes:
- ✅ **Total comments processed** — All comments found this cycle
- ✅ **New comments** — Comments since last run
- ✅ **Auto-responses sent** — Replies to Questions & Praise
- ✅ **Flagged for review** — Sales/partnership inquiries requiring manual attention

## Troubleshooting

**"No API credentials configured"**
→ Set `YOUTUBE_API_KEY` env var or create `~/.config/youtube-credentials.json`

**"Failed to authenticate"**
→ Check API key is valid & YouTube Data API is enabled in Google Cloud Console

**"No new comments found"**
→ Comments may be outside 35-minute lookback window. Check channel has recent activity.

**Replies not posting**
→ API key allows read-only. Use service account or OAuth2 for write access. For now, responses are logged and flagged.

## Next Steps

- [ ] Set up YouTube API credentials (see `YOUTUBE-SETUP.md`)
- [ ] Test manually: `python3 ~/.openclaw/workspace/.cache/youtube-monitor.py`
- [ ] Set up cron job (every 30 minutes)
- [ ] Customize response templates
- [ ] Monitor logs regularly: `tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log`

## Files

```
~/.openclaw/workspace/.cache/
├── youtube-monitor.py           # Main script
├── youtube-monitor-cron.sh      # Cron wrapper
├── youtube-comments.jsonl       # Comment log (auto-created)
├── youtube-monitor.log          # Execution log (auto-created)
├── YOUTUBE-SETUP.md             # Setup guide
└── YOUTUBE-MONITOR-README.md    # This file
```

---

**Status:** ✅ Ready to configure & deploy
**Last Updated:** 2026-04-15 06:30 UTC
