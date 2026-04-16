# YouTube DM Monitor - Live Activation Guide

**Status:** ✅ **READY TO RUN**  
**Channel:** Concessa Obvius  
**Setup Date:** 2026-04-15 03:04 UTC  
**Venv Location:** `~/.openclaw/workspace/venv`

---

## ✅ What's Ready

- [x] **Monitor Script:** `youtube-dm-monitor-live.py` — Fully functional
- [x] **Virtual Environment:** Created and dependencies installed
- [x] **Cron Launcher:** `cron-youtube-dm-monitor-live.sh` — Ready to schedule
- [x] **Test Mode:** Passes all tests
- [x] **DM Categories:** Setup Help, Newsletter, Product Inquiry, Partnership
- [x] **Auto-Response Templates:** Customizable responses for all categories
- [x] **Logging:** `.cache/youtube-dms.jsonl` (JSONL format)
- [x] **Reporting:** JSON + console summaries

---

## 🚀 Quick Start (Next 5 Minutes)

### Step 1: Test the Monitor (30 seconds)

```bash
cd ~/.openclaw/workspace
source venv/bin/activate
python3 youtube-dm-monitor-live.py --test --report
```

**Expected output:**
```
📊 YouTube DM Monitor - Test Mode
✅ Test DMs logged successfully
📈 REPORT
Total DMs: 8
Auto-responses: 8
Partnerships flagged: 1
Conversion potential: 2 product inquiries to follow up on
```

✅ If you see this, skip to Step 2.

### Step 2: Customize Response Templates (2 minutes)

Edit the response templates in `youtube-dm-monitor-live.py`:

1. Open the file:
   ```bash
   nano ~/.openclaw/workspace/youtube-dm-monitor-live.py
   ```

2. Find the `TEMPLATES` dictionary (around line 30)

3. Update each template with your actual links:

   ```python
   TEMPLATES = {
       "setup_help": """Hey! 👋 Thanks for reaching out about setup.
📚 Full setup guide: [YOUR_SETUP_URL]
🎥 Video tutorial: [YOUR_VIDEO_URL]
💬 FAQ: [YOUR_FAQ_URL]
Reply with what you're stuck on!""",

       "newsletter": """Thanks for the interest! 🔔
✉️ Join our newsletter: [YOUR_NEWSLETTER_URL]
You'll get:
- Weekly tips & updates
- Early feature access
- Member-only content
See you there!""",

       "product_inquiry": """Great question! 🎯
📦 Product info: [YOUR_PRICING_PAGE]
💰 We have options for every budget
❓ Help me find the right fit:
- What's your use case?
- Budget range?
- Team size?""",

       "partnership": """Ooh, interesting! 🤝 Love partnership ideas.
For collab/sponsorship, let's email:
📧 [partnership@concessa.com]
Tell me what you have in mind!"""
   }
   ```

4. Save (Ctrl+X, Y, Enter if using nano)

### Step 3: Schedule the Monitor (3 minutes)

Choose **ONE** of these options:

#### **Option A: System Cron (Recommended)**

Check if cron is available on your system:
```bash
crontab -l
```

If no permission error, set up hourly runs:

```bash
# Edit your crontab
crontab -e

# Add this line (runs at top of every hour):
0 * * * * /Users/abundance/.openclaw/workspace/cron-youtube-dm-monitor-live.sh >> ~/.cache/youtube-dm-monitor-cron.log 2>&1
```

**Verify it's installed:**
```bash
crontab -l | grep youtube
```

---

#### **Option B: macOS LaunchD (If cron needs permissions)**

1. Create the LaunchD plist:

```bash
cat > ~/Library/LaunchAgents/com.concessa.youtube-dm-monitor.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.concessa.youtube-dm-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/abundance/.openclaw/workspace/cron-youtube-dm-monitor-live.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>StandardOutPath</key>
    <string>/Users/abundance/.cache/youtube-dm-monitor-cron.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/abundance/.cache/youtube-dm-monitor-cron.log</string>
</dict>
</plist>
EOF
```

2. Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.concessa.youtube-dm-monitor.plist
```

3. Verify it's running:
```bash
launchctl list | grep youtube
```

---

#### **Option C: Manual Runs (Testing)**

If you want to test without cron, run manually anytime:

```bash
cd ~/.openclaw/workspace
source venv/bin/activate
python3 youtube-dm-monitor-live.py --report
```

---

## 📊 Monitor Your Monitor

### Check Logs

```bash
# Real-time logs
tail -f ~/.cache/youtube-dm-monitor-cron.log

# Last 50 lines
tail -50 ~/.cache/youtube-dm-monitor-cron.log

# All DMs processed (JSONL format)
cat ~/.cache/youtube-dms.jsonl | jq '.'

# Just the last 5 DMs
tail -5 ~/.cache/youtube-dms.jsonl | jq '.'
```

### View Reports

```bash
# Latest JSON report
cat ~/.cache/youtube-dm-report.json | jq '.'

# Just partnership flags
grep '"interesting_partnership": true' ~/.cache/youtube-dms.jsonl | jq '.sender, .text'

# Product inquiries only
grep '"category": "product_inquiry"' ~/.cache/youtube-dms.jsonl | jq '.sender, .text'
```

### Generate Custom Reports

```bash
# Last 24 hours
python3 youtube-dm-monitor-live.py --report --hours 24

# Last 7 days
python3 youtube-dm-monitor-live.py --report --hours 168

# With debug output
python3 youtube-dm-monitor-live.py --debug --report
```

---

## 🔗 Optional: Discord Webhook Integration

To get hourly reports in Discord:

1. Go to your Discord server → Channel Settings → Integrations → Webhooks
2. Create a new webhook (name: "YouTube DM Monitor")
3. Copy the webhook URL
4. Add to your shell profile:

```bash
echo 'export YOUTUBE_MONITOR_WEBHOOK="https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"' >> ~/.zshrc
source ~/.zshrc
```

5. Test it:
```bash
./cron-youtube-dm-monitor-live.sh
# Should see a message in Discord within 10 seconds
```

---

## 📋 DM Categorization Logic

The monitor automatically categorizes DMs based on keywords:

### 1. **Setup Help**
Keywords: setup, how to, confused, beginner, tutorial, install, getting started, help, guide, stuck, error, not working

Example: "Hey, I'm trying to set up but I'm confused on step 3"
→ Auto-response with setup guide link

### 2. **Newsletter**
Keywords: newsletter, updates, email list, subscribe, news, latest, stay updated, sign up

Example: "Can I get on your mailing list?"
→ Auto-response with newsletter signup link

### 3. **Product Inquiry**
Keywords: buy, pricing, price, cost, purchase, how much, product, which version, recommend, features, plan

Example: "What's your pricing and which plan is best for a team of 5?"
→ Auto-response with pricing page link + follow-up

### 4. **Partnership**
Keywords: collaborate, sponsorship, partner, joint, co-brand, affiliate, promotion, work together, business opportunity

Example: "We'd love to collaborate on a sponsorship"
→ Auto-response + **🚩 FLAGGED** for manual review

---

## 📈 What Gets Logged (Example)

Each DM is logged to `.cache/youtube-dms.jsonl` as:

```json
{
  "timestamp": "2026-04-15T03:05:22.123456",
  "sender": "alice_creator",
  "sender_id": "UCxxxx1234",
  "text": "Hey! How do I get started with your product?",
  "category": "setup_help",
  "response_sent": "Hey! 👋 Thanks for reaching out about setup...",
  "interesting_partnership": false,
  "raw_dm_id": "msg_abc123"
}
```

**Report Summary** (`.cache/youtube-dm-report.json`):

```json
{
  "timestamp": "2026-04-15T03:05:30",
  "status": "completed",
  "total_dms_processed": 3,
  "auto_responses_sent": 3,
  "by_category": {
    "setup_help": 1,
    "newsletter": 1,
    "product_inquiry": 1
  },
  "partnerships_flagged": 0,
  "interesting_partnerships": [],
  "product_inquiries": 1,
  "conversion_potential": "1 product inquiry to follow up on"
}
```

---

## 🎯 What's Next

1. **Customize templates** (Step 2 above) — 2 min
2. **Schedule with cron or LaunchD** (Step 3 above) — 3 min
3. **Monitor for 24 hours** — Watch the logs and reports accumulate
4. **Review partnership flags** — Check for interesting collab opportunities
5. **Improve templates based on real DMs** — Fine-tune responses as you learn what works

---

## 🐛 Troubleshooting

### "No DMs being fetched"

This usually happens the first time because the browser needs to log into YouTube.

**Solution:**
1. Run with headless disabled to see the browser:
   ```bash
   cd ~/.openclaw/workspace
   source venv/bin/activate
   # Note: The current script doesn't have --headless=false, but Playwright will auto-launch the browser
   python3 youtube-dm-monitor-live.py --report
   ```
2. The browser will open and ask you to log into YouTube
3. Once logged in, the script will work in future cron runs

### "Playwright not found" after cron runs

This means the venv isn't activating properly in cron. Check:

```bash
# Verify venv exists
ls -la ~/.openclaw/workspace/venv/bin/python

# Verify the cron script is using it
grep "source.*venv" ~/.openclaw/workspace/cron-youtube-dm-monitor-live.sh
```

### "Monitor completed with warnings"

Check the logs:
```bash
tail -50 ~/.cache/youtube-dm-monitor-cron.log
```

Common issues:
- YouTube login expired → Re-authenticate by running manually once
- Network timeout → Monitor will retry next hour
- Rate limiting → YouTube API throttling (rare, monitor will backoff)

---

## 📞 Key Files

| File | Purpose | Modify? |
|------|---------|---------|
| `youtube-dm-monitor-live.py` | Main monitor script | ✏️ Yes - update TEMPLATES |
| `cron-youtube-dm-monitor-live.sh` | Hourly launcher | 🔒 Usually no |
| `.cache/youtube-dms.jsonl` | All DM logs | 🔍 Read-only (auto-generated) |
| `.cache/youtube-dm-report.json` | Latest report | 🔍 Read-only (auto-generated) |
| `.cache/youtube-dm-monitor-cron.log` | Execution log | 🔍 Read-only (auto-generated) |

---

## ✨ You're All Set!

The monitor is fully functional and ready to run. 

**Next steps:**
1. Customize templates (2 min)
2. Set up scheduling (3 min)
3. Monitor the logs

That's it. You'll have automatic DM monitoring, categorization, and auto-responses running every hour.

**Questions?** Check the logs: `tail -f ~/.cache/youtube-dm-monitor-cron.log`
