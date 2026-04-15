# YouTube DM Monitor - Status & Activation Checklist

**Last Updated:** 2026-04-15 08:03 UTC  
**Status:** ✅ Ready for Activation  
**Channel:** Concessa Obvius  
**Schedule:** Every hour (configurable)

---

## What's Implemented ✅

### Core Features
- [x] **DM Categorization** - 4 categories: Setup Help, Newsletter, Product Inquiry, Partnership
- [x] **Auto-Response Templates** - Customizable responses for each category
- [x] **Logging** - JSONL format to `.cache/youtube-dms.jsonl`
- [x] **Partnership Flagging** - Intelligent detection of high-value partnerships
- [x] **Browser Automation** - Playwright-based YouTube Studio monitoring
- [x] **Deduplication** - Avoids processing same DM twice
- [x] **Reporting** - JSON reports + console summaries
- [x] **Cron Integration** - Hourly scheduler with error handling

### Support
- [x] Test mode for dry-run testing
- [x] Debug mode for troubleshooting
- [x] Comprehensive documentation
- [x] Detailed logging to `.cache/youtube-dm-monitor.log`
- [x] Discord webhook integration (optional)

---

## Activation Steps

### Step 1: Install Dependencies (2 min)

```bash
cd ~/.openclaw/workspace

# Option A: Virtual Environment (Recommended)
python3 -m venv venv
source venv/bin/activate
pip install playwright
python -m playwright install chromium

# Option B: User Install (If venv not available)
python3 -m pip install --user playwright
python3 -m playwright install
```

### Step 2: Verify Installation (1 min)

```bash
python3 youtube-dm-monitor-live.py --test
```

Expected output:
```
📊 YouTube DM Monitor - Test Mode

✓ Logged DM from Alice_Creator (setup_help)
✓ Logged DM from marketing_guy (partnership)
  🚩 FLAGGED
...
Total DMs: 4
Auto-responses: 4
```

✅ If this works, skip to Step 3

❌ If Playwright error: Re-run installation above

### Step 3: Customize Response Templates (5 min)

Edit `youtube-dm-templates.md` or directly in `youtube-dm-monitor-live.py`:

**File:** `youtube-dm-monitor-live.py` → Search for `TEMPLATES` dict

Example:
```python
TEMPLATES = {
    "setup_help": """Hey! 👋 Thanks for reaching out...
📚 Setup guide: https://yoursite.com/setup
...""",
    # Update others similarly
}
```

**Key fields to update:**
- Setup guide links
- Newsletter signup URL
- Product pricing page
- Partnership email address

### Step 4: Test with Real Channel (5 min)

```bash
# Run monitor in non-headless mode (see the browser)
python3 youtube-dm-monitor-live.py --headless=false --report
```

This will:
1. Open browser to YouTube Studio
2. Fetch real DMs from Concessa Obvius channel
3. Categorize them
4. Generate report

**First run may require:**
- YouTube login (if not cached)
- Accepting any browser permissions
- Confirming YouTube Studio access

### Step 5: Set Up Cron Scheduler (2 min)

**Option A: Cron (System)**

```bash
crontab -e
# Add this line (runs every hour at :00)
0 * * * * /Users/abundance/.openclaw/workspace/cron-youtube-dm-monitor-live.sh
```

**Option B: OpenClaw Native Cron** (if available)

```bash
# This command was already scheduled via OpenClaw
# To verify:
openclaw cron list | grep youtube
```

**Option C: LaunchD (macOS)**

Create `~/Library/LaunchAgents/com.concessa.youtube-monitor.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.concessa.youtube-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/abundance/.openclaw/workspace/cron-youtube-dm-monitor-live.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>StandardOutPath</key>
    <string>/Users/abundance/.cache/youtube-dm-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/abundance/.cache/youtube-dm-monitor.log</string>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.concessa.youtube-monitor.plist
```

### Step 6: Set Up Discord Webhook (Optional, 3 min)

To get hourly reports in Discord:

1. Go to your Discord server → Settings → Webhooks
2. Create new webhook (name: "YouTube DM Monitor")
3. Copy webhook URL
4. Add to shell environment:

```bash
export YOUTUBE_MONITOR_WEBHOOK="https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
```

Make it persistent:
```bash
echo 'export YOUTUBE_MONITOR_WEBHOOK="https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"' >> ~/.bash_profile
source ~/.bash_profile
```

Then test:
```bash
~/. openclaw/workspace/cron-youtube-dm-monitor-live.sh
# Should send a message to Discord
```

### Step 7: Monitor the Monitor (Ongoing)

**Check logs:**
```bash
tail -f ~/.cache/youtube-dm-monitor.log
```

**View recent DMs:**
```bash
tail -10 ~/.cache/youtube-dms.jsonl | jq '.'
```

**View flagged partnerships:**
```bash
grep '"interesting_partnership": true' ~/.cache/youtube-dms.jsonl | jq '.sender, .text'
```

**Generate daily report:**
```bash
python3 youtube-dm-monitor-live.py --report --hours 24
```

---

## Configuration Checklist

- [ ] Dependencies installed (Playwright)
- [ ] Test mode runs successfully
- [ ] Response templates customized
- [ ] Real DM fetch tested manually
- [ ] Cron scheduler activated
- [ ] Discord webhook configured (optional)
- [ ] Logs being written to `.cache/youtube-dms.jsonl`
- [ ] Reviewed first 24 hours of data

---

## Key Files

| File | Purpose |
|------|---------|
| `youtube-dm-monitor-live.py` | Main monitor script |
| `cron-youtube-dm-monitor-live.sh` | Cron launcher |
| `youtube-dm-templates.md` | Response template reference |
| `YOUTUBE-DM-MONITOR-SETUP.md` | Full documentation |
| `.cache/youtube-dms.jsonl` | All DM logs |
| `.cache/youtube-dm-report.json` | Latest report (JSON) |
| `.cache/youtube-dm-monitor.log` | Execution logs |

---

## Expected Behavior

### Hourly (Every 60 minutes)

1. Cron job triggers
2. Playwright opens YouTube Studio
3. Fetches unread DMs from Concessa Obvius
4. For each DM:
   - Categorizes (setup_help / newsletter / product_inquiry / partnership)
   - Logs to `.cache/youtube-dms.jsonl`
   - Marks for auto-response
   - Flags partnerships for review if interesting
5. Generates JSON report
6. (Optional) Sends summary to Discord
7. Logs execution details

### Example Output

```
[2026-04-15 09:03:42] =========================================
[2026-04-15 09:03:42] YouTube DM Monitor - Hourly Run
[2026-04-15 09:03:42] =========================================
[2026-04-15 09:03:42] Checking dependencies...
[2026-04-15 09:03:45] Starting DM monitor...
[2026-04-15 09:03:52] ✓ Navigated to YouTube Studio messages
[2026-04-15 09:03:55] ✓ Extracted 3 DMs from YouTube Studio
[2026-04-15 09:03:56] ✅ Processed 3 new DMs
  • alice_creator: setup_help
  • marketing_guy: partnership
    🚩 Flagged for manual review
  • subscriber_jane: newsletter

📊 REPORT SUMMARY
Total DMs: 3
Auto-responses sent: 3
Categories: {'setup_help': 1, 'partnership': 1, 'newsletter': 1}
Partnerships flagged: 1
Conversion potential: 0 product inquiries to follow up on

[2026-04-15 09:03:57] ✅ Completed at 2026-04-15 09:03:57
```

---

## Support & Debugging

### Enable Debug Mode

```bash
python3 youtube-dm-monitor-live.py --debug --report
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Playwright not installed" | Run `pip install playwright && python -m playwright install` |
| "Can't find DMs" | Check YouTube browser session, may need manual login first |
| "DM list empty" | Verify DMs exist in YouTube Studio, check channel access |
| "Cron not running" | Check crontab: `crontab -l`, verify script is executable: `chmod +x` |
| "Discord webhook fails" | Verify webhook URL, test with curl |

### Get Help

1. Check logs: `tail -50 ~/.cache/youtube-dm-monitor.log`
2. Run in debug mode: `python3 youtube-dm-monitor-live.py --debug`
3. Test manually: `python3 youtube-dm-monitor-live.py --test`
4. View setup guide: `cat YOUTUBE-DM-MONITOR-SETUP.md`

---

## Next Steps

1. **Right now:** Run `python3 youtube-dm-monitor-live.py --test` to verify
2. **Next 5 min:** Update response templates with your actual links/emails
3. **Next 30 min:** Activate cron scheduler
4. **Today:** Monitor first batch manually, review flagged partnerships
5. **Tomorrow:** Set up Discord webhook for automatic reporting

---

**Ready to activate? Start with Step 1 above!** 🚀
