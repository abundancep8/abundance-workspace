# 📺 YouTube Comment Monitor - Concessa Obvius

**Automated comment categorization, response, and logging system for your YouTube channel.**

## What It Does

✅ **Monitors** new comments every 30 minutes  
✅ **Categorizes** comments (questions, praise, spam, sales)  
✅ **Auto-responds** to questions & praise with templates  
🚩 **Flags** sales inquiries for manual review  
🗑️ **Filters** spam (crypto, MLM, etc.)  
📊 **Logs everything** to `.cache/youtube-comments.jsonl`  
📈 **Reports** statistics on each run  

## Quick Start

### 1. Install Dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Get YouTube API Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the JSON file
6. Save it as: `~/.openclaw/workspace/.cache/youtube-credentials.json`

### 3. Update Channel ID
Edit `youtube-comment-monitor.py`, line ~45:
```python
"channel_id": "UCyourActualChannelId",  # Get from youtube.com/channel/UC...
```

### 4. Test Manually
```bash
cd ~/.openclaw/workspace
python3 .cache/youtube-comment-monitor.py
```

First run will open a browser for OAuth auth. Approve it. Done.

### 5. Set Up Cron (Every 30 Minutes)
```bash
crontab -e
```

Add:
```
*/30 * * * * cd ~/.openclaw/workspace && python3 .cache/youtube-comment-monitor.py >> .cache/youtube-monitor.log 2>&1
```

Verify:
```bash
crontab -l | grep youtube-comment-monitor
```

## File Structure

```
.cache/
├── youtube-comment-monitor.py          ← Main script
├── youtube-comment-monitor.sh          ← Cron wrapper
├── youtube-comment-monitor-setup.md    ← Detailed setup guide
├── youtube-credentials.json            ← Your OAuth client secret (CREATE THIS)
├── youtube-token.json                  ← Auto-saved auth token (auto-created)
├── youtube-comments.jsonl              ← All comments logged here
├── youtube-monitor-state.json          ← Tracks processed comments
├── youtube-monitor.log                 ← Cron execution log
└── youtube-monitor-report.txt          ← Summary reports
```

## Comment Categories

### 1️⃣ Questions
**Auto-responds with template**

Patterns: "How do I...", "What is...", "tools", "cost", "timeline"

Example:
```
Q: How much does this cost?
→ ✅ Auto-responded with template
```

### 2️⃣ Praise
**Auto-responds with thank you**

Patterns: "amazing", "inspiring", "love this", "game-changer"

Example:
```
Q: This changed my life! Amazing content!
→ ✅ Auto-responded with thank you
```

### 3️⃣ Spam
**Logged, not responded**

Patterns: crypto, bitcoin, MLM, "get rich quick"

Example:
```
Q: Get rich quick with my crypto scheme!
→ 🗑️ Filtered as spam
```

### 4️⃣ Sales
**Flagged for your review**

Patterns: "partnership", "collaboration", "sponsor", "business opportunity"

Example:
```
Q: I'd like to discuss a partnership opportunity.
→ 🚩 Flagged for review
```

## Log Format

Each comment is logged as JSON (JSONL = one JSON per line):

```json
{
  "timestamp": "2026-04-18T10:00:15.123456+00:00",
  "comment_id": "UgyABC123",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "questions",
  "response_status": "auto_responded",
  "published_at": "2026-04-18T09:55:00Z"
}
```

### View Logs

**All comments:**
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

**Pretty-print:**
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | python3 -m json.tool
```

**Filter by category:**
```bash
grep '"category": "questions"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

**Count by category:**
```bash
grep -o '"category": "[^"]*"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | sort | uniq -c
```

## Reports

Each run generates a report with:
- Total comments processed
- Auto-responses sent
- Sales inquiries flagged for review

View the latest:
```bash
tail ~/.openclaw/workspace/.cache/youtube-monitor-report.txt
```

View cron execution log:
```bash
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log
```

## Customization

### Change Response Templates

Edit `RESPONSES` dict in `youtube-comment-monitor.py`:

```python
RESPONSES = {
    "questions": """Thanks for asking! Here's my recommendation: {answer}

Learn more at: [your link here]""",
    "praise": """Wow, thank you! 🙏 This means everything.""",
}
```

### Add Custom Categorization Rules

Edit `PATTERNS` dict:

```python
"questions": [
    r"how (do|can|should|would) i",
    r"your custom pattern here",
    r"another pattern",
]
```

### Change Monitoring Frequency

Instead of 30 minutes, edit crontab:
- Every 15 min: `*/15 * * * *`
- Every hour: `0 * * * *`
- Every 6 hours: `0 */6 * * *`

## Troubleshooting

### "Channel not found"
Check your channel ID. From YouTube channel URL:
- Wrong: `youtube.com/@username` → Use the URL, it redirects
- Right: `youtube.com/channel/UCyour_actual_id`

### "API quota exceeded"
YouTube gives 10,000 units/day free. Each monitoring run uses ~100-200 units.

Request more: Google Cloud Console → APIs & Services → Quotas → YouTube Data API v3

### "Authentication failed"
Reset OAuth:
```bash
rm ~/.openclaw/workspace/.cache/youtube-token.json
```
Then run the script again. A browser will open for re-auth.

### "No new comments found"
- Channel might have comments disabled
- No new comments since last run
- Check `.cache/youtube-monitor-state.json` for processed IDs

### "Cron not running"
```bash
# Check if cron is running
pgrep cron

# Verify crontab entry
crontab -l

# Check system log
log stream --predicate 'process == "cron"' --level debug
```

## Example Output

```
🟡 Starting YouTube Comment Monitor...
✅ YouTube API authenticated
📥 Found 5 new comments
  ✅ Responded to question from Sarah
  ✅ Thanked Jane for praise
  ✅ Responded to question from Mike
  🚩 Flagged sales inquiry from Enterprise Inc.
  🗑️ Filtered spam from CryptoBroker

╔════════════════════════════════════════════════════════════╗
║         YOUTUBE COMMENT MONITOR - CONCESSA OBVIUS          ║
╚════════════════════════════════════════════════════════════╝

Scan Time: 2026-04-18 10:00:15

📊 STATISTICS
─────────────────────────────────────────────────────────────
Total comments processed:        5
Auto-responses sent:             3
Flagged for review (sales):      1

✅ Next scan: 30 minutes from now
```

## Security

✅ **Do:**
- Keep `youtube-credentials.json` in `.cache/` (hidden from most VCS)
- Use `.gitignore` to exclude:
  ```
  .cache/youtube-credentials.json
  .cache/youtube-token.json
  .cache/youtube-monitor-state.json
  ```
- Rotate credentials every 6 months

❌ **Don't:**
- Commit credentials to version control
- Share your credentials file
- Use the same credentials across multiple machines (create separate OAuth apps)

## API Limits

**YouTube Data API v3 Quotas (Free tier):**
- 10,000 units/day
- Each call costs different units
- Typical monitor run: ~100-200 units
- Plenty of headroom for 48 runs/day (every 30 min)

**If you hit the limit:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. APIs & Services → Quotas
3. Find "YouTube Data API v3"
4. Request quota increase (free for reasonable amounts)

## Support & Debugging

1. **Check execution log:**
   ```bash
   tail -50 ~/.openclaw/workspace/.cache/youtube-monitor.log
   ```

2. **Run manually with verbose output:**
   ```bash
   cd ~/.openclaw/workspace
   python3 -u .cache/youtube-comment-monitor.py
   ```

3. **Check API is enabled:**
   Visit [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Enabled APIs → Search "YouTube Data API v3"

4. **Verify credentials file:**
   ```bash
   cat ~/.openclaw/workspace/.cache/youtube-credentials.json | python3 -m json.tool
   ```

## Next Steps

- [ ] Install dependencies
- [ ] Get YouTube API credentials
- [ ] Update channel ID in script
- [ ] Test manually
- [ ] Set up cron
- [ ] Monitor logs for first week
- [ ] Customize response templates
- [ ] (Optional) Add custom categorization rules

---

**Created:** 2026-04-18  
**Last Updated:** 2026-04-18  
**Cron Job ID:** 114e5c6d-ac8b-47ca-a695-79ac31b5c076
