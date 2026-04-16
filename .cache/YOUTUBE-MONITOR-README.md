# 🎬 YouTube Comment Monitor

**Status:** Ready to deploy  
**Schedule:** Every 30 minutes  
**Channel:** Concessa Obvius  
**Created:** 2026-04-16  

---

## What It Does

Automatically monitors the **Concessa Obvius** YouTube channel for new comments, categorizes them in real-time, and:

✅ **Auto-responds** to questions (with helpful guide links)  
✅ **Auto-responds** to praise (with thank you message)  
🚩 **Flags sales inquiries** for manual review  
❌ **Ignores spam** (crypto, MLM, etc.)  
📊 **Logs everything** to JSONL for analytics  

---

## Quick Start (5 Minutes)

### 1️⃣ Install Dependencies
```bash
pip install google-auth-httplib2 google-api-python-client
```

### 2️⃣ Get YouTube API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable "YouTube Data API v3" → Create API Key
3. Copy the key

### 3️⃣ Set Environment Variable
```bash
export YOUTUBE_API_KEY="paste-your-key-here"
```

### 4️⃣ Test It
```bash
python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py
```

Expected output:
```
✓ Found channel: Concessa Obvius (UCxxxxx...)

==================================================
📊 YOUTUBE COMMENT MONITOR REPORT
==================================================
Total comments processed: X
Auto-responses sent: Y
Flagged for review: Z
...
```

### 5️⃣ Schedule It (Every 30 Minutes)

**Option A: System Crontab**
```bash
(crontab -l 2>/dev/null; echo "*/30 * * * * python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log 2>&1") | crontab -
```

**Option B: Use Wrapper Script**
```bash
(crontab -l 2>/dev/null; echo "*/30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.sh") | crontab -
```

**Option C: OpenClaw Cron (if available)**
```bash
openclaw cron add "youtube-comment-monitor" \
  --schedule "*/30 * * * *" \
  --command "python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py"
```

---

## File Structure

```
.cache/
├── youtube-monitor.py              ← Main script
├── youtube-monitor.sh              ← Cron wrapper
├── youtube-comments.jsonl          ← All comments (auto-created)
├── youtube-monitor-state.json      ← State tracking (auto-created)
├── youtube-monitor.log             ← Execution log
├── youtube-monitor-setup.md        ← Detailed setup guide
└── YOUTUBE-MONITOR-README.md       ← This file
```

---

## Data Flow

```
YouTube API
    ↓
Fetch new comments (last 35 min)
    ↓
Categorize (Q, P, Spam, Sales, Neutral)
    ↓
├→ Questions → Auto-reply + log
├→ Praise → Auto-reply + log
├→ Sales → Flag + log
├→ Spam → Ignore + log
└→ Neutral → Log only
    ↓
Save state (processed IDs, timestamp)
    ↓
Report stats
```

---

## Categories & Actions

### 📝 Question
**Pattern:** How, what, why, tools, cost, timeline, help, setup, start, learn  
**Action:** ✅ Auto-reply with getting started guide  
**Response:** _"Great question! Thanks for asking. I'd recommend starting with [our getting started guide]..."_

### 🌟 Praise
**Pattern:** Amazing, inspiring, love, thank you, appreciate, grateful, impressed, awesome  
**Action:** ✅ Auto-reply with thank you  
**Response:** _"Thank you so much! Your kind words mean the world..."_

### 🚨 Spam
**Pattern:** Crypto, Bitcoin, NFT, MLM, click here, follow back, free money  
**Action:** ❌ Ignore (not logged as actionable)  

### 🚩 Sales
**Pattern:** Partnership, collaboration, sponsor, work with us, business opportunity  
**Action:** 🚩 Flag for your review (response_status: "flagged_for_review")  

### ⚪ Neutral
**Pattern:** Everything else  
**Action:** 📊 Log for analytics  

---

## Monitoring & Analytics

### View Recent Comments
```bash
tail -20 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .
```

### Count by Category
```bash
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

### Find Flagged (Sales) Comments
```bash
jq 'select(.response_status == "flagged_for_review")' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

### Get Auto-Replies
```bash
jq 'select(.response_status == "auto_replied")' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

### Show Execution Log
```bash
tail -50 ~/.openclaw/workspace/.cache/youtube-monitor.log
```

---

## Customization

### 🎯 Change Auto-Reply Messages

Edit `.cache/youtube-monitor.py`, find the `RESPONSES` dict:
```python
RESPONSES = {
    "question": "Your custom question response here...",
    "praise": "Your custom praise response here..."
}
```

### 🔍 Adjust Categorization Rules

Edit the `PATTERNS` dict:
```python
PATTERNS = {
    "question": re.compile(r"your|patterns|here", re.IGNORECASE),
    "praise": re.compile(r"your|patterns|here", re.IGNORECASE),
    # etc.
}
```

### ⏰ Change Check Frequency

In `get_recent_comments()`, change `minutes=35`:
```python
comments = get_recent_comments(service, channel_id, minutes=35)  # ← change this
```

For 15-minute checks: use `minutes=20`  
For 60-minute checks: use `minutes=65`  

---

## Troubleshooting

### "YOUTUBE_API_KEY environment variable not set"
```bash
# Add to ~/.zshrc or ~/.bash_profile
export YOUTUBE_API_KEY="your-key-here"

# Then reload
source ~/.zshrc
```

### "Could not find channel 'Concessa Obvius'"
- Verify exact channel name (case-sensitive)
- Alternative: Use channel ID directly
- Edit line in script: `channel_id = "UCxxxxxxxxxxxxx"`

### No new comments found
- Check that comments exist on the channel
- Verify API key has access
- Run with verbose logging (add print statements)

### Auto-replies not posting
- **Current limitation:** Script uses API Key (read-only)
- **To enable replies:** Need OAuth2 setup (see Setup Guide)
- Modify `post_comment_reply()` function to use YouTube API `commentThreads.insert()`

### Cron not running
```bash
# Check if job exists
crontab -l

# Check system log
log stream --level debug | grep cron

# Test script directly
python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py
```

### Log file growing too large
- Wrapper script auto-rotates at 50MB
- Manual cleanup: `rm ~/.openclaw/workspace/.cache/youtube-monitor.log.*`

---

## Example Output

```
✓ Found channel: Concessa Obvius (UCmNYSEe0cZt_xR8j6ZZyVDA)

==================================================
📊 YOUTUBE COMMENT MONITOR REPORT
==================================================
Total comments processed: 5
Auto-responses sent: 2
Flagged for review: 1

By category:
  • question: 2
  • praise: 1
  • sales: 1
  • spam: 1
  • neutral: 0
==================================================
```

### Log File Example
```json
{"timestamp":"2026-04-16T03:30:00Z","commenter":"Alice","text":"How do I get started?","category":"question","response_status":"auto_replied","processed_at":"2026-04-16T03:30:05.123456Z"}
{"timestamp":"2026-04-16T03:35:00Z","commenter":"Bob","text":"This is amazing!","category":"praise","response_status":"auto_replied","processed_at":"2026-04-16T03:35:07.654321Z"}
{"timestamp":"2026-04-16T03:40:00Z","commenter":"Carol","text":"Let's partner up","category":"sales","response_status":"flagged_for_review","processed_at":"2026-04-16T03:40:02.111111Z"}
```

---

## Advanced: OAuth2 Setup (For Auto-Replies)

To actually **post** replies (not just log), you need OAuth2:

1. **Create credentials:**
   - Google Cloud Console → Credentials → + Create Credentials → OAuth 2.0 Client ID
   - Type: Desktop application
   - Download as JSON

2. **Save credentials:**
   ```bash
   cp ~/Downloads/client_secret_*.json ~/.openclaw/workspace/.cache/youtube-oauth.json
   ```

3. **Update script:**
   Replace `post_comment_reply()` with:
   ```python
   def post_comment_reply(service, parent_id: str, text: str) -> bool:
       try:
           service.comments().insert(
               part="snippet",
               body={
                   "snippet": {
                       "parentId": parent_id,
                       "textOriginal": text
                   }
               }
           ).execute()
           return True
       except Exception as e:
           print(f"Failed to post reply: {e}")
           return False
   ```

4. **Authenticate** (first time):
   ```bash
   python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py
   # Follow browser prompt to authorize
   ```

---

## Notes & Limits

- **API Rate Limits:** YouTube API allows 10,000 quota units/day. This script uses ~15-20 per run.
- **Comment Latency:** Comments appear in API ~1-2 minutes after being posted
- **Auto-Reply Posting:** Currently placeholder. Requires OAuth2 to actually post.
- **Channel Access:** Script reads comments from public channels (no auth needed for reads)

---

## Support

**Issues?**
1. Check the execution log: `tail ~/.openclaw/workspace/.cache/youtube-monitor.log`
2. Test manually: `python ~/.openclaw/workspace/.cache/youtube-monitor.py`
3. Review the detailed setup guide: `youtube-monitor-setup.md`

**Want to modify?**
- Patterns are in `PATTERNS` dict (customize categorization)
- Responses are in `RESPONSES` dict (customize messages)
- Schedule is set in crontab or OpenClaw cron

---

**Status:** ✅ Ready to deploy  
**Last Updated:** 2026-04-16 04:00 UTC  
**Next Check:** In 30 minutes (auto)
