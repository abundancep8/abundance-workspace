# 🎬 YouTube Comment Monitor — Setup Checklist

## ✅ Pre-Deployment

- [ ] **Dependencies Installed**
  ```bash
  pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
  ```

- [ ] **API Credentials Obtained**
  - [ ] Choose auth method (API Key / OAuth 2.0 / Service Account)
  - [ ] Follow YOUTUBE-SETUP.md
  - [ ] Save credentials securely (NOT in git)

- [ ] **Configuration Updated**
  - [ ] Edit `youtube-monitor-config.json`
  - [ ] Set `channel_id` (format: `UCxxxxxxxxxx`)
  - [ ] Set `api_key` or `credentials_file`
  - [ ] Verify `auto_respond_enabled: true`

- [ ] **Response Templates Customized**
  - [ ] Review default templates
  - [ ] Update with your style/links
  - [ ] Test with sample comments

## 🧪 Testing

- [ ] **Manual Test Run**
  ```bash
  cd /Users/abundance/.openclaw/workspace
  python3 .cache/youtube-monitor-integrated.py --debug
  ```
  - [ ] No errors in output
  - [ ] See "Processed: N comments" (even if N=0 for new channels)
  - [ ] Log files created in `.cache/`

- [ ] **Verify Log Files Created**
  ```bash
  ls -la .cache/youtube-monitor-*
  ```
  - [ ] `youtube-comments.jsonl` exists
  - [ ] `youtube-monitor-stats.jsonl` exists
  - [ ] `youtube-monitor-state.json` exists

- [ ] **Check Log Format**
  ```bash
  # Should show valid JSON (or empty if no new comments)
  cat .cache/youtube-comments.jsonl | head -1 | jq .
  cat .cache/youtube-monitor-stats.jsonl | head -1 | jq .
  ```

## 🚀 Deployment

- [ ] **Deploy via OpenClaw Cron**
  - Cron ID: `114e5c6d-ac8b-47ca-a695-79ac31b5c076`
  - Interval: Every 30 minutes
  - Status: Ready to activate

- [ ] **Alternative: System Crontab (Optional)**
  ```bash
  crontab -e
  # Add: */30 * * * * cd /Users/abundance/.openclaw/workspace && /usr/bin/python3 .cache/youtube-monitor-integrated.py >> .cache/youtube-monitor.log 2>&1
  ```

- [ ] **Verify Permissions**
  ```bash
  chmod +x /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-integrated.py
  ls -la .cache/youtube-monitor-integrated.py
  ```

## 📊 Monitoring Setup

- [ ] **Monitor Stats Regularly**
  ```bash
  # View latest report
  tail -1 .cache/youtube-monitor-stats.jsonl | jq .
  
  # Or with timestamps
  jq -r '[.timestamp, "Processed: \(.total_processed)", "Auto-responses: \(.auto_responses_sent)", "Flagged: \(.flagged_for_review)"] | @csv' .cache/youtube-monitor-stats.jsonl
  ```

- [ ] **Set Up Log Rotation (Optional)**
  ```bash
  # Keep last 90 days of logs
  find .cache/youtube-*.jsonl -mtime +90 -delete
  ```

- [ ] **Create Alerts (Optional)**
  - [ ] Alert when `flagged_for_review` > 0
  - [ ] Daily summary of stats
  - [ ] Error notifications

## 🔒 Security Checklist

- [ ] **API Credentials Secure**
  - [ ] Keys NOT in git (`.cache/` is in `.gitignore`)
  - [ ] Keys NOT in code
  - [ ] Using environment variables or secure file storage
  - [ ] Credentials file permissions: `600`

- [ ] **Access Control**
  - [ ] Only you can read credentials
  - [ ] Script runs as your user (not root)
  - [ ] Log files not world-readable

- [ ] **Credential Rotation Plan**
  - [ ] Plan to rotate API keys quarterly
  - [ ] Document expiration dates
  - [ ] Test new credentials before disabling old ones

## 🎯 Post-Deployment

- [ ] **Monitor First 24 Hours**
  - [ ] Check logs every few hours
  - [ ] Verify auto-responses are posting correctly
  - [ ] Confirm state file is updating (last_checked)

- [ ] **Review Generated Responses**
  - [ ] Auto-responses read naturally
  - [ ] Links work correctly
  - [ ] Adjust templates if needed

- [ ] **Check Flagged Comments**
  ```bash
  grep '"flagged_for_review"' .cache/youtube-comments.jsonl | jq .
  ```
  - [ ] Sales inquiries are being caught
  - [ ] No false positives
  - [ ] Adjust patterns if needed

- [ ] **Test Category Detection**
  ```bash
  # View distribution
  jq -r '.by_category | to_entries | .[] | "\(.key): \(.value)"' .cache/youtube-monitor-stats.jsonl | sort | uniq -c
  ```

## 📋 Maintenance Tasks

**Weekly:**
- [ ] Review flagged comments
- [ ] Check error logs
- [ ] Verify monitor is running (check latest `youtube-monitor-stats.jsonl` timestamp)

**Monthly:**
- [ ] Review response templates
- [ ] Analyze comment patterns
- [ ] Adjust category patterns if needed

**Quarterly:**
- [ ] Rotate API credentials
- [ ] Review and archive old logs
- [ ] Update documentation

## 🆘 Troubleshooting

### Monitor Not Running?
- [ ] Check cron logs: `log stream --level debug | grep youtube`
- [ ] Verify Python is installed: `which python3`
- [ ] Check permissions: `ls -la .cache/youtube-monitor-integrated.py`
- [ ] Run manual test: `python3 .cache/youtube-monitor-integrated.py --debug`

### No Comments Being Fetched?
- [ ] Verify YouTube API is enabled in Google Cloud Console
- [ ] Check channel ID is correct
- [ ] Ensure API key is valid (test in API explorer)
- [ ] Check channel has recent videos with comments enabled

### Auto-Responses Not Posting?
- [ ] Using API key? It's read-only. Switch to OAuth 2.0 or Service Account.
- [ ] Check credentials have proper scopes: `youtube.force-ssl`
- [ ] Verify account is logged in and has channel access

### False Positives in Categorization?
- [ ] Review `CATEGORY_PATTERNS` in `youtube-monitor-integrated.py`
- [ ] Adjust regex patterns for your use case
- [ ] Add exclusion patterns as needed

---

## 📞 Quick Reference

| Issue | Solution |
|-------|----------|
| "API key invalid" | Check Google Cloud Console → YouTube API v3 enabled |
| "Channel not found" | Verify `channel_id` format: `UCxxxxxxxxxx` |
| "Permission denied" | Switch to OAuth 2.0 or Service Account credentials |
| "No comments fetched" | Manual test: `python3 .cache/youtube-monitor-integrated.py --debug` |

---

## ✨ When Everything Works

You should see:
- ✅ Monitor running every 30 minutes (check cron logs)
- ✅ New comments logged to `youtube-comments.jsonl`
- ✅ Stats recorded in `youtube-monitor-stats.jsonl`
- ✅ State updated with `last_checked` timestamp
- ✅ Auto-responses posted (check YouTube channel)
- ✅ Sales inquiries flagged for review

**Estimated time to full deployment: 30 minutes**

---

Last updated: 2026-04-16  
Status: Ready for deployment
