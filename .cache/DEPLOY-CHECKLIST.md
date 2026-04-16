# Deployment Checklist - YouTube Comment Monitor

Use this to verify everything is set up correctly.

## Pre-Deployment ✅

- [ ] Python 3.6+ installed: `python3 --version`
- [ ] Dependencies installed: `pip list | grep google`
- [ ] YouTube API key obtained from Google Cloud Console
- [ ] API key added to environment: `echo $YOUTUBE_API_KEY`
- [ ] Scripts are executable: `ls -la .cache/youtube-monitor.*`

## Testing

- [ ] Manual test succeeds:
  ```bash
  python /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py
  ```
  Expected: "Found channel" + stats report

- [ ] Log file created:
  ```bash
  ls -la /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl
  ```

- [ ] State file created:
  ```bash
  cat /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-state.json
  ```

## Cron Setup

Choose ONE method:

### Method A: System Crontab
- [ ] Cron job added:
  ```bash
  crontab -l | grep youtube-monitor
  ```
- [ ] Test cron works:
  ```bash
  /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.sh
  ```

### Method B: OpenClaw Cron
- [ ] Job registered with OpenClaw
- [ ] Check status: `openclaw cron list`
- [ ] Watch logs: `openclaw cron logs youtube-comment-monitor`

## Post-Deployment

- [ ] Wait 30 minutes for first auto-run
- [ ] Check logs: `tail ~/.openclaw/workspace/.cache/youtube-monitor.log`
- [ ] Verify comments logged: `tail ~/.openclaw/workspace/.cache/youtube-comments.jsonl`
- [ ] Review categorization accuracy
- [ ] Test report stats match expected counts

## Ongoing

- [ ] Check logs weekly: `tail -30 youtube-monitor.log`
- [ ] Review flagged sales comments: `jq 'select(.response_status == "flagged_for_review")' youtube-comments.jsonl`
- [ ] Adjust patterns if miscategorization occurs
- [ ] Monitor API usage (included in Google Cloud Console)

---

## Rollback

If issues occur:

```bash
# Disable cron
crontab -e
# Comment out the youtube-monitor line

# Or with OpenClaw
openclaw cron delete youtube-comment-monitor

# Keep the logs and state
# You can re-enable anytime
```

## Success Criteria

✅ Script runs every 30 minutes  
✅ New comments appear in JSONL log within 32 minutes of being posted  
✅ Categories match expectations (spot-check 10 comments)  
✅ Sales comments flagged, not auto-replied  
✅ Zero errors in log file  

---

**Last Updated:** 2026-04-16  
**Status:** Ready for deployment
