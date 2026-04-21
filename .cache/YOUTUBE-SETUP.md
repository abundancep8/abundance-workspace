# YouTube Comment Monitor Setup

## 🎯 What This Does

Monitors the **Concessa Obvius** YouTube channel every 30 minutes for new comments, categorizes them, auto-responds to some, and flags others for manual review.

**Categories:**
1. **Questions** — "How do I start?", "What tools?", "Cost?", "Timeline?" → Auto-responds with template
2. **Praise** — "Amazing!", "Inspiring", "Thank you!" → Auto-responds with appreciation
3. **Spam** — Crypto, MLM, forex, gambling → Logs, no response
4. **Sales** — Partnerships, collaborations, sponsorships → Flagged for review
5. **Neutral** — Default category

**Log Location:** `~/.openclaw/workspace/.cache/youtube-comments.jsonl`

Each line is a JSON object with: timestamp, commenter, text, category, response_status, response_text.

---

## 🔧 Setup Steps

### 1. Install Python Dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Set Up YouTube API Credentials

**Option A: Using Google Cloud Console (Full OAuth2)**

1. Go to https://console.cloud.google.com/
2. Create a new project: "YouTube Comment Monitor"
3. Enable **YouTube Data API v3**
4. Create an **OAuth 2.0 Client ID** (type: Desktop app)
5. Download the JSON and save to: `~/.config/youtube/credentials.json`
6. Run the monitor script once — it will prompt you to authorize and save a token

**Option B: Using API Key (Read-Only, Simpler)**

1. Create a new project in Google Cloud
2. Enable YouTube Data API v3
3. Create an **API Key** in the Credentials section
4. Set environment variable: `export YOUTUBE_API_KEY=your_key_here`
5. Modify the script to use the API key instead of OAuth2

### 3. Set the Channel ID

In `youtube-monitor.py`, find the line:
```python
CHANNEL_ID = None  # Will be resolved from channel name
```

Replace with your channel ID (search for "Concessa Obvius" on YouTube, then use `?channel=...` in the URL):
```python
CHANNEL_ID = "UCxxxxxxxxxxxxxxxxxxx"
```

Or leave as `None` and the script will resolve it automatically on first run.

### 4. Customize Response Templates (Optional)

Edit the `RESPONSES` dict in `youtube-monitor.py`:

```python
RESPONSES = {
    "questions": "Thank you for the question! {comment_preview} I'd recommend checking out [LINK]. DM for details.",
    "praise": "🙏 Thank you so much! We're thrilled to hear this. Keep building!",
}
```

---

## ⏰ Set Up Cron (Every 30 Minutes)

### macOS / Linux

```bash
# Edit crontab
crontab -e

# Add this line (runs at :00 and :30 of every hour):
*/30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh

# Save and exit (Ctrl+X, then Y in nano)
```

### Verify Cron is Active

```bash
# Check installed crons
crontab -l

# Monitor the log file
tail -f ~/.openclaw/workspace/.cache/monitor.log
```

---

## 📊 Monitor Output

Each run outputs JSON with stats:

```json
{
  "processed": 5,
  "auto_responses": 3,
  "flagged": 1,
  "by_category": {
    "questions": 2,
    "praise": 1,
    "spam": 1,
    "sales": 1
  }
}
```

### View All Comments Logged

```bash
# Pretty-print all logged comments
jq . ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Count by category
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Show flagged for review
jq 'select(.response_status == "flagged_for_review")' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

---

## 🔌 Integration Options

### Send Report to Discord
Add to cron script or create a separate webhook:

```bash
# After running monitor, send to Discord webhook
REPORT=$(python3 youtube-monitor.py | tail -1)
curl -X POST -H "Content-Type: application/json" \
  -d "{\"content\": \"YouTube Monitor Report: $REPORT\"}" \
  YOUR_DISCORD_WEBHOOK_URL
```

### Send Flagged Comments to Email
Add after processing:

```python
# In youtube-monitor.py, after categorization:
if category == "sales":
    send_email_notification(comment, category)
```

### Manual Review Dashboard

Check comments flagged for review:

```bash
jq 'select(.response_status == "flagged_for_review") | {timestamp, commenter, text}' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

---

## 🛠️ Troubleshooting

### "No module named google.auth"
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### "Credentials not found"
- Did you save credentials to `~/.config/youtube/credentials.json`?
- Run the script manually first to set up OAuth2: `python3 youtube-monitor.py`

### "Channel not found"
- Make sure CHANNEL_NAME matches exactly: "Concessa Obvius"
- Or set CHANNEL_ID manually in the script

### Cron not running
```bash
# Check system logs
log stream --level debug --predicate 'eventMessage contains "cron"'

# Test script directly
/Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh

# Check permissions
ls -la /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

---

## 📝 Next Steps

1. ✅ Install dependencies: `pip install google-auth-oauthlib ...`
2. ✅ Get YouTube API credentials
3. ✅ Update CHANNEL_ID in script
4. ✅ Test manually: `python3 youtube-monitor.py`
5. ✅ Add to crontab: `crontab -e`
6. ✅ Monitor output: `tail -f ~/.openclaw/workspace/.cache/monitor.log`

---

## 📚 Resources

- [YouTube Data API Docs](https://developers.google.com/youtube/v3)
- [OAuth 2.0 Setup](https://developers.google.com/identity/protocols/oauth2)
- [Cron Expression Reference](https://crontab.guru/)
- [jq Manual](https://stedolan.github.io/jq/manual/)
