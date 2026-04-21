# YouTube Comment Monitor - Setup & Integration

**Status:** ✅ Ready to Deploy  
**Channel:** Concessa Obvius  
**Check Interval:** Every 30 minutes  
**Log Location:** `.cache/youtube-comments.jsonl`

---

## 🚀 Quick Start

### 1. Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable **YouTube Data API v3**
4. Create an **API Key** (Credentials → Create Credentials → API Key)
5. Copy the key

### 2. Set Environment Variable

```bash
export YOUTUBE_API_KEY="your-api-key-here"
```

Or add to your shell profile (`~/.zshrc` or `~/.bash_profile`):
```bash
export YOUTUBE_API_KEY="your-api-key-here"
```

### 3. Update Configuration

Edit `.cache/youtube-monitor-config.json`:

```json
{
  "channel": {
    "name": "Concessa Obvius",
    "channelId": "UCxxxxxx",  // ← Update this
    "checkInterval": 30
  },
  ...
}
```

**How to find Channel ID:**
1. Go to the channel page
2. Right-click → View Page Source
3. Search for `"channelId":"UC..."`

Or use: `https://www.youtube.com/oembed?url=https://www.youtube.com/@ConcessaObvious&format=json`

### 4. Test the Monitor

```bash
node .cache/youtube-monitor-api.js
```

Expected output:
```
[2026-04-20T22:00:00.000Z] Starting YouTube comment monitor...
Found 50 recent videos
Video abc123: 15 comment threads
✓ [questions] "How do I start?"
✓ [praise] "This is amazing..."
⚠ [sales] "Let's partner up!"

============================================================
YOUTUBE COMMENT MONITOR REPORT
============================================================
Channel: Concessa Obvius
Timestamp: 2026-04-20T22:00:00.000Z
New comments processed: 20
Total comments processed (all-time): 20
Auto-responses sent: 8
Total auto-responses (all-time): 8
Flagged for review: 3
Total flagged (all-time): 3
Log file: .cache/youtube-comments.jsonl
============================================================
```

---

## 🤖 OpenClaw Cron Integration

### Register Cron Task

Add to your OpenClaw config or run:

```bash
openclaw cron register \
  --name "youtube-comment-monitor" \
  --schedule "*/30 * * * *" \
  --command "node ~/.openclaw/workspace/.cache/youtube-monitor-api.js" \
  --env YOUTUBE_API_KEY="your-api-key" \
  --description "Monitor Concessa Obvius channel for new comments"
```

### Or Use OpenClaw Cron Directly

```bash
openclaw cron schedule \
  --task "YouTube Comment Monitor" \
  --interval "30 minutes" \
  --script "node .cache/youtube-monitor-api.js"
```

### Verify Cron Job

```bash
openclaw cron list
```

---

## 📊 Log Format

Each comment is logged to `.cache/youtube-comments.jsonl` (JSON Lines format):

```json
{
  "timestamp": "2026-04-20T22:00:00.123Z",
  "commenter": "John Doe",
  "text": "How do I get started with this?",
  "category": "questions",
  "response_status": "auto-responded",
  "autoResponseText": "Thanks for your question! I cover this in detail in our resources..."
}
```

### Query the Log

```bash
# Count all comments
wc -l .cache/youtube-comments.jsonl

# Filter by category
grep '"category":"questions"' .cache/youtube-comments.jsonl | wc -l

# View most recent comments
tail -20 .cache/youtube-comments.jsonl | jq '.'

# Export flagged sales inquiries
grep '"category":"sales"' .cache/youtube-comments.jsonl | jq '.' > flagged-sales.json
```

---

## 🎯 Auto-Response Categories

### 1. Questions ❓
**Pattern:** "how do i", "cost", "tools", "timeline", "start", "where can", etc.  
**Action:** Auto-respond with one of 3 template responses  
**Example:** "How do I get started?"

### 2. Praise ⭐
**Pattern:** "amazing", "inspiring", "love it", "thank you", "awesome", etc.  
**Action:** Auto-respond with gratitude template  
**Example:** "This video changed my life!"

### 3. Spam 🚫
**Pattern:** "crypto", "bitcoin", "nft", "mlm", "dropshipping", etc.  
**Action:** Log (not auto-responded)  
**Example:** "Buy Bitcoin now! 🚀"

### 4. Sales 💼
**Pattern:** "partnership", "collaboration", "sponsor", "advertise", "affiliate"  
**Action:** Flag for manual review  
**Example:** "Let's do a brand partnership deal"

### 5. General 📝
**Default** if none of above match  
**Action:** Log only  
**Example:** Random commentary

---

## 📈 Reports

The monitor generates reports at each run:

```
Total comments processed: 20
Auto-responses sent: 8
Flagged for review: 3
```

### View Historical Stats

```bash
# Current session state
cat .cache/youtube-monitor-state.json | jq '.'

# Output:
{
  "totalProcessed": 1,234,
  "totalResponses": 456,
  "totalFlagged": 78,
  "lastChecked": "2026-04-20T22:00:00.000Z",
  "processedCommentIds": [...]
}
```

---

## ⚙️ Advanced Configuration

### Customize Response Templates

Edit `.cache/youtube-monitor-config.json`:

```json
{
  "responses": {
    "questions": [
      "Custom response 1",
      "Custom response 2"
    ],
    "praise": [
      "Thank you!",
      "Grateful for this."
    ]
  }
}
```

### Add New Categories

Extend the `categories` object in config:

```json
{
  "categories": {
    "feedback": {
      "patterns": ["bug", "issue", "broken", "error"],
      "autoRespond": false,
      "action": "flag"
    }
  }
}
```

---

## 🔐 Security Notes

- **API Key:** Don't commit to git. Use environment variables or `.env` files (not in version control).
- **Comment Data:** Logged locally. Contains public YouTube comments only.
- **OAuth:** Full reply posting requires OAuth setup (not just API key). Currently logs responses locally.

---

## 🛠 Troubleshooting

### "YOUTUBE_API_KEY not set"
```bash
export YOUTUBE_API_KEY="your-key"
node .cache/youtube-monitor-api.js
```

### "API error: 403"
- Check API key is valid
- Verify YouTube Data API v3 is enabled in Cloud Console
- Confirm API key has correct permissions

### "Channel not found"
- Verify `channelId` in config is correct
- Check channel is public and has videos

### No comments processed
- Run monitor manually to test: `node .cache/youtube-monitor-api.js`
- Check `.cache/youtube-monitor-state.json` for last run
- Verify comment feed has new comments

---

## 📝 Manual Runs

```bash
# Run immediately
cd ~/.openclaw/workspace
node .cache/youtube-monitor-api.js

# Run with debugging
DEBUG=1 node .cache/youtube-monitor-api.js

# Run and show last 10 logged comments
node .cache/youtube-monitor-api.js && tail -10 .cache/youtube-comments.jsonl | jq '.'
```

---

## 🚀 Production Checklist

- [ ] API key configured and tested
- [ ] Channel ID verified in config
- [ ] Cron task registered
- [ ] Log file location confirmed (`.cache/youtube-comments.jsonl`)
- [ ] Template responses customized (optional)
- [ ] First run successful with no errors
- [ ] Flagged comments reviewed

---

**Monitor Active:** Every 30 minutes  
**Last Updated:** 2026-04-20  
**Questions?** Check the log: `.cache/youtube-comments.jsonl`
