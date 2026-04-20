# YouTube Comment Monitor - Setup Guide

## Prerequisites

1. **YouTube API Key**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable YouTube Data API v3
   - Create an API Key (restrict to YouTube Data API)
   - Set environment variable: `export YOUTUBE_API_KEY="your-key-here"`

2. **Channel ID**
   - For "Concessa Obvius": Navigate to the channel
   - Check the URL for the channel ID (usually in `/c/...` or `/@...` format)
   - Or use the YouTube Data API: `https://www.googleapis.com/youtube/v3/search?part=snippet&q=Concessa%20Obvius&key=YOUR_KEY`
   - Update `CONFIG.channelId` in `youtube-monitor.js`

3. **Node.js** (v14+)
   ```bash
   node --version
   ```

## Installation

```bash
# Make the script executable
chmod +x /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.js

# Ensure .cache directory exists
mkdir -p /Users/abundance/.openclaw/workspace/.cache
```

## Configuration

Edit the `CONFIG` object in `youtube-monitor.js`:

```javascript
const CONFIG = {
  channelId: 'ACTUAL_CHANNEL_ID_HERE',  // ← Update this
  logFile: '/Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl',
  stateFile: '/Users/abundance/.openclaw/workspace/.cache/youtube-monitor-state.json',
  apiKey: process.env.YOUTUBE_API_KEY,  // Set via env var
};
```

## Running Manually

```bash
export YOUTUBE_API_KEY="your-api-key"
node /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.js
```

Expected output:
```
📊 YouTube Comment Monitor Report
──────────────────────────────────
✅ Processed:      5 comments
💬 Auto-responses: 2 sent
🚩 Flagged review: 1 comments
...
```

## Cron Setup (Every 30 minutes)

Add to crontab (`crontab -e`):

```bash
# Run every 30 minutes
*/30 * * * * export YOUTUBE_API_KEY="your-api-key" && node /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.js >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log 2>&1
```

Or use OpenClaw's built-in cron support:

```bash
openclaw cron add --interval 30m --task "node /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.js"
```

## Output Files

- **youtube-comments.jsonl** - Timestamped log of all comments
  ```json
  {"timestamp": "2026-04-20T01:30:00Z", "commenter": "John Doe", "text": "How do I get started?", "category": "question", "responseStatus": "auto-responded"}
  ```

- **youtube-monitor-state.json** - Tracks last check time and processed comment IDs
  ```json
  {
    "lastCheckTime": "2026-04-20T01:30:00Z",
    "processedIds": ["aaaa.bbbb.cccc", ...]
  }
  ```

- **youtube-monitor.log** - Execution logs (if using cron)

## Customization

### Add Custom Response Templates

Edit the `TEMPLATES` object:

```javascript
const TEMPLATES = {
  question: `Thanks for the question! ...[personalized response]...`,
  praise: `Thank you! ...[acknowledgment]...`,
};
```

### Adjust Categorization Rules

Modify the `categorizeComment()` function to refine detection patterns.

### Auto-Reply to Comments (Advanced)

Current implementation logs auto-responses but doesn't actually post them yet. To enable:

1. Set up OAuth 2.0 credentials (not just API key)
2. Implement the YouTube Comments API `insert` method
3. Handle rate limits (500 requests/day for non-whitelisted apps)

Example (requires OAuth):
```javascript
async function replyToComment(commentId, text) {
  // Use YouTube API to insert a reply
  // POST /youtube/v3/comments with snippet.parentId = commentId
}
```

## Troubleshooting

**"YOUTUBE_API_KEY not set"**
- Ensure the environment variable is exported before running
- Check: `echo $YOUTUBE_API_KEY`

**"No comments found"**
- Verify the channel ID is correct
- Check that comments are public on the channel
- Ensure API key has YouTube Data API v3 enabled

**Rate Limit Errors**
- Standard API quota: 10,000 units/day
- Each request uses ~3 units
- Monitor at [Google Cloud Console](https://console.cloud.google.com/apis/dashboard)

**Comments Not Being Processed**
- Check `youtube-monitor-state.json` to ensure state is persisting
- Verify file permissions: `ls -la .cache/`

## Monitoring the Monitor

View recent comments:
```bash
tail -f /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl
```

View logs (if using cron):
```bash
tail -f /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log
```

Check state:
```bash
cat /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-state.json
```

## Next Steps

1. ✅ Get YouTube API key
2. ✅ Find the channel ID for Concessa Obvius
3. ✅ Update CONFIG in the script
4. ✅ Test manually: `node youtube-monitor.js`
5. ✅ Set up cron job
6. 📊 Monitor logs and tweak categorization as needed
