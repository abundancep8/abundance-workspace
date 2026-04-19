# YouTube Comment Monitor Setup

**Status:** ✅ Scripts created | ⏳ Awaiting credentials and cron setup

## What's Running

The monitor is configured to run every 30 minutes and will:

1. **Fetch comments** from the Concessa Obvius channel
2. **Categorize** each comment:
   - ❓ **Questions** (how-to, cost, tools, timeline) → auto-reply with helpful template
   - 👍 **Praise** (amazing, inspiring, thank you) → auto-reply with gratitude
   - 🚩 **Spam** (crypto, MLM, get-rich schemes) → skip, no response
   - 🔗 **Sales/Partnerships** (collaboration, sponsorship) → flag for manual review
   - Other → logged but not responded to

3. **Log everything** to `.cache/youtube-comments.jsonl`:
   ```json
   {
     "timestamp": "2026-04-19T08:00:00Z",
     "comment_id": "...",
     "author": "John Doe",
     "text": "How do I get started?",
     "category": "question",
     "response_status": "auto_responded",
     "emoji": "❓"
   }
   ```

4. **Report metrics**:
   - Total comments processed
   - Auto-responses sent
   - Flagged for review

## Setup Required

### 1. Install Dependencies

```bash
pip install google-auth-oauthlib google-api-python-client
```

### 2. YouTube API Credentials

You need a service account or OAuth2 credentials from Google Cloud Console.

#### Option A: Service Account (Recommended for Automation)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable YouTube Data API v3
4. Create a **Service Account** (not OAuth client)
5. Download JSON credentials
6. Save to: `.secrets/youtube-credentials.json`

```bash
mkdir -p /Users/abundance/.openclaw/workspace/.secrets
# Place credentials.json here
```

**Note:** The service account email must be added as a manager to the YouTube channel, OR you need OAuth2 refresh tokens (more complex).

#### Option B: OAuth2 (If you own/manage the channel)

Use OAuth2 with refresh tokens. Requires interactive login once, then runs unattended.

### 3. Verify Channel Name

The monitor looks for "Concessa Obvius" by name. Verify this is the correct channel name on YouTube.

To use Channel ID instead, edit the script:
```python
CHANNEL_ID = "UCxxxxxxxxxxxxxx"  # Replace with actual ID
# Then modify get_channel_comments() to skip the channel lookup
```

### 4. Install Required Packages

```bash
cd /Users/abundance/.openclaw/workspace
python3 -m pip install google-auth-oauthlib google-api-python-client --user
```

### 5. Set Up Cron Job

Once credentials are in place:

```bash
# Add to crontab
crontab -e

# Add this line (runs every 30 minutes):
*/30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh >> /tmp/youtube-monitor.log 2>&1
```

Or use OpenClaw's built-in cron scheduling.

## Files

- **`youtube-monitor.py`** — Main monitoring script
- **`youtube-monitor-cron.sh`** — Wrapper for scheduled execution
- **`.cache/youtube-comments.jsonl`** — Log of all monitored comments
- **`.cache/youtube-monitor-state.json`** — Processed comment IDs (prevents duplicates)
- **`.cache/youtube-monitor-cron.log`** — Execution log (last 50 runs)

## Customization

### Auto-Response Templates

Edit `CATEGORY_TEMPLATES` in `youtube-monitor.py`:

```python
CATEGORY_TEMPLATES = {
    "question": {
        "keywords": ["how", "what", "cost", ...],
        "response": "Your custom response here..."
    },
    ...
}
```

### Comment Categorization

Add keywords or new categories as needed. Matching is case-insensitive.

### Rate Limiting

The script checks the last 5 videos to avoid YouTube API rate limits. Adjust if needed:
```python
for video_id in videos[:5]:  # Change 5 to desired limit
```

## Monitoring

Check execution logs:

```bash
tail -f /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.log
```

View processed comments:

```bash
tail -n 20 /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl
```

Check state (which comments have been processed):

```bash
cat /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-state.json | jq '.processed_ids | length'
```

## Troubleshooting

### "ERROR: Credentials file not found"
→ Create `.secrets/youtube-credentials.json` with YouTube API credentials

### "Cannot find channel 'Concessa Obvius'"
→ Verify the exact channel name, or use Channel ID instead

### "Permission denied: YouTube API"
→ Service account needs manager access to the channel, or use OAuth2 tokens

### "Rate limit exceeded"
→ Reduce the number of videos checked per run, or increase time between runs

---

**Next step:** Place your YouTube API credentials in `.secrets/youtube-credentials.json`, then I'll activate the cron job.
