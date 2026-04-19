# YouTube Comment Monitor – Quick Start

## ✅ What's Done

- [x] Main monitoring script: `youtube-monitor.py`
- [x] Cron wrapper: `youtube-monitor-cron.sh`
- [x] Dependencies installed
- [x] Initial state file created
- [x] Logging directory ready

## ⏳ What You Need (3 Steps)

### Step 1: Get YouTube API Credentials

You need ONE of these:

**Option A: Service Account (Simpler)**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create/select project → Enable YouTube Data API v3
3. Credentials → Create Service Account
4. Download JSON key
5. Save as: `/Users/abundance/.openclaw/workspace/.secrets/youtube-credentials.json`
6. Share channel with service account email as Manager

**Option B: OAuth2 (If you manage the channel)**
- Use existing OAuth2 tokens from your channel's auth flow

### Step 2: Create `.secrets` Directory

```bash
mkdir -p /Users/abundance/.openclaw/workspace/.secrets
# Then place credentials.json there
```

### Step 3: Activate Cron (Every 30 Minutes)

```bash
crontab -e
```

Add:
```
*/30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

Save & exit.

## 📋 What Happens Every 30 Minutes

1. **Fetch** new comments from Concessa Obvius
2. **Categorize**:
   - ❓ Questions → Auto-reply (helpful template)
   - 👍 Praise → Auto-reply (thanks template)
   - 🚩 Spam → Skip (no response)
   - 🔗 Sales → Flag for manual review
3. **Log** to `.cache/youtube-comments.jsonl` with timestamp, author, text, category, response status
4. **Report** metrics

## 📊 Monitoring

**Check latest runs:**
```bash
tail -50 /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.log
```

**View logged comments:**
```bash
tail -20 /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl | jq '.'
```

**Check state:**
```bash
cat /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-state.json | jq '.'
```

## 🎯 Metrics (After Each Run)

- Total comments processed
- Auto-responses sent
- Flagged for review
- Sample of recent comments

## 🔧 Customization

Edit `youtube-monitor.py` to:
- Change response templates (search `CATEGORY_TEMPLATES`)
- Add/remove category keywords
- Adjust how many videos are checked per run
- Change channel name or use Channel ID instead

## ❓ Common Issues

| Issue | Fix |
|-------|-----|
| "Credentials not found" | Place `.secrets/youtube-credentials.json` |
| "Cannot find channel" | Verify exact channel name in YouTube |
| "Permission denied" | Service account needs Manager access to channel |
| "Rate limit exceeded" | Check fewer videos per run (edit script) |

## 📂 Files

```
.cache/
  youtube-monitor.py                 # Main script
  youtube-monitor-cron.sh            # Cron wrapper
  youtube-monitor-state.json         # Tracking (processed IDs)
  youtube-monitor-cron.log           # Execution history
  youtube-comments.jsonl             # Comment log
  YOUTUBE_MONITOR_SETUP.md           # Full docs
  YOUTUBE_MONITOR_QUICK_START.md     # This file

.secrets/
  youtube-credentials.json           # (You need to create this)
```

---

**Ready?** Place your YouTube API credentials in `.secrets/youtube-credentials.json`, then set up the cron job above. The monitor will start running every 30 minutes.
