# 🎬 YouTube Comment Monitor - Complete Setup Summary

**Installed:** April 14, 2026 @ 7:30 AM (Pacific)  
**Channel:** Concessa Obvius  
**Monitor Interval:** Every 30 minutes  
**Status:** ✅ Ready (pending one-time authentication)

---

## 📋 Installation Complete

### What Was Installed

```
workspace/
├── scripts/
│   ├── youtube-comment-monitor.py       ✅ Main monitoring script
│   ├── youtube-setup-auth.py            ✅ Auth helper (run once)
│   └── youtube-monitor-cron.sh          ✅ Cron launcher
├── .cache/
│   ├── youtube-comments.jsonl           ✅ Comment log (auto-created)
│   ├── youtube-monitor.log              ✅ Run logs (auto-created)
│   ├── .youtube-monitor-state.json      ✅ State tracking (auto-created)
│   └── youtube-monitor-README.txt       ✅ Quick reference
├── .secrets/
│   ├── youtube-credentials.json         ✅ API credentials (exists)
│   └── youtube-token.json               ⚠️  Needs refresh
├── YOUTUBE-MONITOR-SETUP.md             ✅ Detailed guide
├── YOUTUBE-MONITOR-CRON-SETUP.md        ✅ Cron configuration
└── .youtube-monitor-manifest.json       ✅ Deployment manifest
```

---

## 🚀 Getting Started (3 Steps)

### Step 1: Authenticate (ONE TIME - 30 seconds)

Run this command on your Mac:

```bash
python3 ~/openclaw/workspace/scripts/youtube-setup-auth.py
```

**What happens:**
1. Opens your browser to Google OAuth
2. Asks permission to access your YouTube channel
3. Saves authentication token (valid 6+ months)
4. Confirms readiness

**Why needed:** The old OAuth token (from April 10) has expired.

---

### Step 2: Set Up Cron (Choose One Method)

Pick the method that works best for you:

#### 🟢 Method A: System Crontab (Recommended)
```bash
(crontab -l 2>/dev/null || echo "") | cat - << 'EOF' | crontab -
# YouTube Comment Monitor - Every 30 minutes
*/30 * * * * cd /Users/abundance/.openclaw/workspace && bash scripts/youtube-monitor-cron.sh >> .cache/youtube-monitor.log 2>&1
EOF
```

Verify:
```bash
crontab -l | grep youtube
```

#### 🟢 Method B: OpenClaw Native
```bash
openclaw cron add youtube-monitor "*/30 * * * *" "cd /Users/abundance/.openclaw/workspace && bash scripts/youtube-monitor-cron.sh"
```

#### 🟢 Method C: macOS LaunchAgent (Background)
See detailed instructions in: `YOUTUBE-MONITOR-CRON-SETUP.md`

---

### Step 3: Verify & Monitor

**Test it works:**
```bash
python3 ~/openclaw/workspace/scripts/youtube-comment-monitor.py
```

**Watch it run:**
```bash
tail -f ~/openclaw/workspace/.cache/youtube-monitor.log
```

**View comments as they arrive:**
```bash
tail -f ~/openclaw/workspace/.cache/youtube-comments.jsonl | jq .
```

---

## 📊 How It Works

### Every 30 Minutes:

1. **Fetch** new comments from Concessa Obvius channel
2. **Categorize** each comment:
   - 🤔 **Questions** → Auto-respond
   - 👏 **Praise** → Auto-respond
   - 🚫 **Spam** → Log only
   - 💼 **Sales** → Flag for review
   - 📝 **General** → Log only
3. **Log** all comments to `youtube-comments.jsonl`
4. **Track** state (processed IDs, last check time)
5. **Report** summary stats

### Example Report:

```
📊 YouTube Comment Monitor Report
Time: 2026-04-14 07:30:45 (Pacific)

📈 Statistics:
  • Total comments processed: 5
  • Auto-responses sent: 3
  • Flagged for review (sales): 1
  • Net logged: 1

🔄 Next check: In 30 minutes
```

---

## 🎯 Comment Categorization

| Category | Detection | Action | Notes |
|----------|-----------|--------|-------|
| **Questions** | how, what, help, cost, timeline, tools | Auto-respond | Helpful template reply |
| **Praise** | amazing, awesome, inspiring, thank you | Auto-respond | Gratitude template reply |
| **Spam** | crypto, mlm, forex, "click here" | Log only | No response sent |
| **Sales** | partnership, collaboration, sponsorship | Flag for review | Marked for manual handling |
| **General** | Everything else | Log only | No response sent |

---

## 📁 Key Files & Logs

### View Recent Comments
```bash
tail -20 .cache/youtube-comments.jsonl | jq .
```

### Find Flagged Sales
```bash
grep '"category": "sales"' .cache/youtube-comments.jsonl | jq .
```

### Check Auto-Responses Sent
```bash
grep '"response_status": "auto_replied"' .cache/youtube-comments.jsonl | wc -l
```

### View Monitor Status
```bash
tail -50 .cache/youtube-monitor.log
```

### Check State (What Was Processed)
```bash
cat .cache/.youtube-monitor-state.json | jq .
```

---

## 🔐 Credentials & Secrets

**Locations:**
- `~/.openclaw/workspace/.secrets/youtube-credentials.json` (Google OAuth app)
- `~/.openclaw/workspace/.secrets/youtube-token.json` (Active auth token)

**Security:**
- Credentials are stored locally, never sent to external servers
- Token automatically refreshes when needed
- Read-only file permissions (chmod 600)

**Troubleshooting:**
If you get auth errors, re-run:
```bash
python3 ~/openclaw/workspace/scripts/youtube-setup-auth.py
```

---

## 📈 Monitoring the Monitor

### Real-Time Dashboard
```bash
watch -n 5 'echo "=== LAST 10 RUNS ==="; tail -10 .cache/youtube-monitor.log; echo ""; echo "=== RECENT COMMENTS ==="; tail -3 .cache/youtube-comments.jsonl | jq .'
```

### Daily Stats
```bash
echo "Total comments today:"
grep "$(date +%Y-%m-%d)" .cache/youtube-comments.jsonl | wc -l

echo "Auto-responses sent:"
grep "$(date +%Y-%m-%d)" .cache/youtube-comments.jsonl | grep "auto_replied" | wc -l

echo "Flagged for review:"
grep "$(date +%Y-%m-%d)" .cache/youtube-comments.jsonl | grep "sales" | wc -l
```

### Check Cron Job Status (if using system cron)
```bash
# View crontab
crontab -l | grep youtube

# Check recent executions
log stream --predicate 'process == "cron"' --level debug | grep youtube

# Last 20 lines of log
tail -20 .cache/youtube-monitor.log
```

---

## 🛠️ Customization

### Edit Response Templates

File: `scripts/youtube-comment-monitor.py`

Find this section:
```python
RESPONSE_TEMPLATES = {
    "question": """Thanks for the question! 🎯
{question_summary}
For detailed answers, visit [YOUR LINK]
—Your Name""",
    
    "praise": """Thank you so much! 🙏
[Your custom message]
—Your Name""",
}
```

Edit the templates and save. Changes take effect on next run.

### Change Detection Keywords

In the same file, update the `PATTERNS` dictionary to detect different keywords or change sensitivity.

### Monitor Different Channel

Change this line:
```python
CHANNEL_NAME = "Concessa Obvius"  # ← Edit this
```

---

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| "invalid_client" auth error | Run: `python3 scripts/youtube-setup-auth.py` |
| Channel not found | Verify exact channel name matches |
| No comments processed | Check if channel has public comments on recent videos |
| Cron not running | Check: `crontab -l` or `log stream --predicate 'process == "cron"'` |
| Permission denied | Ensure script is executable: `chmod +x scripts/youtube-monitor-cron.sh` |
| Python library errors | Install: `pip3 install google-auth-oauthlib google-api-python-client` |

See detailed troubleshooting in: `YOUTUBE-MONITOR-SETUP.md`

---

## 📞 Quick Reference

### Essential Commands

```bash
# Authenticate (ONE TIME)
python3 ~/openclaw/workspace/scripts/youtube-setup-auth.py

# Run monitor manually
python3 ~/openclaw/workspace/scripts/youtube-comment-monitor.py

# Watch the logs
tail -f ~/openclaw/workspace/.cache/youtube-monitor.log

# View comments
tail -20 ~/openclaw/workspace/.cache/youtube-comments.jsonl | jq .

# Find sales comments
grep '"category": "sales"' ~/openclaw/workspace/.cache/youtube-comments.jsonl | jq .

# Count today's activity
grep "$(date +%Y-%m-%d)" ~/openclaw/workspace/.cache/youtube-comments.jsonl | jq -s 'group_by(.category) | map({category: .[0].category, count: length})'
```

---

## ✅ Checklist

Before the monitor starts running automatically:

- [ ] Run authentication: `python3 scripts/youtube-setup-auth.py`
- [ ] Test the monitor: `python3 scripts/youtube-comment-monitor.py`
- [ ] Set up cron (choose method A, B, or C)
- [ ] Verify cron is running: `crontab -l | grep youtube`
- [ ] Check logs: `tail -20 .cache/youtube-monitor.log`
- [ ] View a comment: `tail -1 .cache/youtube-comments.jsonl | jq .`

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `YOUTUBE-MONITOR-SETUP.md` | Detailed setup and configuration |
| `YOUTUBE-MONITOR-CRON-SETUP.md` | Cron job installation options |
| `.cache/youtube-monitor-README.txt` | Quick reference |
| `.youtube-monitor-manifest.json` | Deployment metadata |

---

## 🎉 You're Done!

Your YouTube comment monitor is ready to:
- ✅ Monitor Concessa Obvius channel 24/7
- ✅ Auto-respond to questions and praise
- ✅ Flag sales inquiries for review
- ✅ Log everything for analysis
- ✅ Run automatically every 30 minutes

**Next step:** Run the authentication command above, then choose your preferred cron setup.

Questions? Check the docs or review the logs in `.cache/youtube-monitor.log`.

---

**Installed:** 2026-04-14 14:30 UTC  
**System:** macOS (arm64) · Python 3.14 · YouTube Data API v3
