# YouTube DM Monitor - Setup & Installation Guide

## Overview

The YouTube DM Monitor automatically:
1. **Fetches** unread DMs from YouTube Studio (Concessa Obvius channel)
2. **Categorizes** each DM into: Setup Help, Newsletter, Product Inquiry, Partnership
3. **Auto-responds** with templated replies
4. **Logs** all activity to `.cache/youtube-dms.jsonl`
5. **Flags** interesting partnerships for manual review
6. **Reports** metrics: total DMs, responses sent, conversion potential

Runs hourly via cron. Requires browser automation (Playwright).

---

## Prerequisites

- Python 3.7+
- YouTube account with Studio access (Concessa Obvius channel)
- Playwright (for browser automation)
- Bash/cron (for scheduling)

---

## Installation

### 1. Create Virtual Environment (Recommended)

```bash
cd ~/.openclaw/workspace
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install playwright
python -m playwright install chromium
```

**If using system Python** (via Homebrew), install with `--user` flag:
```bash
python3 -m pip install --user playwright
python3 -m playwright install
```

### 3. Verify Installation

```bash
python3 youtube-dm-monitor-live.py --test
```

Expected output:
```
✓ Logged DM from Alice_Creator (setup_help)
✓ Logged DM from marketing_guy (partnership)
  🚩 FLAGGED
...
📈 REPORT
Total DMs: 4
Auto-responses: 4
```

---

## Configuration

### 1. Update Auto-Response Templates

Edit `youtube-dm-monitor-live.py` to customize templates:

```python
TEMPLATES = {
    "setup_help": """Your custom setup help message...""",
    "newsletter": """Your newsletter signup message...""",
    # etc.
}
```

Or use the included `youtube-dm-templates.md` as reference.

### 2. Customize Keywords

Modify `KEYWORDS` dict to adjust categorization:

```python
KEYWORDS = {
    "setup_help": ["setup", "how to", "confused", ...],
    "newsletter": ["newsletter", "subscribe", ...],
    # etc.
}
```

### 3. Set Discord Webhook (Optional)

To send reports to Discord, set the environment variable:

```bash
export YOUTUBE_MONITOR_WEBHOOK="https://discord.com/api/webhooks/..."
```

Add to `.env` or `~/.bash_profile` to persist across sessions:
```bash
echo 'export YOUTUBE_MONITOR_WEBHOOK="https://discord.com/api/webhooks/..."' >> ~/.bash_profile
```

---

## Running the Monitor

### Manual Run

```bash
# Activate venv first (if created above)
source ~/.openclaw/workspace/venv/bin/activate

# Run with report
python3 youtube-dm-monitor-live.py --report

# Run in headless mode (no browser window)
python3 youtube-dm-monitor-live.py --headless --report

# Enable debug output
python3 youtube-dm-monitor-live.py --debug --report
```

### Scheduled (Cron)

#### Option A: Using Cron Script (Recommended)

Make the script executable:
```bash
chmod +x ~/. openclaw/workspace/cron-youtube-dm-monitor-live.sh
```

Add to crontab (runs every hour):
```bash
crontab -e
```

Add this line:
```
0 * * * * /Users/abundance/.openclaw/workspace/cron-youtube-dm-monitor-live.sh
```

View cron logs:
```bash
tail -f ~/.cache/youtube-dm-monitor.log
```

#### Option B: OpenClaw Cron (If Configured)

```bash
openclaw cron add --name youtube-dm-monitor --interval "0 * * * *" \
  --command "cd ~/.openclaw/workspace && source venv/bin/activate && python3 youtube-dm-monitor-live.py --report"
```

---

## Output Files

| File | Contents |
|------|----------|
| `.cache/youtube-dms.jsonl` | All DMs (one JSON per line) |
| `.cache/youtube-dm-report.json` | Latest report (JSON format) |
| `.cache/youtube-dm-monitor.log` | Execution log (cron runs) |

### Viewing Logs

```bash
# Last 20 DMs
tail -20 ~/.cache/youtube-dms.jsonl | jq '.'

# Interesting partnerships (flagged for manual review)
grep '"interesting_partnership": true' ~/.cache/youtube-dms.jsonl | jq '.'

# DMs from last hour
jq 'select(.timestamp > now - 3600)' ~/.cache/youtube-dms.jsonl

# Count by category
jq '.category' ~/.cache/youtube-dms.jsonl | sort | uniq -c

# Watch live (cron mode)
tail -f ~/.cache/youtube-dm-monitor.log
```

---

## Categorization Rules

### Setup Help
**Keywords:** setup, how to, confused, beginner, tutorial, install, getting started, doesn't work, help, guide, stuck, error, not working

**Template:** Links to setup guide, video, FAQ

**Response:** Auto-send

### Newsletter
**Keywords:** newsletter, updates, email list, subscribe, news, latest, stay updated, follow, sign up

**Template:** Newsletter signup CTA with benefits

**Response:** Auto-send

### Product Inquiry
**Keywords:** buy, pricing, price, cost, purchase, how much, afford, product, which version, recommend, features, difference, plan

**Template:** Product info & pricing with follow-up questions

**Response:** Auto-send

### Partnership
**Keywords:** collaborate, sponsorship, partner, joint, co-brand, affiliate, promotion, promote, work together, business opportunity, brand deal

**Template:** Redirect to partnership email

**Response:** Auto-send + FLAG for manual review if:
- Message > 150 characters
- Contains: "brand", "major", "large", "budget", "contract", "deal"
- Mentions YouTube/influencer/agency
- Asks a question

---

## Troubleshooting

### "Playwright not installed"
```bash
python3 -m pip install --user playwright
python3 -m playwright install
```

### "Channel not found" or "DM list empty"
- Verify YouTube browser session is active
- Check if DMs are actually available in YouTube Studio
- Monitor may need to be interactive (not headless) first time

### "Can't compare offset-naive and offset-aware datetimes"
- Indicates timezone issue in logs
- Delete `.cache/youtube-dms.jsonl` and restart
- Or check that all timestamps are ISO format

### Cron not running
```bash
# Check cron logs
log stream --predicate 'process == "cron"'

# Verify crontab
crontab -l

# Test script directly
/Users/abundance/.openclaw/workspace/cron-youtube-dm-monitor-live.sh

# Add to cron error log
0 * * * * /Users/abundance/.openclaw/workspace/cron-youtube-dm-monitor-live.sh 2>&1 | logger
```

### Discord webhook not working
- Verify webhook URL is correct
- Test with curl:
```bash
curl -X POST "$YOUTUBE_MONITOR_WEBHOOK" \
  -H 'Content-Type: application/json' \
  -d '{"content":"Test message"}'
```

---

## Monitoring & Analytics

### Get Current Stats

```bash
# Last 24 hours
python3 -c "
from youtube_dm_monitor_live import YouTubeDMMonitor
m = YouTubeDMMonitor()
stats = m.get_stats(hours=24)
print(f\"📊 24h Report:\")
print(f\"  Total DMs: {stats['total_dms']}\")
print(f\"  Auto-responses: {stats['auto_responses_sent']}\")
print(f\"  By category: {stats['by_category']}\")
print(f\"  Partnerships flagged: {stats['partnerships_flagged']}\")
"
```

### Export to CSV

```bash
python3 << 'EOF'
import json
import csv

with open('.cache/youtube-dms.jsonl') as f:
    dms = [json.loads(line) for line in f if line.strip()]

with open('.cache/youtube-dms.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['timestamp', 'sender', 'category', 'text'])
    writer.writeheader()
    writer.writerows(dms)

print(f"✅ Exported {len(dms)} DMs to .cache/youtube-dms.csv")
EOF
```

---

## Advanced Configuration

### Custom Response Logic

Edit `YouTubeDMMonitor.process_dm()` to add custom logic:

```python
def process_dm(self, sender, sender_id, text, dm_id=None):
    # Your custom logic
    if "special_keyword" in text.lower():
        response = "Custom response..."
    else:
        category = self.categorize_dm(text)
        response = TEMPLATES[category]
    # ...
```

### Multiple Channels

Create separate monitor instances:

```bash
# youtube-dm-monitor-concessa.py
CHANNEL = "Concessa Obvius"
LOG_FILE = ".cache/youtube-dms-concessa.jsonl"

# youtube-dm-monitor-other.py
CHANNEL = "Your Other Channel"
LOG_FILE = ".cache/youtube-dms-other.jsonl"
```

Then run both in cron:
```
0 * * * * /path/to/cron-monitor-concessa.sh
0 * * * * /path/to/cron-monitor-other.sh
```

---

## Support

- **Docs:** See `YOUTUBE-DM-MONITOR-SETUP.md`
- **Logs:** `tail -f ~/.cache/youtube-dm-monitor.log`
- **Debug:** Run with `--debug` flag
- **Test:** Run with `--test` flag

---

## What's Next?

- [ ] Verify browser automation works with your YouTube account
- [ ] Customize response templates
- [ ] Set up Discord webhook for reports
- [ ] Configure cron schedule
- [ ] Monitor first 24 hours manually, then automate
- [ ] Export to CRM if needed
- [ ] Review flagged partnerships daily

---

_Happy DMing! 🚀_
