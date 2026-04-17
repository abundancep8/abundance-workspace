# 🎬 YouTube Comment Monitor

Automated comment categorization, auto-response, and review flagging for the Concessa Obvius YouTube channel.

## What It Does

Monitors your YouTube channel every 30 minutes and:

1. **Fetches comments** from recent videos
2. **Categorizes** each comment:
   - `question` → How do I start? What tools? What costs?
   - `praise` → Inspiring, amazing, love this
   - `spam` → Crypto, MLM, get rich quick
   - `sales` → Partnerships, collaborations, business proposals
   - `other` → Doesn't fit any category

3. **Auto-responds** to questions & praise with templates
4. **Flags sales inquiries** for manual review
5. **Hides spam** automatically
6. **Logs everything** to `.cache/youtube-comments.jsonl` for analysis

## Files

- **`youtube-monitor.py`** — Main monitoring script
- **`youtube-monitor.sh`** — Easy runner (edit to add credentials)
- **`youtube-monitor-setup.md`** — Detailed setup guide
- **`youtube-report.py`** — Generate reports from logs
- **`youtube-comments.jsonl`** — Log of all processed comments (one JSON per line)
- **`youtube-state.json`** — Internal state tracking

## Quick Start

### 1. Get Your Credentials

**YouTube API Key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create/select a project
3. Enable "YouTube Data API v3"
4. Create an API Key in Credentials
5. Copy the key

**Channel ID:**
- Go to your channel
- The ID starts with `UC...` (find it in the channel URL or settings)

### 2. Configure the Monitor

Edit `.cache/youtube-monitor.sh`:

```bash
YOUTUBE_API_KEY="YOUR_API_KEY_HERE"
YOUTUBE_CHANNEL_ID="UCxxxxxxxxxx"
```

### 3. Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 4. Test It

```bash
bash .cache/youtube-monitor.sh
```

You should see:
```
=== YouTube Comment Monitor Report ===
Run time: 2026-04-17 02:02:30 PDT
Total comments processed: 4
Auto-responses sent: 2
Flagged for review (sales): 1

Breakdown by category:
  question: 1
  praise: 1
  spam: 1
  sales: 1
  other: 0

Cumulative processed: 4
Log file: /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl
```

### 5. View Reports

```bash
# Full report
python3 .cache/youtube-report.py

# View logged comments (as JSON)
cat .cache/youtube-comments.jsonl | python3 -m json.tool

# Filter for flagged sales comments
cat .cache/youtube-comments.jsonl | jq 'select(.response_status=="flagged_review")'

# Filter for questions
cat .cache/youtube-comments.jsonl | jq 'select(.category=="question")'
```

## Cron Setup (Auto-Run Every 30 Minutes)

### Option A: Using OpenClaw Cron

```bash
# OpenClaw will handle the scheduling and environment
# The cron ID is: 114e5c6d-ac8b-47ca-a695-79ac31b5c076
```

### Option B: Manual Crontab

```bash
# Edit crontab
crontab -e

# Add this line (runs every 30 minutes):
*/30 * * * * cd /Users/abundance/.openclaw/workspace && bash .cache/youtube-monitor.sh >> .cache/youtube-monitor.log 2>&1
```

### Verify Cron is Running

```bash
# Watch the log in real-time
tail -f .cache/youtube-monitor.log

# Check the latest entries
tail -30 .cache/youtube-monitor.log
```

## Customize Responses

Edit `.cache/youtube-monitor.py`, find this section:

```python
TEMPLATES = {
    "question": "Thank you for the great question! I appreciate your interest. I'll look into this and get back to you soon. 🙏",
    "praise": "Thank you so much for the kind words! Your support means everything. 💜"
}
```

Change the responses to match your voice.

## Fine-Tune Categorization

Edit the `CATEGORIES` dict in `.cache/youtube-monitor.py` to add/remove keywords:

```python
CATEGORIES = {
    "question": [
        r"how\s+do\s+i", r"how\s+to", r"what.*cost", r"how.*much",
        # Add more patterns here
    ],
    "praise": [
        r"amazing", r"inspiring", r"love\s+this",
        # Add more patterns
    ],
    ...
}
```

Patterns are **regex** (Python flavored). Test with:

```bash
python3 -c "
import re
text = 'Your comment here'
pattern = r'how\s+do\s+i'
if re.search(pattern, text.lower()):
    print('MATCH')
"
```

## Output Format (JSONL)

Each line is a valid JSON object:

```json
{
  "timestamp": "2026-04-17T09:02:00Z",
  "comment_id": "UgyPH7zV3z7k_HQgqh94AaABCQ",
  "video_id": "dQw4w9WgXcQ",
  "commenter": "Alex Chen",
  "text": "How do I get started with this?",
  "category": "question",
  "response_status": "auto_responded",
  "auto_response": "Thank you for the great question!...",
  "likes": 3
}
```

### Response Statuses

- `auto_responded` — Comment received an auto-response (questions & praise)
- `flagged_review` — Marked for manual review (sales inquiries)
- `spam_hidden` — Automatically hidden (spam)
- `pending` — No action taken

## Advanced: Analyze Comments

```bash
# Count by category
cat .cache/youtube-comments.jsonl | python3 -c "
import json, sys
from collections import Counter
data = [json.loads(line) for line in sys.stdin]
cats = Counter(c['category'] for c in data)
for cat, count in cats.most_common():
    print(f'{cat}: {count}')
"

# Find unanswered questions (if you're manually responding)
cat .cache/youtube-comments.jsonl | jq 'select(.category=="question" and .response_status=="pending")'

# Export to CSV
cat .cache/youtube-comments.jsonl | python3 -c "
import json, sys, csv
data = [json.loads(line) for line in sys.stdin]
writer = csv.DictWriter(sys.stdout, fieldnames=data[0].keys())
writer.writeheader()
writer.writerows(data)
" > comments.csv
```

## Troubleshooting

### Script won't run
```
ERROR: Google API client not installed.
```
Run: `pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client`

### API key error
```
ERROR: YOUTUBE_API_KEY env var not set
```
Edit `youtube-monitor.sh` and add your API key (or set env var before running)

### No comments found
- Channel ID might be wrong (check with `youtube.com/@yourname`)
- API key might not have YouTube Data API enabled
- Channel might have comments disabled
- Limit of requests exceeded (YouTube has rate limits)

### Check API Limits
YouTube API has quotas. Each request costs quota points:
- Fetching comments: 1 point per request
- Daily limit: 10,000 points (by default)

Running every 30 minutes ≈ 48 requests/day = ~48 quota points. You're well within limits.

## Next Steps

1. ✅ Get API credentials
2. ✅ Edit `youtube-monitor.sh` with your credentials
3. ✅ Run `bash .cache/youtube-monitor.sh` to test
4. ✅ Set up cron job
5. ✅ Customize response templates
6. ✅ Tune categorization as comments come in
7. ✅ Check reports regularly with `python3 .cache/youtube-report.py`

---

**Need help?** Check `.cache/youtube-monitor-setup.md` for detailed instructions.
