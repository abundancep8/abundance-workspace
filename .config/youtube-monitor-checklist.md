# YouTube Monitor Setup Checklist

## ☐ Pre-Setup (5 min)

- [ ] Have a browser ready (for OAuth login)
- [ ] Know your YouTube channel (Concessa Obvius)

## ☐ Step 1: Get API Credentials (15 min)

1. [ ] Go to https://console.cloud.google.com/
2. [ ] Create or select a project
3. [ ] Enable YouTube Data API v3
4. [ ] Create OAuth 2.0 Client ID (Desktop app)
5. [ ] Download JSON file
6. [ ] Save to: `.secrets/youtube-credentials.json`

## ☐ Step 2: Run Setup (5 min)

```bash
cd /Users/abundance/.openclaw/workspace
./scripts/youtube-monitor-setup.sh
```

This will:
- ✓ Check credentials
- ✓ Install Python dependencies
- ✓ Authenticate (browser login)
- ✓ Create config file
- ✓ Run initial test

## ☐ Step 3: Set Up Cron (2 min)

```bash
crontab -e
```

Add this line:
```
*/30 * * * * /usr/bin/python3 /Users/abundance/.openclaw/workspace/scripts/youtube-monitor.py >> /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log 2>&1
```

Save and exit.

Verify:
```bash
crontab -l | grep youtube-monitor
```

## ☐ Post-Setup Validation (5 min)

- [ ] Run manual test: `python3 scripts/youtube-monitor.py`
- [ ] Check for JSONL log: `.cache/youtube-comments.jsonl`
- [ ] Verify cron is scheduled: `crontab -l`
- [ ] Check first run output in: `.cache/youtube-monitor.log`

## ✅ Done!

Monitor is now running every 30 minutes.

**Useful commands:**

```bash
# View real-time logs
tail -f .cache/youtube-monitor.log

# Check latest comments
tail -5 .cache/youtube-comments.jsonl | jq .

# Find flagged comments (sales)
grep "flagged_review" .cache/youtube-comments.jsonl | jq .

# View configuration
cat .config/youtube-monitor.json | jq .

# Stop monitoring (remove from crontab)
crontab -e  # and delete the line
```

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "credentials.json not found" | Download from Google Cloud Console and save to `.secrets/youtube-credentials.json` |
| "OAuth token expired" | Delete `.secrets/youtube-token.json` and run setup again |
| "No comments found" | Verify channel ID in `.config/youtube-monitor.json` |
| Cron not running | Check crontab: `crontab -l` and check logs: `tail .cache/youtube-monitor.log` |

---

**📖 Full docs:** See `docs/YOUTUBE-MONITOR.md`
