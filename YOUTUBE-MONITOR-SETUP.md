# YouTube Comment Monitor Setup

**Channel:** Concessa Obvius  
**Frequency:** Every 30 minutes  
**Status:** Ready to deploy

---

## 📋 What This Does

Monitors the Concessa Obvius YouTube channel for new comments, automatically:

1. **Categorizes** each comment:
   - **Questions** — "How do I...?", "What is...?", pricing, timeline, tools
   - **Praise** — Inspiring, amazing, thank you, love this
   - **Spam** — Crypto, MLM, gambling, sketchy links
   - **Sales** — Partnerships, sponsorships, affiliate offers
   - **Other** — Doesn't match patterns

2. **Auto-responds** to Questions & Praise with templates
3. **Flags** Sales inquiries for manual review
4. **Logs** all activity to `.cache/youtube-comments.jsonl`
5. **Reports** summary stats (processed, auto-responded, flagged)

---

## 🔑 Setup: YouTube API Credentials

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (name it "Concessa YouTube Monitor")
3. Enable the **YouTube Data API v3**:
   - Search "YouTube Data API v3"
   - Click **Enable**

### Step 2: Create OAuth2 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth 2.0 Client ID**
3. Select **Desktop application**
4. Download the JSON file
5. Save it to: `~/.openclaw/youtube-credentials.json`

```bash
# Verify it's in place
ls -la ~/.openclaw/youtube-credentials.json
```

### Step 3: Install Python Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

---

## 🔄 Cron Setup (macOS)

### Option A: Using LaunchAgent (Recommended)

Create `~/Library/LaunchAgents/com.youtube-monitor.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.youtube-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/abundance/.openclaw/workspace/scripts/youtube-monitor.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>1800</integer>
    <!-- Run every 30 minutes (1800 seconds) -->
    <key>StandardOutPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor-error.log</string>
</dict>
</plist>
```

Then load it:

```bash
launchctl load ~/Library/LaunchAgents/com.youtube-monitor.plist
launchctl start com.youtube-monitor
```

### Option B: Using Cron

Add to crontab:

```bash
crontab -e
```

Add this line:

```
*/30 * * * * /Users/abundance/.openclaw/workspace/scripts/youtube-monitor.sh
```

---

## 📊 Files & Locations

| File | Purpose |
|------|---------|
| `scripts/youtube-comment-monitor.py` | Main monitoring script |
| `scripts/youtube-monitor.sh` | Cron wrapper (logging, error handling) |
| `.cache/youtube-comments.jsonl` | Log of all comments (JSONL format) |
| `.cache/youtube-monitor.log` | Execution log (one entry per run) |
| `~/.openclaw/youtube-credentials.json` | OAuth2 credentials (DO NOT COMMIT) |
| `~/.openclaw/youtube-token.json` | Refresh token (auto-created, DO NOT COMMIT) |

---

## 📝 Log Format

Each line in `youtube-comments.jsonl` is a JSON object:

```json
{
  "timestamp": "2026-04-14T08:30:00Z",
  "commenter": "John Doe",
  "text": "How do I get started with your system?",
  "category": "question",
  "response_status": "responded",
  "comment_id": "UgyABC..."
}
```

**response_status** values:
- `none` — Category 3 (spam) or 5 (other)
- `responded` — Auto-response sent
- `failed` — Attempted response but failed
- `flagged_for_review` — Category 4 (sales)

---

## 🎯 Workflow

### Initial Auth (First Run)

The first time you run the script, it will:

1. Prompt you to visit a URL and authorize
2. Save a refresh token to `~/.openclaw/youtube-token.json`
3. Proceed with monitoring

### Every 30 Minutes

The script:

1. ✅ Fetches recent comments from all videos on the channel
2. ✅ Checks against seen comments (no duplicates)
3. ✅ Categorizes each new comment
4. ✅ Auto-responds to questions/praise
5. ✅ Flags sales inquiries
6. ✅ Logs everything
7. ✅ Prints summary report

### Manual Reports

Generate a summary report:

```bash
python3 - <<'EOF'
import json
from pathlib import Path
from collections import Counter

log = Path(".cache/youtube-comments.jsonl")
data = [json.loads(line) for line in open(log) if line.strip()]

print(f"Total comments: {len(data)}")
print(f"By category: {dict(Counter(d['category'] for d in data))}")
print(f"Auto-responded: {sum(1 for d in data if d['response_status'] == 'responded')}")
print(f"Flagged for review: {sum(1 for d in data if d['response_status'] == 'flagged_for_review')}")
EOF
```

---

## 🛠️ Customization

### Change Auto-Response Templates

Edit `youtube-comment-monitor.py`:

```python
TEMPLATES = {
    "question": "Your custom question response here...",
    "praise": "Your custom praise response here...",
}
```

### Adjust Categorization Patterns

Add/modify patterns in the `PATTERNS` dict:

```python
PATTERNS = {
    "question": [
        r"how\s+(?:do|can)",
        r"custom_pattern_here",
    ],
    ...
}
```

### Change Check Frequency

Edit the LaunchAgent plist or cron:

- LaunchAgent: Change `<integer>1800</integer>` to seconds (e.g., 3600 = 1 hour)
- Cron: Change `*/30` to desired minutes

---

## ⚙️ Troubleshooting

### "Module not found: google"

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### "Credentials file not found"

Ensure `~/.openclaw/youtube-credentials.json` exists with valid OAuth2 credentials from Google Cloud Console.

### "Channel not found"

Verify the channel name in the script matches exactly. You can test:

```bash
python3 -c "
from youtube_comment_monitor import get_channel_id, authenticate_youtube
youtube = authenticate_youtube()
print(get_channel_id(youtube, 'Concessa Obvius'))
"
```

### Check Execution Log

```bash
tail -50 .cache/youtube-monitor.log
```

### Verify LaunchAgent Status

```bash
launchctl list | grep youtube-monitor
```

---

## 🔐 Security Notes

- **Never commit** `youtube-credentials.json` or `youtube-token.json`
- Credentials are stored locally in `~/.openclaw/`
- Token auto-refreshes; no manual intervention needed
- Monitor runs with your user permissions (no sudo needed)

---

## 📈 Next Steps

1. ✅ Save credentials to `~/.openclaw/youtube-credentials.json`
2. ✅ Run script once manually: `python3 scripts/youtube-comment-monitor.py`
3. ✅ Authorize via browser (one-time)
4. ✅ Verify `.cache/youtube-comments.jsonl` is populated
5. ✅ Set up LaunchAgent or cron for every 30 minutes
6. ✅ Check logs: `tail -f .cache/youtube-monitor.log`

---

**Status:** Ready. Configure credentials and schedule, then launch. 🚀
