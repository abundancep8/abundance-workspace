# YouTube Monitor — Next Steps

## ✅ Done
- [x] Created monitoring script (`.cache/youtube-monitor.py`)
- [x] Created cron wrapper (`.cache/youtube-monitor.sh`)
- [x] Created setup guide (`.cache/YOUTUBE_MONITOR_SETUP.md`)

## ⚠️ To Do

### 1. Get YouTube API Credentials
- [ ] Create Google Cloud Project
- [ ] Enable YouTube Data API v3
- [ ] Generate API Key
- [ ] Set environment variable: `export YOUTUBE_API_KEY="YOUR_KEY"`

### 2. Get Channel ID
- [ ] Find or set `YOUTUBE_CHANNEL_ID` for "Concessa Obvius"

### 3. Customize (Optional)
- [ ] Edit question response template in `.cache/youtube-monitor.py` (line ~30)
- [ ] Edit praise response template (same location)
- [ ] Adjust keyword lists if needed (line ~40)

### 4. Test
```bash
cd /Users/abundance/.openclaw/workspace
python3 .cache/youtube-monitor.py
```

### 5. Install Cron Job
```bash
chmod +x .cache/youtube-monitor.sh
crontab -e
# Add: */30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.sh >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log 2>&1
```

## 📋 Questions for You

Before I activate the cron job, I need:

1. **YouTube API Key** (from Google Cloud Console)
2. **Concessa Obvius Channel ID** (from the channel's About page or URL)
3. **Response Templates** — What exactly should the auto-replies say?
   - For questions (e.g., pointing to FAQ, tutorials, etc.)?
   - For praise (thank you message)?

Once you provide these, I'll:
- Update the script with your credentials
- Test it
- Set up the cron job to run every 30 minutes
- Show you how to monitor it

---

**Full guide:** See `.cache/YOUTUBE_MONITOR_SETUP.md`
