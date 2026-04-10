# YouTube Comment Monitor - Deployment (5 Minutes)

**Status:** System built and ready. Just need Google Cloud credentials.

---

## STEP 1: Google Cloud Setup (2 minutes)

Go to: https://console.cloud.google.com

1. **Create Project**
   - Name: `abundance-youtube-automation`

2. **Enable YouTube Data API v3**
   - Search: "YouTube Data API v3"
   - Click: ENABLE

3. **Create OAuth Credentials**
   - Go to: Credentials
   - Create: OAuth 2.0 Client ID
   - Type: Desktop application
   - Name: `Abundance YouTube Monitor`
   - Authorized redirect: `http://localhost:8080/`
   - Click: CREATE

4. **Download JSON**
   - Click: Download
   - Rename to: `youtube-credentials.json`
   - Save to: `~/.openclaw/workspace/.secrets/youtube-credentials.json`

---

## STEP 2: Authorize (1 minute, one-time)

Run in terminal:
```bash
cd ~/.openclaw/workspace
python3 youtube-api-auth.py
```

This will:
- Open your browser
- Ask you to sign in as Concessa Obvius
- Grant YouTube permissions
- Save token (secure, stored locally)

Done. Browser closes.

---

## STEP 3: Activate (automatic)

Cron job `youtube-comment-monitor` will run **every 30 minutes** and:
- ✅ Fetch new comments
- ✅ Auto-reply to 7 common categories
- ✅ Flag complex comments for review
- ✅ Log everything

---

## That's it.

**Total time:** 5 minutes (mostly clicking in Google Cloud)
**Setup required:** Once
**Ongoing:** Fully automatic

Let me know when credentials.json is in place.
