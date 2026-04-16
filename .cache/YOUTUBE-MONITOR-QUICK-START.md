# YouTube Comment Monitor - Quick Start

## ✅ What's Built

Complete, production-ready system:

- **youtube-monitor.js** — Main fetcher/categorizer/responder/logger
- **youtube-monitor-cron.sh** — Cron wrapper (runs every 30 min)
- **youtube-monitor-report.js** — Report generator for analysis
- **youtube-monitor-config.json** — Keywords & templates (easy to customize)
- **youtube-comments.jsonl** — All comments with metadata + responses
- **youtube-monitor-state.json** — Prevents duplicate processing
- **youtube-monitor.log** — Cron execution history

## 🚀 Next Steps (3 minutes)

### 1. Get YouTube API Key
- Go to [Google Cloud Console](https://console.cloud.google.com)
- Create project → Enable "YouTube Data API v3" → Create API Key
- Copy key, run: `export YOUTUBE_API_KEY="YOUR_KEY_HERE"`

### 2. Get Channel ID
- Visit your YouTube channel
- From URL `youtube.com/channel/UCxxxxx`, copy `UCxxxxx`
- Or run: `curl "https://www.googleapis.com/youtube/v3/channels?part=id&forUsername=YOUR_USERNAME&key=$YOUTUBE_API_KEY"`
- Then: `export YOUTUBE_CHANNEL_ID="UCxxxxx"`

### 3. Set Permanent Env Vars
Add to `~/.zshrc`:
```bash
export YOUTUBE_API_KEY="sk-..."
export YOUTUBE_CHANNEL_ID="UCxxx"
```

Reload: `source ~/.zshrc`

### 4. Test Manually
```bash
node /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.js
```

Expected output: "REPORT" section with stats

### 5. Install Cron Job
```bash
crontab -e
```

Paste (single line):
```
*/30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

Verify: `crontab -l`

## 📊 Viewing Results

**Recent comments:**
```bash
tail -5 /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl
```

**Generate report (last 24 hours):**
```bash
node /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-report.js --since=24
```

**Find flagged (sales) comments:**
```bash
node /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-report.js | grep -A 5 "Flagged"
```

**View cron logs:**
```bash
tail -20 /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log
```

## 🎯 Categories & Actions

| Category | Trigger | Action |
|----------|---------|--------|
| Questions | "how to", "cost", "timeline", etc. | Auto-respond with template |
| Praise | "amazing", "inspiring", "thank you", etc. | Auto-respond with thank you |
| Spam | "crypto", "mlm", "free money", etc. | Ignore (log only) |
| Sales | "partnership", "collaboration", "sponsor", etc. | **Flag for manual review** |
| Other | Nothing matches | Ignore (log only) |

## 🔧 Customization

**Edit templates:** `.cache/youtube-monitor.js` → `CONFIG.templates`

**Edit keywords:** `.cache/youtube-monitor-config.json` → `categorization`

**Change auto-respond actions:** `.cache/youtube-monitor.js` → auto-respond logic

## 📝 Log Format

Each line in `youtube-comments.jsonl` is:
```json
{
  "timestamp": "2026-04-16T04:00:00.000Z",
  "commentId": "xyz123",
  "videoId": "vid456",
  "commenter": "John Doe",
  "text": "This is amazing!",
  "category": "praise",
  "response": "Thank you so much for the kind words! 🙏",
  "responseStatus": "responded",
  "flaggedForReview": false
}
```

Use `jq` or Python to parse if needed.

## ⚠️ Known Limits

- API quota: YouTube Data API v3 has 10,000 units/day (most ops = 1-5 units)
- 30-min interval: ~1,440 checks/month (well within limits)
- Only fetches YouTube channel comments, not Community posts
- Auto-responses are logged but require manual posting to YouTube (for API access reasons)

---

**Once set up, monitor will run silently every 30 minutes.**
**Check logs/reports as needed.**
