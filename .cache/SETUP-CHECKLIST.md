# YouTube Monitor - Setup Checklist

## Quick Start (5 minutes)

- [ ] **Option A: Use yt-dlp (no setup needed)**
  ```bash
  pip install yt-dlp
  python3 ~/.openclaw/workspace/.cache/youtube-monitor.py
  ```

- [ ] **Option B: Use YouTube API (recommended)**
  1. Get API key from Google Cloud Console
  2. Set: `export YOUTUBE_API_KEY="your-key"`
  3. Install: `pip install google-api-python-client google-auth-oauthlib`
  4. Run: `python3 ~/.openclaw/workspace/.cache/youtube-monitor.py`

## Verify Installation

```bash
# Test the monitor script
python3 ~/.openclaw/workspace/.cache/youtube-monitor.py

# Should output:
# ✓ No new comments found for Concessa Obvius
# OR
# 📊 YouTube Comment Monitor Report
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

```bash
# Test the report tool
python3 ~/.openclaw/workspace/.cache/youtube-report.py

# Should show statistics
```

## Cron Setup (Already Configured)

The cron job is set to run every 30 minutes via OpenClaw's scheduler (cron ID: `114e5c6d-ac8b-47ca-a695-79ac31b5c076`).

**Manual cron setup** (if not using OpenClaw):
```bash
crontab -e
# Add: */30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.sh >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log 2>&1
```

## Post-Setup

- [ ] **Customize channel** (if not Concessa Obvius):
  Edit `.cache/youtube-monitor.py` → Update `CHANNEL_NAME` and `CHANNEL_HANDLE`

- [ ] **Customize keywords** (optional):
  Edit `.cache/youtube-monitor.py` → `CATEGORIES` dict

- [ ] **Customize responses** (optional):
  Edit `.cache/youtube-monitor.py` → `TEMPLATES` dict

- [ ] **Monitor running smoothly**:
  ```bash
  # Check last run
  tail ~/.openclaw/workspace/.cache/youtube-monitor.log
  
  # Check state file
  cat ~/.openclaw/workspace/.cache/youtube-monitor-state.json | python3 -m json.tool
  ```

## Daily Tasks

- [ ] **Check for flagged comments:**
  ```bash
  python3 ~/.openclaw/workspace/.cache/youtube-report.py --flagged
  ```

- [ ] **View full report:**
  ```bash
  python3 ~/.openclaw/workspace/.cache/youtube-report.py
  ```

- [ ] **Manually respond** to flagged sales inquiries on YouTube

---

**Files created:**
- ✅ `youtube-monitor.py` - Main monitoring script
- ✅ `youtube-monitor.sh` - Cron wrapper
- ✅ `youtube-report.py` - Report & review tool
- ✅ `YOUTUBE-MONITOR.md` - Full documentation
- ✅ `youtube-monitor-state.json` - Tracking state (auto-created)
- ✅ `youtube-comments.jsonl` - Comment log (auto-created)

**All ready!** Monitor is scheduled and will run every 30 minutes.
