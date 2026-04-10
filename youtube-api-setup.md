# YouTube Data API v3 Setup
## For Concessa Obvius Channel Automation

**Channel:** Concessa Obvius (UC32674)
**Purpose:** Automated comment/DM responses

---

## QUICK SETUP (5 minutes)

### Step 1: Google Cloud Project
1. Go to https://console.cloud.google.com
2. Create new project: `abundance-youtube-automation`

### Step 2: Enable YouTube Data API v3
1. Search for "YouTube Data API v3"
2. Click ENABLE

### Step 3: Create OAuth 2.0 Credentials
1. Go to Credentials
2. Create Credentials → OAuth 2.0 Client ID
3. Application Type: Desktop application
4. Name: `Abundance YouTube Monitor`
5. Authorized redirect URIs: `http://localhost:8080/`
6. Download JSON file

### Step 4: Save Credentials
```
Place downloaded JSON at:
~/.openclaw/workspace/.secrets/youtube-credentials.json
```

### Step 5: One-Time Authorization
```bash
cd ~/.openclaw/workspace
python3 youtube-api-auth.py
```

This will:
- Open browser automatically
- Ask you to sign in as Concessa Obvius channel owner
- Grant permissions (read comments + send replies)
- Save token to `.secrets/youtube-token.json` (secure)

### Step 6: Activate Monitor
Once token is saved, the cron job will run automatically every 30 min.

---

## That's it. Done in 5 minutes.
