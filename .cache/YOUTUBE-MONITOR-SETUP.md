# YouTube Comment Monitor - Setup Guide

## Overview
Monitors the **Concessa Obvius** YouTube channel every 30 minutes for new comments. Categorizes, auto-responds, and logs all activity.

## Prerequisites

### 1. Install Dependencies
```bash
pip install google-auth-httplib2 google-api-python-client
```

### 2. YouTube API Setup

#### Option A: Simple API Key (Read-Only)
For **monitoring only** (no replies):

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create an API key (Credentials → Create Credentials → API Key)
5. Set environment variable:
```bash
export YOUTUBE_API_KEY="your-api-key-here"
```

#### Option B: OAuth2 (Full Access - Needed for Auto-Replies)
For **monitoring + posting replies**:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create OAuth 2.0 credentials (Credentials → Create Credentials → OAuth 2.0 Client ID)
5. Download JSON and save to `~/.openclaw/workspace/.cache/youtube-credentials.json`
6. Set environment variable:
```bash
export YOUTUBE_OAUTH_CREDENTIALS="/Users/abundance/.openclaw/workspace/.cache/youtube-credentials.json"
```

**Note:** The current script only supports API Key. To enable auto-replies, modify the `post_comment_reply()` function to use OAuth2.

## Running

### Manual Test
```bash
python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py
```

### Automatic (Every 30 Minutes)
Add to your OpenClaw cron via:
```bash
openclaw cron add "youtube-comment-monitor" \
  --schedule "*/30 * * * *" \
  --command "python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py"
```

Or use this in a cron expression:
```
*/30 * * * * python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log 2>&1
```

## Output Files

- **`.cache/youtube-comments.jsonl`** — Detailed log of all comments (JSON Lines format)
- **`.cache/youtube-monitor-state.json`** — Last processed timestamp and comment IDs
- **`.cache/youtube-monitor.log`** — Execution logs (if using cron)

## Log Format

Each line in `youtube-comments.jsonl`:
```json
{
  "timestamp": "2026-04-16T04:00:00Z",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "question",
  "response_status": "auto_replied",
  "processed_at": "2026-04-16T04:00:05.123456Z"
}
```

## Categories

| Category | Pattern | Action |
|----------|---------|--------|
| **Question** | how, what, why, tools, cost, timeline, help | ✅ Auto-reply with guide |
| **Praise** | amazing, inspiring, love, thank you, impressed | ✅ Auto-reply with thank you |
| **Spam** | crypto, mlm, click here, follow back | ❌ Ignore |
| **Sales** | partnership, collaboration, sponsor, work with us | 🚩 Flag for review |
| **Neutral** | (no match) | — Log only |

## Customization

### Change Templates
Edit `RESPONSES` in the script:
```python
RESPONSES = {
    "question": "Your custom question response...",
    "praise": "Your custom praise response..."
}
```

### Add/Modify Patterns
Edit `PATTERNS` dictionary to fine-tune categorization.

### Change Check Interval
In `get_recent_comments()`, adjust the `minutes` parameter (default: 35 minutes for 30-min checks with 5-min buffer).

## Troubleshooting

### "YOUTUBE_API_KEY environment variable not set"
```bash
export YOUTUBE_API_KEY="your-key"
python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py
```

### "Could not find channel 'Concessa Obvius'"
- Verify the channel name is exact
- Try using the channel ID directly (modify script)

### Auto-replies not working
- Requires OAuth2 setup (see Option B above)
- Current script posts replies as placeholder only
- Modify `post_comment_reply()` to use `youtube.commentThreads().insert()` with OAuth2

## Monitoring

Check recent activity:
```bash
# Last 10 entries
tail -10 /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl

# Count by category
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' \
  /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl

# Find flagged comments
jq 'select(.response_status == "flagged_for_review")' \
  /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl
```

---

**Last Updated:** 2026-04-16
