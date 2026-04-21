# 🎬 YouTube Comment Monitor

Automated monitoring and response system for YouTube channels. Monitors the "Concessa Obvius" channel every 30 minutes, categorizes comments, auto-responds intelligently, and flags potential partnerships for review.

## ⚡ Quick Start (5 minutes)

### 1. Get Your API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **YouTube Data API v3**
4. Go to **Credentials** → **Create** → **API Key**
5. Copy the key

### 2. Test the Monitor

```bash
cd /Users/abundance/.openclaw/workspace

# Run once to test (no API key = dry run)
python3 .cache/youtube-monitor.py

# With API key (will actually monitor)
YOUTUBE_API_KEY="your-key" python3 .cache/youtube-monitor.py
```

### 3. Set Up Cron (30-minute intervals)

```bash
# Add to crontab
crontab -e

# Paste this line:
*/30 * * * * cd /Users/abundance/.openclaw/workspace && YOUTUBE_API_KEY="your-key" python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1
```

### 4. Monitor Progress

```bash
# View recent comments
tail -f .cache/youtube-monitor.log

# See all logged comments
cat .cache/youtube-comments.jsonl | jq .

# See comments flagged for review
cat .cache/youtube-comments.jsonl | jq 'select(.category == "sales")'
```

---

## 📁 Files in This System

| File | Purpose |
|------|---------|
| `youtube-monitor.py` | Main monitoring script (Python 3) |
| `youtube-monitor.sh` | Shell wrapper for cron/OpenClaw |
| `youtube-monitor-state.json` | Tracks processed comments (deduplication) |
| `youtube-comments.jsonl` | Append-only log of all comments |
| `youtube-monitor.log` | Cron execution logs |
| `youtube-comments.example.jsonl` | Example output (see below) |
| `YOUTUBE_SETUP.md` | Detailed setup guide |
| `CRON_SETUP.md` | OpenClaw & system cron integration |
| `README-YOUTUBE-MONITOR.md` | This file |

---

## 🤖 How It Works

### Comment Categories

**1. Questions** (Auto-respond)
- Patterns: "how", "what", "tools", "cost", "timeline", "start", etc.
- Action: Auto-responds with contextual answer
- Example: "How do I get started?" → Gets response with getting started guide

**2. Praise** (Auto-respond)
- Patterns: "amazing", "love", "inspiring", "great", "thanks", etc.
- Action: Auto-responds with thank you
- Example: "This is amazing!" → Gets thank you response

**3. Spam** (Ignore)
- Patterns: "crypto", "bitcoin", "mlm", "affiliate", etc.
- Action: Logged but no response
- Example: "Get free Bitcoin!" → Logged as spam, ignored

**4. Sales** (Flag for Review)
- Patterns: "partnership", "collaboration", "sponsor", etc.
- Action: Logged and flagged as "pending review"
- Example: "Want to partner?" → Logged with response_status="flagged"

### Processing Pipeline

```
Fetch new comments from YouTube
    ↓
Check if already processed (deduplication)
    ↓
Categorize using regex patterns
    ↓
Decide on response (Q/P get responses, Sales get flagged, Spam ignored)
    ↓
Post response to YouTube (if auto-respond)
    ↓
Log to youtube-comments.jsonl with status
    ↓
Update processed IDs in state file
    ↓
Output report (count, stats)
```

---

## 📊 Data Format

### Input: YouTube Comments

Each comment is fetched with:
- Commenter name
- Comment text
- Video ID
- Comment ID
- Timestamp

### Output: youtube-comments.jsonl (JSONL format)

Each line is a JSON object:

```json
{
  "timestamp": "2026-04-21T07:00:15Z",
  "commenter": "Sarah Chen",
  "text": "How do I get started with your platform?",
  "category": "question",
  "response": "Thanks for the great question! Check out our getting started guide...",
  "response_status": "sent",
  "video_id": "dQw4w9WgXcQ",
  "comment_id": "Ugw1a2b3c4d5"
}
```

**Fields:**
- `timestamp` — ISO 8601 timestamp of comment
- `commenter` — Display name of YouTube user
- `text` — Comment text (plaintext)
- `category` — One of: question, praise, spam, sales, other
- `response` — The auto-response text (null if none)
- `response_status` — One of:
  - `"none"` — No response (spam/other)
  - `"sent"` — Response posted successfully
  - `"failed"` — Response attempted but failed
  - `"flagged"` — Marked for manual review
- `video_id` — YouTube video ID where comment appeared
- `comment_id` — YouTube comment ID (unique)

### State File: youtube-monitor-state.json

```json
{
  "last_checked": "2026-04-21T07:30:00.000000",
  "processed_ids": [
    "Ugw1a2b3c4d5",
    "Ugw2e3f4g5h6",
    "Ugw3i4j5k6l7"
  ]
}
```

The `processed_ids` list prevents processing the same comment twice (deduplication).

---

## 🔧 Configuration

### Change the Channel

Edit line 35 in `youtube-monitor.py`:

```python
CHANNEL_NAME = "Concessa Obvius"  # Change this
```

Or set via env var:

```bash
YOUTUBE_CHANNEL_ID="UCxxxxxxxxx" python3 .cache/youtube-monitor.py
```

### Customize Auto-Responses

Edit the `RESPONSE_TEMPLATES` dict in `youtube-monitor.py`:

```python
RESPONSE_TEMPLATES = {
    "question": "Thanks for asking! {answer} Let us know if you need more.",
    "praise": "Thanks so much! Really appreciate it!",
}
```

And customize the `generate_response()` method for per-question-type responses:

```python
def generate_response(self, category: str, comment: str) -> Optional[str]:
    if category == "question":
        if "pricing" in comment.lower():
            return "Our pricing starts at $29. See www.example.com/pricing"
        elif "tutorial" in comment.lower():
            return "Check our tutorial playlist: [link]"
    return None
```

### Add New Categories

Add regex patterns in the `categorize_comment()` method:

```python
# Your new category
your_patterns = [r"\byour_word\b", r"\banother_word\b"]
if any(re.search(pattern, text_lower) for pattern in your_patterns):
    return "your_category"
```

---

## 📈 Monitoring & Reports

### View Report Output

After each run, see:

```
============================================================
📊 REPORT
============================================================
Processed: 6
Auto-responses sent: 4
Flagged for review: 1
Log file: .cache/youtube-comments.jsonl
============================================================
```

### Query Examples

**All comments from last 24 hours:**
```bash
CUTOFF=$(date -u -d "24 hours ago" +%Y-%m-%dT%H:%M:%S)
cat .cache/youtube-comments.jsonl | jq --arg cutoff "$CUTOFF" 'select(.timestamp > $cutoff)'
```

**Questions that auto-responded:**
```bash
cat .cache/youtube-comments.jsonl | jq 'select(.category == "question" and .response_status == "sent")'
```

**Sales to review:**
```bash
cat .cache/youtube-comments.jsonl | jq 'select(.response_status == "flagged")'
```

**Failed responses:**
```bash
cat .cache/youtube-comments.jsonl | jq 'select(.response_status == "failed")'
```

**Count by category:**
```bash
cat .cache/youtube-comments.jsonl | jq -s 'group_by(.category) | map({category: .[0].category, count: length})'
```

---

## 🐛 Troubleshooting

### "YOUTUBE_API_KEY env var not set"

Set your API key:

```bash
export YOUTUBE_API_KEY="your-key"
python3 .cache/youtube-monitor.py
```

### "Could not find channel: Concessa Obvius"

The monitor can't auto-lookup the channel. Provide the channel ID directly:

```bash
YOUTUBE_CHANNEL_ID="UCxxxxxxxxx" python3 .cache/youtube-monitor.py
```

Find channel ID: Visit YouTube → Go to channel → Settings → Copy channel ID from URL.

### "Failed to post response"

The API couldn't post your response. Reasons:
- API key doesn't have write permissions (use a service account)
- Video has comments disabled
- Rate limits hit (wait and retry)

The script logs as "failed" and continues. Check logs.

### Cron not running

Check crontab:

```bash
crontab -l
```

Check logs:

```bash
tail -f .cache/youtube-monitor.log
```

Check cron system logs:

```bash
log stream --predicate 'process == "cron"' --level debug
```

---

## 🚀 Advanced Usage

### Run with Different API Types

**API Key (simple, read-only):**
```bash
YOUTUBE_API_KEY="key" python3 .cache/youtube-monitor.py
```

**Service Account (full access with write permissions):**
```bash
GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json" python3 .cache/youtube-monitor.py
```

### Batch Process Historical Comments

Edit the script to fetch more than recent 5 videos:

```python
# Line ~180
maxResults=20,  # Changed from 5
```

Then run once to backfill the log.

### Export Data

**To CSV:**
```bash
cat .cache/youtube-comments.jsonl | jq -r '[.timestamp, .commenter, .category] | @csv' > comments.csv
```

**To SQL (SQLite):**
```bash
cat .cache/youtube-comments.jsonl | jq -r '[.timestamp, .commenter, .text, .category] | @csv' | \
  sqlite3 :memory: ".mode csv" ".import /dev/stdin comments" "SELECT * FROM comments LIMIT 10;"
```

### Schedule Report Email

Wrap the monitor and pipe output to email:

```bash
(cron output) | mail -s "YouTube Monitor Report" you@example.com
```

---

## 📚 Documentation

- **`YOUTUBE_SETUP.md`** — Complete setup guide (API keys, auth, testing)
- **`CRON_SETUP.md`** — Cron scheduling (system cron, OpenClaw cron, env vars)
- **`youtube-monitor.py`** — Full source code with comments

---

## 🎯 What's Next?

1. ✅ Get YouTube API key (see YOUTUBE_SETUP.md)
2. ✅ Test the monitor manually
3. ✅ Set up cron (see CRON_SETUP.md)
4. ✅ Review flagged comments daily
5. ✅ Customize responses as needed
6. ✅ Monitor performance metrics

---

## 📋 Checklist

- [ ] YouTube API key obtained and tested
- [ ] `youtube-monitor.py` runs successfully
- [ ] Cron job registered (30-minute schedule)
- [ ] Logs viewable and readable
- [ ] Example data in `.cache/youtube-comments.example.jsonl`
- [ ] Response templates customized for your channel
- [ ] Daily review process for flagged comments established

---

## 💡 Tips

1. **Start conservative.** Set cron to hourly at first, then dial to 30 min once stable.
2. **Monitor API quota.** Check Google Cloud Console to watch your usage.
3. **Archive old data.** Keep last 30 days in the active log, archive older to separate files.
4. **Test responses.** Review auto-responses for the first week to tune templates.
5. **Scale responses.** If you get hundreds of questions, consider ML categorization.

---

## 📞 Support

- YouTube API docs: https://developers.google.com/youtube/v3
- Google Cloud help: https://cloud.google.com/docs
- Local docs: See `.cache/YOUTUBE_SETUP.md` and `.cache/CRON_SETUP.md`

---

**Happy monitoring! 🚀**
