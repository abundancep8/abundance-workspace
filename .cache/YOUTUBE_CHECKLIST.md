# YouTube Monitor Setup Checklist

Follow these steps to get the comment monitor running.

## Phase 1: Google Cloud Setup (15 min)

- [ ] Go to https://console.cloud.google.com/
- [ ] Create a new project (name: "YouTube Comment Monitor")
- [ ] Search for "YouTube Data API v3" and enable it
- [ ] Go to "Credentials" → "Create Credentials"
- [ ] Select "Service Account"
- [ ] Fill in service account details (any name is fine)
- [ ] Grant role: "Editor" (or "YouTube Data API") 
- [ ] Click "Done"
- [ ] Go to "Service Accounts" tab
- [ ] Click on your new service account
- [ ] Go to "Keys" tab → "Add Key" → "Create new key"
- [ ] Choose "JSON" format
- [ ] Save the file as: `~/.openclaw/credentials/youtube.json`
- [ ] Set permissions: `chmod 600 ~/.openclaw/credentials/youtube.json`

## Phase 2: Local Setup (10 min)

- [ ] Install Python dependencies:
  ```bash
  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
  ```

- [ ] Get your YouTube channel ID:
  - Go to your YouTube channel
  - Copy from URL: `youtube.com/c/YOUR_CHANNEL_ID`
  - Or YouTube Studio → Details → Channel ID

- [ ] Set environment variable:
  ```bash
  export YOUTUBE_CHANNEL="UCxxxxxxxxxxxxxxx"
  ```

- [ ] Add to shell profile (`.bashrc`, `.zshrc`, etc.):
  ```bash
  export YOUTUBE_CREDS_FILE="$HOME/.openclaw/credentials/youtube.json"
  export YOUTUBE_CHANNEL="UCxxxxxxxxxxxxxxx"
  ```

- [ ] Verify Python script is executable:
  ```bash
  ls -l .cache/youtube-monitor.py
  # Should show: -rwxr-xr-x
  ```

## Phase 3: Test Script (5 min)

- [ ] Run the monitor manually:
  ```bash
  cd /Users/abundance/.openclaw/workspace
  python .cache/youtube-monitor.py
  ```

- [ ] Check output:
  - Should show report with comment count
  - Should create `.cache/youtube-comments.jsonl` file
  - Should create `.cache/youtube-monitor.log` file

- [ ] View results:
  ```bash
  python .cache/youtube-report.py --summary
  tail .cache/youtube-comments.jsonl | jq .
  ```

## Phase 4: Enable Cron (5 min)

Choose ONE approach:

### Option A: System Crontab (Recommended)
```bash
# Edit crontab
crontab -e

# Add this line (paste at the end):
*/30 * * * * cd /Users/abundance/.openclaw/workspace && \
  python .cache/youtube-monitor.py >> .cache/youtube-cron.log 2>&1
```

- [ ] Crontab entry added
- [ ] Verify: `crontab -l | grep youtube`
- [ ] Check log after 30 minutes: `tail -f .cache/youtube-cron.log`

### Option B: OpenClaw Native Cron (When Available)
```bash
openclaw cron add .cache/cron-youtube-monitor.json
openclaw cron enable youtube-comment-monitor
```

- [ ] Cron job registered
- [ ] Verify: `openclaw cron list`

## Phase 5: Customization (Optional)

- [ ] Edit response templates in `youtube-monitor.py`
  - Customize the strings in `generate_response()` function
  - Add your FAQ URL or help resource link
  - Personalize the tone

- [ ] Review categorization rules (in `categorize_comment()`)
  - Adjust keywords for your channel type
  - Add/remove spam patterns
  - Fine-tune question detection

- [ ] Set up reporting schedule:
  - Decide when to review flagged comments (weekly?)
  - Add calendar reminder to check `--flagged` report

## Phase 6: Ongoing Maintenance

- [ ] **Weekly:** Review flagged comments
  ```bash
  python .cache/youtube-report.py --flagged
  ```

- [ ] **Monthly:** Check overall stats
  ```bash
  python .cache/youtube-report.py --stats
  ```

- [ ] **Quarterly:** Review and update categorization rules

- [ ] **Watch:** YouTube API quota at Google Cloud Console

## Verification Checklist

After setup, verify everything works:

```bash
# 1. Credentials file exists
ls -l ~/.openclaw/credentials/youtube.json

# 2. Python can import required libraries
python -c "import google.oauth2.service_account; print('✓ Google libs OK')"

# 3. Script is executable
test -x .cache/youtube-monitor.py && echo "✓ Script is executable"

# 4. Environment variable set
echo $YOUTUBE_CHANNEL

# 5. Crontab entry exists
crontab -l | grep youtube

# 6. Log files are writable
touch .cache/test.log && rm .cache/test.log && echo "✓ Log dir is writable"
```

## Status

- **Completed Phase:** _____ / 6
- **Estimated time:** 45 minutes total
- **Support:** See `YOUTUBE_README.md` for troubleshooting

---

Once this checklist is complete, your YouTube comment monitor will run automatically every 30 minutes and log all comments with automatic responses to questions and praise! 🚀
