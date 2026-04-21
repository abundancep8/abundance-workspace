# OpenClaw Cron Setup for YouTube Comment Monitor

This document explains how to run the YouTube Comment Monitor every 30 minutes using OpenClaw's cron system.

## Option 1: Use System Crontab (Simpler)

If you prefer traditional cron:

```bash
crontab -e
```

Add this line:

```
*/30 * * * * cd /Users/abundance/.openclaw/workspace && YOUTUBE_API_KEY="your-api-key" bash .cache/youtube-monitor.sh >> .cache/youtube-monitor.log 2>&1
```

Replace `"your-api-key"` with your actual YouTube API key.

Test with:

```bash
bash .cache/youtube-monitor.sh
```

---

## Option 2: Use OpenClaw Cron Scheduler

OpenClaw has a built-in cron system. You can register a recurring job via the CLI or config.

### Via OpenClaw Config

Add to your `.openclaw/config.json` or `.openclaw/cron.json`:

```json
{
  "crons": [
    {
      "id": "youtube-comment-monitor",
      "name": "YouTube Comment Monitor",
      "description": "Monitor Concessa Obvius channel for new comments every 30 minutes",
      "schedule": "*/30 * * * *",
      "command": "cd /Users/abundance/.openclaw/workspace && python3 .cache/youtube-monitor.py",
      "env": {
        "YOUTUBE_API_KEY": "${YOUTUBE_API_KEY}",
        "YOUTUBE_CHANNEL_ID": "UCxxxxxxxxx"
      },
      "timeout": 60,
      "onSuccess": "log",
      "onFailure": "log"
    }
  ]
}
```

Then reload OpenClaw:

```bash
openclaw gateway restart
```

### Via OpenClaw CLI

```bash
openclaw cron add \
  --id youtube-comment-monitor \
  --schedule "*/30 * * * *" \
  --command "cd /Users/abundance/.openclaw/workspace && python3 .cache/youtube-monitor.py"
```

Check cron status:

```bash
openclaw cron list
openclaw cron status youtube-comment-monitor
openclaw cron logs youtube-comment-monitor
```

---

## Environment Variables

The monitor needs your YouTube API key. Store it securely:

### Option A: System Environment

```bash
# Add to ~/.zshrc (macOS) or ~/.bashrc (Linux)
export YOUTUBE_API_KEY="your-api-key"
```

Then reload:

```bash
source ~/.zshrc
```

### Option B: .env File

Create `.openclaw/workspace/.env`:

```
YOUTUBE_API_KEY=your-api-key
YOUTUBE_CHANNEL_ID=UCxxxxxxxxx
```

The `youtube-monitor.sh` wrapper will load it automatically.

### Option C: OpenClaw Secrets

If your OpenClaw supports secrets management:

```bash
openclaw secrets set YOUTUBE_API_KEY "your-api-key"
```

Then reference it in cron:

```json
"env": {
  "YOUTUBE_API_KEY": "${YOUTUBE_API_KEY}"
}
```

---

## Verifying Setup

### Test the Script Manually

```bash
cd /Users/abundance/.openclaw/workspace
YOUTUBE_API_KEY="your-key" python3 .cache/youtube-monitor.py
```

Expected output:

```
🎬 YouTube Comment Monitor
Channel: Concessa Obvius
Time: 2026-04-21T00:12:34.567890

✅ Channel ID: UCxxxxxxxxx
Fetching comments...

Found 3 new comments. Processing...

============================================================
📊 REPORT
============================================================
Processed: 3
Auto-responses sent: 2
Flagged for review: 1
Log file: .cache/youtube-comments.jsonl
============================================================
```

### Check Cron Logs

System cron:

```bash
tail -f .cache/youtube-monitor.log
```

OpenClaw cron:

```bash
openclaw cron logs youtube-comment-monitor --follow
```

### Verify Comment Log

```bash
cat .cache/youtube-comments.jsonl | jq . | head -20
```

Should show entries like:

```json
{
  "timestamp": "2026-04-21T07:00:00Z",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "question",
  "response": "Thanks for the great question! Check out our getting started guide...",
  "response_status": "sent",
  "video_id": "dQw4w9WgXcQ",
  "comment_id": "UgyXXXXXXX"
}
```

---

## Monitoring & Alerts

### Check Comments Awaiting Review

Every 30 minutes, flagged comments (category = "sales") should be reviewed:

```bash
cat .cache/youtube-comments.jsonl | jq 'select(.category == "sales" and .response_status == "flagged")'
```

### Recent Activity

```bash
tail -20 .cache/youtube-comments.jsonl | jq .
```

### Stats

Total comments processed:

```bash
wc -l .cache/youtube-comments.jsonl
```

By category:

```bash
cat .cache/youtube-comments.jsonl | jq '.category' | sort | uniq -c
```

Auto-responses sent:

```bash
cat .cache/youtube-comments.jsonl | jq 'select(.response_status == "sent")' | wc -l
```

---

## Troubleshooting

### Cron Not Running

Check that the cron is registered and enabled:

**System cron:**
```bash
crontab -l
```

**OpenClaw cron:**
```bash
openclaw cron list --verbose
```

### "YOUTUBE_API_KEY not set"

Ensure the env var is exported:

```bash
echo $YOUTUBE_API_KEY
```

If empty, set it:

```bash
export YOUTUBE_API_KEY="your-key"
```

### Permissions Error

Make sure the script is executable:

```bash
chmod +x .cache/youtube-monitor.sh
```

And the `.cache` directory is writable:

```bash
chmod 755 .cache
```

### API Quota Exceeded

Check your Google Cloud Console quota:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. **APIs & Services** → **Quotas**
4. Find "YouTube Data API v3"
5. View daily limits and current usage

If you're hitting limits:
- Increase the cron interval (e.g., run every hour instead of 30 min)
- Request a higher quota (takes 24h approval)
- Use a service account with higher limits

---

## Example: Custom Response Logic

To customize responses, edit `.cache/youtube-monitor.py` and modify the `generate_response()` method:

```python
def generate_response(self, category: str, comment: str) -> Optional[str]:
    """Generate an auto-response for questions and praise."""
    if category == "question":
        # Custom logic based on comment keywords
        if "pricing" in comment.lower():
            return "Our pricing starts at $29/month. See www.example.com/pricing for details."
        elif "tutorial" in comment.lower():
            return "Check out our tutorial playlist: www.youtube.com/c/ConcessaObvius/playlists"
        else:
            return "Great question! We have more info in our docs: www.example.com/docs"
    
    elif category == "praise":
        return "Thank you! We're so glad you loved it. New videos coming soon!"
    
    return None
```

Then commit and push the updated script.

---

## Schedule Explanation

The schedule `*/30 * * * *` means:

- `*/30` — Every 30 minutes
- `*` — Every hour
- `*` — Every day
- `*` — Every month
- `*` — Every day of week

So the monitor runs at:
- 12:00 AM, 12:30 AM
- 1:00 AM, 1:30 AM
- 2:00 AM, 2:30 AM
- ... (every 30 minutes all day)

To change frequency:
- `0 * * * *` — Every hour at :00
- `0 9,14,18 * * *` — At 9 AM, 2 PM, 6 PM
- `0 0 * * *` — Once daily at midnight

---

## Next Steps

1. **Get YouTube API key** (see YOUTUBE_SETUP.md)
2. **Test the script** manually
3. **Set up cron** (system or OpenClaw)
4. **Monitor logs** for the first 24 hours
5. **Review flagged comments** regularly
6. **Customize responses** as needed

See `.cache/YOUTUBE_SETUP.md` for detailed setup instructions.
