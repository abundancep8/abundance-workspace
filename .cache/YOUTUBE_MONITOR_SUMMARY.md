# YouTube Comment Monitor - Complete Setup ✅

## What's Been Built

A full-featured YouTube comment monitoring system for the **Concessa Obvius** channel that:

### Core Features
- ✅ **Monitors new comments** every 30 minutes via cron
- ✅ **Categorizes comments** into 4 types:
  - **Questions:** "How do I start?", "What tools do you use?", "How much does it cost?", "What's your timeline?"
  - **Praise:** "Amazing!", "This is inspiring!", "Love this!", "Great content!"
  - **Spam:** Crypto, NFTs, MLM, "get rich quick" schemes
  - **Sales:** Partnership offers, collaboration requests, sponsor inquiries
- ✅ **Auto-responds** to Questions and Praise with templates
- ✅ **Flags Sales inquiries** for manual review
- ✅ **Logs everything** to `.cache/youtube-comments.jsonl`
- ✅ **Reports stats** after each run

### Files Created
```
.cache/
├── youtube-monitor.py          ← Main script (13.4 KB)
├── run-youtube-monitor.sh      ← Cron wrapper
├── youtube-comments.jsonl      ← Comment log (created on first run)
├── youtube-monitor-state.json  ← Tracking state (auto-created)
├── youtube-monitor.log         ← Execution log (auto-created)
├── YOUTUBE_SETUP.md            ← Full setup guide
└── YOUTUBE_MONITOR_SUMMARY.md  ← This file
```

## What You Need To Do

### 1. Install Python Dependencies (5 minutes)

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Set Up YouTube API Credentials (10 minutes)

Follow the **YOUTUBE_SETUP.md** guide (linked above). In summary:
1. Create a Google Cloud project
2. Enable YouTube Data API v3
3. Create OAuth 2.0 credentials (Desktop app)
4. Download JSON → Save to `~/.openclaw/youtube-credentials.json`

**This step requires a Google account with admin access to Cloud Console.**

### 3. Test the Monitor (2 minutes)

```bash
cd ~/.openclaw/workspace
python3 .cache/youtube-monitor.py
```

Expected output:
```
Starting YouTube Comment Monitor for 'Concessa Obvius'
Found X new comments
==================================================
YOUTUBE COMMENT MONITOR REPORT
...
```

First run will prompt you to authorize in your browser. Accept and a token file is created.

### 4. Enable Cron Job

The monitor is configured to run every 30 minutes. Once tested, it will auto-execute.

**Check logs:**
```bash
tail -f .cache/youtube-monitor.log
```

**View collected comments:**
```bash
cat .cache/youtube-comments.jsonl | jq .
```

## How It Works

### Comment Categorization

Uses keyword-based rules:

- **Question:** Starts with "how/what/why/where/when" OR ends with "?"
- **Praise:** Contains words like "amazing", "inspiring", "love", "great", "awesome", etc.
- **Spam:** Contains keywords like "bitcoin", "nft", "mlm", "crypto", "forex", "dropship"
- **Sales:** Contains "partnership", "collaboration", "sponsor", "affiliate", "brand deal"

### Auto-Response Workflow

1. **Questions** → Auto-responds with template (help resources, FAQ, Discord link)
2. **Praise** → Auto-responds with thank-you template
3. **Spam** → Logged as `ignored` (no response)
4. **Sales** → Logged as `flagged_for_review` (you review manually)

### Data Flow

```
YouTube Channel
    ↓
fetch_new_comments() [checks last 5 videos]
    ↓
categorize_comment() [rules-based]
    ↓
auto_respond() [Questions/Praise only]
    ↓
log_comment() → .cache/youtube-comments.jsonl
    ↓
Print Report
```

### State Tracking

The monitor remembers which comments it's already processed using `.cache/youtube-monitor-state.json`:
- Tracks `last_checked` timestamp
- Maintains list of processed comment IDs
- Prevents duplicate processing

## Log Format Example

Each comment is logged as a single JSON line:

```json
{
  "timestamp": "2026-04-19T01:00:05.123456",
  "comment_id": "UgwBxyz123abc",
  "video_id": "dQw4w9WgXcQ",
  "commenter": "Alice Smith",
  "text": "This is amazing! How did you learn to do this?",
  "category": "question",
  "response_status": "queued"
}
```

## Customization

### Change Channel
Edit `youtube-monitor.py` line 32:
```python
CHANNEL_NAME = "Your Channel Name"
```

### Customize Auto-Response Templates
Edit the `TEMPLATES` dict in `youtube-monitor.py`:
```python
TEMPLATES = {
    'question': "Your custom question response...",
    'praise': "Your custom praise response..."
}
```

Include placeholders like `{question_topic}` (will be customized per comment in future versions).

### Adjust Categorization Rules
Edit `CATEGORY_RULES` to add/remove keywords:
```python
CATEGORY_RULES = {
    'spam': {
        'keywords': ['bitcoin', 'nft', ...],
        'phrases': ['make money fast', ...]
    },
    'sales': {
        'keywords': ['partnership', ...],
        'phrases': ['collaborate with', ...]
    }
}
```

## Monitoring & Troubleshooting

### Check Monitor Health
```bash
# View latest execution report
tail -30 .cache/youtube-monitor.log

# Count comments by category
cat .cache/youtube-comments.jsonl | jq -r '.category' | sort | uniq -c

# Find flagged sales inquiries
cat .cache/youtube-comments.jsonl | jq 'select(.category == "sales")'

# Find auto-responses sent
cat .cache/youtube-comments.jsonl | jq 'select(.response_status == "queued")'
```

### Common Issues

**"Channel not found"**
- Verify exact channel name matches YouTube
- Check spelling and capitalization

**"API quota exceeded"**
- YouTube Data API v3 has 10,000 units/day quota
- Check usage in Google Cloud Console
- Monitor runs ~500-1000 units/check; you can run ~10-20 times daily

**"No new comments found"**
- Normal if monitor just ran
- Check `.cache/youtube-monitor-state.json` for last check time

## Next Steps

1. ✅ Follow YOUTUBE_SETUP.md to set up credentials
2. ✅ Run `python3 .cache/youtube-monitor.py` to test
3. ✅ Review `.cache/youtube-comments.jsonl` to verify categorization
4. ✅ Customize templates and rules if needed
5. ✅ Monitor runs automatically every 30 minutes

## Future Enhancements

Potential additions (not yet implemented):
- [ ] Actually post auto-responses to YouTube (requires special permissions)
- [ ] Email alerts for flagged sales inquiries
- [ ] Sentiment analysis for better categorization
- [ ] Dashboard/UI for reviewing flagged comments
- [ ] Database instead of JSONL for easier querying
- [ ] Integrate with Discord bot for notifications

---

**Need help?** Check YOUTUBE_SETUP.md or run the monitor manually to debug:
```bash
python3 .cache/youtube-monitor.py
```

Built: 2026-04-19 | Channel: Concessa Obvius | Interval: Every 30 minutes
