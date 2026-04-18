# YouTube Comment Monitor

Automated monitoring for the Concessa Obvius channel that:
- Fetches new comments every 30 minutes
- Categorizes comments (Questions, Praise, Spam, Sales)
- Auto-responds to Questions and Praise
- Flags Sales inquiries for human review
- Logs all activity to `youtube-comments.jsonl`

## Setup

### 1. Install Dependencies
```bash
pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Get YouTube API Credentials

You have two options:

#### Option A: API Key (Recommended for monitoring only)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "YouTube Data API v3"
4. Go to Credentials → Create API Key
5. Copy the key

Set environment variable:
```bash
export YOUTUBE_API_KEY="your-api-key-here"
echo 'export YOUTUBE_API_KEY="your-api-key-here"' >> ~/.zprofile
```

#### Option B: OAuth / Service Account (For posting comments)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create service account
3. Create and download JSON key
4. Enable YouTube Data API v3

Set environment variable:
```bash
export YOUTUBE_CREDENTIALS_JSON="/path/to/credentials.json"
echo 'export YOUTUBE_CREDENTIALS_JSON="/path/to/credentials.json"' >> ~/.zprofile
```

### 3. Configure Channel ID
```bash
export YOUTUBE_CHANNEL_ID="UCxxxxxxxxxxxxxx"
echo 'export YOUTUBE_CHANNEL_ID="UCxxxxxxxxxxxxxx"' >> ~/.zprofile
```

Or let the script auto-detect by channel name (slower).

### 4. Test the Script
```bash
cd ~/.openclaw/workspace/.cache
python3 youtube-comment-monitor.py
```

You should see:
```
[...] Starting YouTube comment monitor...
=== YouTube Comment Monitor Report ===
...
```

### 5. Set Up Cron Job

Edit your crontab:
```bash
crontab -e
```

Add this line to run every 30 minutes:
```
*/30 * * * * cd ~/.openclaw/workspace/.cache && python3 youtube-comment-monitor.py >> monitor.log 2>&1
```

To run at specific times only (e.g., 9 AM - 6 PM, weekdays):
```
*/30 9-18 * * 1-5 cd ~/.openclaw/workspace/.cache && python3 youtube-comment-monitor.py >> monitor.log 2>&1
```

### 6. Verify Cron Job
```bash
crontab -l | grep youtube
```

## Usage

### Run Monitor Manually
```bash
python3 youtube-comment-monitor.py
```

### Generate Report (last 24 hours)
```bash
python3 youtube-monitor-report.py
```

### Generate Report (last N hours)
```bash
python3 youtube-monitor-report.py 48  # Last 48 hours
```

### View Monitor Log
```bash
tail -f monitor.log
```

### View Comments Log
```bash
# Pretty-print last 10 comments
tail -10 youtube-comments.jsonl | python3 -m json.tool
```

## Configuration

### Response Templates
Edit the `TEMPLATES` dictionary in `youtube-comment-monitor.py`:

```python
TEMPLATES = {
    "question": "Your custom response...",
    "praise": "Your custom response..."
}
```

### Categorization Rules
Edit the `categorize_comment()` function to adjust:
- Keywords for each category
- Default category when unclear

### Files

| File | Purpose |
|------|---------|
| `youtube-comment-monitor.py` | Main monitoring script |
| `youtube-monitor-report.py` | Generate reports |
| `youtube-monitor-setup.sh` | Interactive setup |
| `youtube-comments.jsonl` | Comment log (auto-created) |
| `monitor.log` | Cron execution log |
| `.youtube-monitor-state.json` | Internal state (auto-created) |

## Data Structure

Each logged comment is a JSON object:

```json
{
  "id": "comment_thread_id",
  "commenter": "User Name",
  "text": "Comment text...",
  "timestamp": "2026-04-18T03:30:00Z",
  "author_channel_id": "UCxxxxxxxxxxxxxx",
  "reply_count": 0,
  "category": "question",
  "processed_at": "2026-04-18T03:30:15.123456Z",
  "response_status": "auto_responded"
}
```

Response statuses:
- `auto_responded` - Reply posted automatically
- `failed` - Failed to post reply
- `flagged_spam` - Spam detected
- `flagged_review` - Sales inquiry flagged for human review

## Troubleshooting

### "No new comments found"
- The channel might not have public comments
- API rate limit may have been reached
- Check that you're using the correct channel ID

### "Failed to authenticate"
- Verify your API key or credentials file is correct
- Check environment variables are set: `echo $YOUTUBE_API_KEY`
- Make sure the API is enabled in Google Cloud Console

### "Failed to post reply"
- If using API Key, you can't post comments (monitoring only)
- Switch to OAuth/Service Account credentials
- Make sure the service account has YouTube channel owner permissions

### Cron job not running
```bash
# Check cron logs
log stream --predicate 'process == "cron"' --level debug

# Verify cron job is installed
crontab -l

# Check the monitor.log for errors
tail -100 ~/.openclaw/workspace/.cache/monitor.log
```

## Rate Limits

YouTube API has quotas:
- Free tier: 10,000 units/day
- Each commentThreads.list: ~4 units
- Each comments.insert: ~50 units

With 30-minute intervals (48 checks/day):
- 48 × 4 = 192 units for fetching
- 48 × 10 auto-replies × 50 = 24,000 units for posting

**Recommendation:** Use read-only monitoring with API Key, handle responses manually or batch them.

## Support

If something breaks, check:
1. `monitor.log` for error messages
2. Environment variables are set
3. API key/credentials are valid
4. YouTube channel is public

---

**Updated:** 2026-04-18 03:30 UTC
