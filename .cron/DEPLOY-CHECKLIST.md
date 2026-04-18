# YouTube Comment Monitor - Deployment Checklist

## ✅ Pre-Deployment

- [x] Dependencies installed (google-auth-oauthlib, google-auth-httplib2, google-api-python-client)
- [x] YouTube credentials available (`.secrets/youtube-credentials.json`)
- [x] Credentials linked in workspace (symlink: `youtube_credentials.json`)
- [x] Token file location setup (symlink: `.cache/youtube_token.json`)
- [x] Monitor script ready (`.cron/youtube-comment-monitor.py`)
- [x] Report script ready (`.cron/youtube-report.py`)
- [x] `.cache` directory exists and writable

## 📋 Configuration Review

Review and confirm:

- [ ] `CHANNEL_HANDLE` is correct (currently: "ConcessaObvius")
- [ ] `RESPONSE_TEMPLATES` match your voice and style
- [ ] Category keywords in `categorize_comment()` are appropriate
- [ ] `.cache` permissions are correct (user can write)

## 🚀 Deployment Steps

1. **Test the script locally:**
   ```bash
   cd /Users/abundance/.openclaw/workspace
   python3 .cron/youtube-comment-monitor.py
   ```
   Expected output:
   - Authenticates with YouTube API
   - Fetches comments from channel
   - Reports: "Processed: X, Auto-responses sent: Y, Flagged: Z"

2. **Check the logs:**
   ```bash
   tail -50 .cache/youtube-comments.jsonl | jq .
   tail .cache/youtube-monitor.log
   ```

3. **Deploy to cron (every 30 minutes):**
   ```bash
   crontab -e
   ```
   Add this line:
   ```
   */30 * * * * cd /Users/abundance/.openclaw/workspace && python3 .cron/youtube-comment-monitor.py >> .cache/youtube-monitor.log 2>&1
   ```

4. **Verify cron is scheduled:**
   ```bash
   crontab -l | grep youtube
   ```

5. **Set up monitoring alerts (optional):**
   - Edit `.cron/youtube-comment-monitor-config.yaml` to enable Discord notifications on failure
   - Or check logs periodically: `tail .cache/youtube-monitor.log`

## 📊 Post-Deployment

Monitor these metrics:

- **Comments processed per cycle:** `.cache/youtube-comments.jsonl` line count
- **Auto-responses sent:** Check `response_status: "sent"`
- **Flagged for review:** Check `response_status: "flagged"`
- **Errors/logs:** `.cache/youtube-monitor.log`

Run reports:
```bash
python3 .cron/youtube-report.py  # Summary
tail -10 .cache/youtube-comments.jsonl | jq .  # Recent
```

## 🔍 Troubleshooting

If deployment fails:

1. **Check cron logs:**
   ```bash
   log stream --predicate 'process == "cron"' --level debug
   ```

2. **Run script manually:**
   ```bash
   cd /Users/abundance/.openclaw/workspace
   python3 .cron/youtube-comment-monitor.py 2>&1
   ```

3. **Verify credentials:**
   ```bash
   ls -la youtube_credentials.json .cache/youtube_token.json
   ```

4. **Check YouTube API quota:**
   - Go to: https://console.cloud.google.com/
   - Project: utopian-calling-492519-a3
   - Check YouTube Data API v3 quota

## 📈 Next: Enhancements

- [ ] Add AI-powered categorization (Claude API)
- [ ] Create Discord notifications for flagged comments
- [ ] Build comment sentiment analysis
- [ ] Generate weekly summaries
- [ ] Export reports to Google Sheets

---

**Status:** Ready for deployment ✅
**Last Updated:** 2026-04-17T19:30:00Z
**Maintained By:** YouTube Comment Monitor System
