🎬 YouTube COMMENT MONITOR - INSTALLATION COMPLETE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 SETUP CHECKLIST:

✓ Monitor script installed: scripts/youtube-comment-monitor.py
✓ Cron launcher installed: scripts/youtube-monitor-cron.sh
✓ Auth helper installed: scripts/youtube-setup-auth.py
✓ Logging infrastructure ready: .cache/youtube-comments.jsonl
✓ State tracking ready: .cache/.youtube-monitor-state.json
✓ Documentation complete: YOUTUBE-MONITOR-SETUP.md

⚠️  STEP REQUIRED: Re-authenticate with YouTube API

The OAuth token (youtube-token.json) has expired and needs to be refreshed.

COMMAND TO RUN (on your Mac):
  python3 ~/openclaw/workspace/scripts/youtube-setup-auth.py

This will:
  1. Open your browser to Google OAuth
  2. Ask for permission to access your YouTube channel
  3. Save a fresh token valid for ~6 months
  4. Ready the monitor to run

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 HOW IT WORKS:

Every 30 minutes:
  1. Fetch new comments from Concessa Obvius channel
  2. Categorize: Questions, Praise, Spam, Sales, or General
  3. Auto-respond to Questions and Praise
  4. Flag Sales comments for your review
  5. Log everything to youtube-comments.jsonl

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📁 FILES & LOGS:

Monitor Script:     scripts/youtube-comment-monitor.py
Cron Wrapper:       scripts/youtube-monitor-cron.sh
Comment Log:        .cache/youtube-comments.jsonl (JSON Lines)
Monitor Logs:       .cache/youtube-monitor.log (rotated at 5MB)
State File:         .cache/.youtube-monitor-state.json
Documentation:      YOUTUBE-MONITOR-SETUP.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 QUICK START:

1. Re-authenticate (ONE TIME):
   python3 ~/openclaw/workspace/scripts/youtube-setup-auth.py

2. Test the monitor:
   python3 ~/openclaw/workspace/scripts/youtube-comment-monitor.py

3. View comments as they arrive:
   tail -f ~/openclaw/workspace/.cache/youtube-comments.jsonl | jq .

4. Check flagged (sales) comments:
   grep '"category": "sales"' ~/openclaw/workspace/.cache/youtube-comments.jsonl | jq .

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📡 MONITORING SCHEDULE:

The monitor runs automatically every 30 minutes via OpenClaw cron.

To check cron status:
  openclaw cron list

To view recent logs:
  tail -20 ~/openclaw/workspace/.cache/youtube-monitor.log

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 RESPONSE CATEGORIES:

1. QUESTIONS → Auto-respond with helpful template
   Keywords: how, what, help, cost, timeline, tools

2. PRAISE → Auto-respond with gratitude
   Keywords: amazing, awesome, inspiring, thank you

3. SPAM → Log only (no response)
   Keywords: crypto, bitcoin, mlm, forex, "click here"

4. SALES → Flag for manual review
   Keywords: partnership, collaboration, sponsorship, brand deal

5. GENERAL → Log only

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 SUPPORT:

For troubleshooting, see: YOUTUBE-MONITOR-SETUP.md

For auth issues, re-run: python3 scripts/youtube-setup-auth.py
For bug reports, check: .cache/youtube-monitor.log

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ CONFIGURED: 2026-04-14 07:30 UTC
NEXT STEP: Run the authentication command above.
