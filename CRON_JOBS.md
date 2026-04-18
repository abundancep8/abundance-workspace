# Scheduled Cron Jobs

## YouTube Comment Monitor (Every 30 minutes)

**Status:** ✅ Configured  
**Script:** `.cache/youtube-comment-monitor.py`  
**Cron Entry:** `*/30 * * * * ~/.openclaw/workspace/.cache/youtube-monitor-cron.sh`  

### What it does:
- Monitors **Concessa Obvius** YouTube channel for new comments
- Categorizes each comment:
  - **Questions** (how-to, tools, cost, timeline) → Auto-responds
  - **Praise** (amazing, inspiring) → Auto-responds
  - **Spam** (crypto, MLM, scams) → Logged only
  - **Sales** (partnerships, collaborations) → Flagged for review
- Logs all comments to `.cache/youtube-comments.jsonl` with:
  - Timestamp
  - Commenter name
  - Comment text
  - Category
  - Response status

### Outputs:
- **Log file:** `.cache/monitor.log` (cron execution logs)
- **Comments database:** `.cache/youtube-comments.jsonl` (all comments with metadata)
- **Console report:** Total processed, auto-responses sent, flagged for review

### Setup Required:

1. **Install dependencies:**
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client anthropic
   ```

2. **Configure YouTube API:**
   - [Google Cloud Console](https://console.cloud.google.com) → Create project
   - Enable YouTube Data API v3
   - Create OAuth 2.0 Desktop credentials
   - Download JSON → `~/.openclaw/workspace/.cache/youtube-credentials.json`

3. **First run (to authenticate):**
   ```bash
   python ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
   ```
   This will open a browser for YouTube OAuth login and save the token.

4. **Add to crontab:**
   ```bash
   crontab -e
   # Add: */30 * * * * ~/.openclaw/workspace/.cache/youtube-monitor-cron.sh
   ```

### Customization:

Edit `youtube-comment-monitor.py` to:
- Modify response templates (lines 68-71)
- Add/change category keywords (lines 57-67)
- Change monitoring window (default: past 1 hour)
- Change response behavior for specific categories

### Monitoring:

```bash
# Live monitoring
tail -f ~/.openclaw/workspace/.cache/monitor.log

# View all comments
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Filter by category
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq 'select(.category=="sales")'

# Count by category
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq -r .category | sort | uniq -c

# Find flagged for review
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq 'select(.response_status=="flagged_for_review")'
```

---

**Created:** 2026-04-18  
**Next step:** Follow setup steps 1-4 to activate monitoring
