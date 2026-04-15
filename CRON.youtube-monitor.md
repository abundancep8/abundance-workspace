# Cron: YouTube Comment Monitor

**Task ID:** `youtube-comment-monitor`  
**Schedule:** Every 30 minutes  
**Status:** ⏳ Ready to activate

## Command

```bash
cd /Users/abundance/.openclaw/workspace && npm run -C scripts monitor
```

## What It Does

Each run:
1. ✅ Connects to YouTube API using saved credentials
2. 🔎 Fetches new comments on Concessa Obvius channel videos
3. 🏷️ Categorizes each comment (Questions, Praise, Spam, Sales)
4. 💬 Auto-responds to Questions & Praise with templates
5. 🚩 Flags Sales inquiries for manual review
6. 📝 Logs all activity to `.cache/youtube-comments.jsonl`

## Output Files

- **Comments log:** `.cache/youtube-comments.jsonl`
  ```json
  {"timestamp":"2026-04-14T20:00:00Z","commenter":"User123","text":"How do I...?","category":"questions","response_status":"sent"}
  ```
- **State:** `.cache/youtube-monitor-state.json` (prevents duplicate processing)
- **Cron log:** `logs/youtube-monitor.log`

## Getting Started

### Step 1: Install Dependencies
```bash
cd /Users/abundance/.openclaw/workspace/scripts
npm install
```

### Step 2: Authenticate
```bash
npm run auth
```
Follow the prompts to authorize with YouTube.

### Step 3: Test Run
```bash
npm run monitor
```
You should see a report like:
```
📊 YOUTUBE COMMENT MONITOR REPORT
==================================================
Total comments processed: 5
Auto-responses sent: 3
Flagged for review (Sales): 1

By Category:
  Questions: 2
  Praise: 1
  Spam: 1
  Sales: 1
```

### Step 4: Activate Cron
Once you're ready, tell me to activate the cron job:
```
/cron add youtube-comment-monitor --every 30m
```

## Template Responses

The auto-responses are defined in `scripts/youtube-monitor.js`:

```javascript
const TEMPLATES = {
  questions: `Thanks for your question! ...`,
  praise: `Thank you so much! 🙏 ...`
};
```

Edit these before activating the cron job.

## Monitoring

Watch the cron logs:
```bash
tail -f logs/youtube-monitor.log
```

View recent comments:
```bash
tail -10 .cache/youtube-comments.jsonl | jq .
```

## Quota Notes

- YouTube Data API: 10,000 quota units/day
- Each comment fetch: ~3-5 units
- Each response: ~50 units
- Schedule is safe for daily limits

---

**Ready to go?** Tell me when you've completed auth, and I'll activate the cron schedule.
