# YouTube Comment Monitor v2 - Quick Start

**Status:** ✅ Running every 30 minutes (demo mode)  
**Latest Report:** `.cache/youtube-comments-report.txt`  
**Comment Log:** `.cache/youtube-comments.jsonl`

---

## Check Status (Right Now)

```bash
# See latest report
cat ~/.openclaw/workspace/.cache/youtube-comments-report.txt

# See last 5 comments logged
tail -5 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .

# See processing state
cat ~/.openclaw/workspace/.cache/youtube-comment-state.json | jq .
```

---

## What It's Doing

Every 30 minutes, the monitor:

1. ✅ **Fetches** recent comments from Concessa Obvius YouTube channel
2. ✅ **Categorizes** each comment:
   - Questions (how, what, cost, tools) → **Auto-reply**
   - Praise (amazing, inspiring) → **Auto-reply**
   - Spam (crypto, MLM) → **Flag for review**
   - Sales (partnerships, collabs) → **Flag for review**
   - Other → **Flag for review**
3. ✅ **Logs** everything to `.jsonl` with timestamp, author, text, category, response
4. ✅ **Generates report** showing total processed, auto-replied, flagged

---

## Test Run

```bash
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor-v2.py
```

Output shows:
- How many comments processed
- How many auto-replies sent
- How many flagged for review
- Channel URL
- Current mode (DEMO or PRODUCTION)

---

## Enable Production Mode (Real YouTube)

Currently in **DEMO mode** (test data).

To use **real YouTube comments**:

1. Go to https://console.cloud.google.com
2. Create a project, enable YouTube Data API v3
3. Create OAuth2 credentials (Desktop app)
4. Download JSON → save to `~/.openclaw/workspace/.secrets/youtube-credentials.json`
5. Run auth:
```bash
cd ~/.openclaw/workspace
python3 << 'EOF'
from google_auth_oauthlib.flow import InstalledAppFlow
import json
from pathlib import Path

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
CREDENTIALS_FILE = Path.home() / '.openclaw/workspace/.secrets/youtube-credentials.json'
TOKEN_FILE = Path.home() / '.openclaw/workspace/.secrets/youtube-token.json'

flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
creds = flow.run_local_server(port=0)

with open(TOKEN_FILE, 'w') as f:
    f.write(creds.to_json())

print("✅ OAuth2 token saved!")
EOF
```
6. Next run will be in PRODUCTION mode!

---

## Log Files

| File | What | View With |
|------|------|-----------|
| `.cache/youtube-comments-report.txt` | Human report | `cat` |
| `.cache/youtube-comments.jsonl` | Full comment log | `tail -10 \| jq .` |
| `.cache/youtube-comment-state.json` | Dedup state | `cat \| jq .` |
| `.cache/youtube-monitor-cron.log` | Cron runs | `tail -20` |

---

## Categories & Auto-Replies

### Questions (Auto-Reply)
- "How do I start?" → Detailed startup guide
- "What tools?" → Lists tools used
- "How much cost?" → Pricing answer
- "How long?" → Timeline
- General "?" → Helpful redirect

### Praise (Auto-Reply)
- "Amazing!" → Thank you, but build!
- "Inspiring" → Action beats inspiration
- "Great work" → Thanks, keep going
- "Thank you" → Appreciation message

### Spam (Flag)
- Crypto/Bitcoin/NFT
- MLM/Recruitment
- "DM me" / Scam signals

### Sales (Flag)
- Partnership requests
- Sponsorship offers
- "Work with us"

### Other (Flag)
- Doesn't match above

---

## For Next 30 Minutes

Monitor will run automatically. Check results anytime:

```bash
# Get latest report
cat ~/.openclaw/workspace/.cache/youtube-comments-report.txt
```

That's it! The monitor handles everything else.

---

**Next Step:** Set up YouTube credentials to switch from DEMO to PRODUCTION mode.  
**Docs:** See `YOUTUBE-COMMENT-MONITOR-v2-SETUP.md` for full details.
