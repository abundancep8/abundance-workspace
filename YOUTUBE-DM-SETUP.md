# YouTube DM Monitor Setup

## Current Status: ⚠️ Awaiting Authentication

The YouTube DM monitoring system is configured but requires OAuth credentials to authenticate with the YouTube API.

## What's Ready

✅ **Monitor Script:** `youtube-dm-monitor-api.py`
- Monitors Concessa Obvius (@UC32674) for new DMs
- Categorizes messages into 4 types:
  1. **Setup Help** — "How to", tutorials, getting started questions
  2. **Newsletter** — Email list requests, update subscriptions
  3. **Product Inquiry** — Purchase interest, pricing questions
  4. **Partnership** — Collaboration, sponsorship, brand deals

✅ **Auto-Response Templates** — Ready to send category-specific replies
✅ **Logging System** — All DMs logged to `.cache/youtube-dms.jsonl` with:
- Timestamp, sender, text, category, response sent
- Conversion tracking for product inquiries
- Partnership flags for manual review

✅ **Reporting** — Generates summary:
- Total DMs processed
- Auto-responses sent
- Conversion opportunities
- Flagged partnerships

## What's Needed: YouTube OAuth Setup

### Step 1: Enable YouTube API
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable YouTube Data API v3
4. Create OAuth 2.0 Credentials (Desktop app)
5. Download credentials JSON file

### Step 2: Authenticate
```bash
# Run authentication script (to be created)
python3 youtube-api-auth.py
```

This will:
- Open browser for OAuth consent
- Save token to `.secrets/youtube-token.json`
- Test channel access

### Step 3: Start Monitoring
```bash
# Run monitor (setup as cron job)
python3 youtube-dm-monitor-api.py
```

## Cron Job Command

```
0 * * * * cd /Users/abundance/.openclaw/workspace && python3 youtube-dm-monitor-api.py >> .cache/youtube-dm-monitor.log 2>&1
```

This runs the monitor every hour and logs output.

## Log Files

- **DM Log:** `.cache/youtube-dms.jsonl` (one JSON object per line)
- **State:** `.cache/youtube-dms-state.json` (tracks last processed DM)
- **Monitor Log:** `.cache/youtube-dm-monitor.log` (stdout/stderr)

## Example Log Entry

```json
{
  "timestamp": "2026-04-10T09:15:00-07:00",
  "dm_id": "abc123",
  "created_at": "2026-04-10T08:45:00Z",
  "sender": "Creator Name",
  "sender_id": "UCxxxxxxx",
  "text": "How do I get started with your system?",
  "category": "setup_help",
  "auto_response_sent": true,
  "response_template": "Hey! Great question...",
  "flagged_for_review": false
}
```

## Next Actions

1. Set up YouTube OAuth credentials
2. Run `youtube-api-auth.py` to authenticate
3. Test monitor manually: `python3 youtube-dm-monitor-api.py`
4. Add to cron if working: `crontab -e`

---

**Note:** YouTube API DM sending has limitations. Current setup queues auto-responses for logging; actual DM replies may require manual YouTube Studio or alternative API method.
