# YouTube Comment Monitor - Authentication Setup

## OAuth 2.0 Setup (Recommended)

### Step 1: Enable YouTube Data API

1. Go to [Google Cloud Console](https://console.developers.google.com)
2. Create a new project (or select existing)
3. Search for "YouTube Data API v3"
4. Click **Enable**

### Step 2: Create OAuth 2.0 Credentials

1. In Cloud Console, go to **Credentials** (left sidebar)
2. Click **Create Credentials** → **OAuth 2.0 Client ID**
3. Choose **Desktop application**
4. Click **Create**
5. Download the JSON file

### Step 3: Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 4: Configure Monitor

```bash
cd ~/.openclaw/workspace/.cache
python3 youtube_monitor.py --setup-auth
```

When prompted, paste the path to your downloaded `credentials.json`.

The script will save it as `youtube-credentials.json` and create `youtube-token.pickle` on first auth.

---

## Running the Monitor

### Single Run

```bash
python3 ~/.openclaw/workspace/.cache/youtube_monitor.py
```

### Generate Report

```bash
python3 ~/.openclaw/workspace/.cache/youtube_monitor.py --report
```

### Scheduled (Every 30 Minutes)

See `CRON_CONFIG.sh` for cron setup.

---

## Credential Storage

- **Credentials File:** `~/.openclaw/workspace/.cache/youtube-credentials.json`
- **Token File:** `~/.openclaw/workspace/.cache/youtube-token.pickle` (auto-created on first run)
- **State File:** `~/.openclaw/workspace/.cache/youtube-monitor-state.json` (tracks processed comments)
- **Log File:** `~/.openclaw/workspace/.cache/youtube-comments.jsonl` (all comments)

---

## Troubleshooting

### "Credentials file not found"

Run `python3 youtube_monitor.py --setup-auth` again.

### "Authentication failed"

- Ensure API is enabled in Cloud Console
- Delete `youtube-token.pickle` and re-authenticate
- Check that credentials.json is valid JSON

### "Channel not found"

- Verify "Concessa Obvius" is the exact channel name
- Edit `youtube_monitor.py` line ~47 to set correct channel name

### "No comments fetched"

- Check channel has public comments
- Verify API quota is not exceeded (YouTube Data API has 10,000 units/day)
