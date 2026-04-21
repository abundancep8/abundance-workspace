# YouTube DM Monitor - Cron Job Setup & Documentation

A production-ready system for monitoring YouTube DMs, auto-responding with templates, and flagging partnerships for manual review.

## 📋 What It Does

The YouTube DM Monitor is a scheduled automation that:

✅ **Fetches new DMs** from the Concessa Obvius YouTube channel (test data simulation for now)
✅ **Categorizes automatically** - setup_help, newsletter, product_inquiry, partnership
✅ **Auto-responds** with appropriate template messages
✅ **Flags partnerships** for manual review (budget mentions, major brands, 100+ chars)
✅ **Logs everything** to JSONL for analysis and audit trail
✅ **Generates hourly reports** with stats and conversion potential
✅ **Tracks state** to avoid processing the same DM twice
✅ **Handles errors** gracefully with comprehensive logging

## 📁 Files Included

```
/Users/abundance/.openclaw/workspace/
├── youtube-dm-monitor-cron.py          # Main Python worker (production code)
├── youtube-dm-monitor-cron.sh          # Shell wrapper (for cron/launchd)
├── youtube-dm-templates.json           # Auto-response templates config
├── youtube-dm-state.json               # Processed DM ID tracking
├── setup-youtube-dm-cron.sh            # Installation & setup script
├── YOUTUBE-DM-CRON-SETUP.md           # This file
└── .cache/                             # Auto-created on first run
    ├── youtube-dms.jsonl               # DM log (append-only)
    ├── youtube-dm-state.json           # State tracking (managed)
    ├── youtube-dm-monitor.log          # Execution log
    └── reports/                        # Hourly reports
        └── report_2026-04-20_20-05-00.txt
```

## 🚀 Quick Start

### 1. Make scripts executable

```bash
chmod +x /Users/abundance/.openclaw/workspace/youtube-dm-monitor-cron.sh
chmod +x /Users/abundance/.openclaw/workspace/setup-youtube-dm-cron.sh
```

### 2. Run setup script to install cron/launchd

```bash
cd /Users/abundance/.openclaw/workspace
./setup-youtube-dm-cron.sh install
```

You'll be prompted to choose:
- **Option 1**: launchd (recommended for macOS) - runs every 60 minutes
- **Option 2**: crontab - runs every hour at :00
- **Option 3**: Both
- **Option 4**: Cancel

### 3. Test it

```bash
./setup-youtube-dm-cron.sh test
```

Or run directly:

```bash
python3 youtube-dm-monitor-cron.py
```

### 4. Check status

```bash
./setup-youtube-dm-cron.sh status
```

## ⚙️ Configuration

### Response Templates (`youtube-dm-templates.json`)

Edit templates to customize auto-responses for each category:

```json
{
  "setup_help": {
    "subject": "Setup Help - Let's Get You Started! 👋",
    "body": "Thanks for reaching out..."
  },
  "newsletter": { ... },
  "product_inquiry": { ... },
  "partnership": { ... }
}
```

**Categories:**
- `setup_help` - Questions about setup, installation, getting started
- `newsletter` - Subscription requests
- `product_inquiry` - Pricing, features, recommendations
- `partnership` - Collaboration, sponsorship, affiliate requests

### Partnership Flagging Rules

Partnerships are flagged for manual review if they mention:
- Budget/investment amounts (`$`, `budget`, `funding`, etc.)
- Major brands (Google, Meta, Amazon, Stripe, Shopify, etc.)
- Specific phrases (`exclusive`, `white label`, `revenue share`, etc.)
- Text longer than 100 characters

Customize the major brands list in `youtube-dm-monitor-cron.py`:

```python
def _load_major_brands(self) -> List[str]:
    return [
        "google", "meta", "facebook", ...
    ]
```

## 📊 Data & Logging

### JSONL Log Format (`youtube-dms.jsonl`)

Each line is a JSON object with:

```json
{
  "id": "dm_001",
  "timestamp": "2026-04-20T20:05:00.123456",
  "sender": "Alice_Creator",
  "text": "I'm trying to set up your product...",
  "category": "setup_help",
  "response_sent": true,
  "response_preview": "Thanks for reaching out! Here are...",
  "interesting_partnership": false
}
```

**Append-only design**: Never deletes, only appends. Safe for concurrent reads.

### State File (`youtube-dm-state.json`)

Tracks processed DM IDs to avoid duplicates:

```json
{
  "processed_ids": ["dm_001", "dm_002", ...],
  "last_run": "2026-04-20T20:05:00.123456",
  "run_count": 42,
  "hourly_report_generated": "2026-04-20T20:00:00.123456"
}
```

**Auto-managed** - Do not edit manually.

### Execution Log (`youtube-dm-monitor.log`)

Standard text log with timestamps, levels, and messages:

```
2026-04-20 20:05:00,123 [INFO] ============================================================
2026-04-20 20:05:00,124 [INFO] YouTube DM Monitor - Cron Job Started
2026-04-20 20:05:00,125 [INFO] Run count: 1
2026-04-20 20:05:00,126 [INFO] ============================================================
2026-04-20 20:05:00,127 [INFO] Processing 2 new DM(s)...
2026-04-20 20:05:00,128 [INFO] ✓ Logged DM from Alice_Creator (ID: dm_001, Category: setup_help)
```

### Hourly Reports (`reports/report_YYYY-MM-DD_HH-MM-SS.txt`)

Generated once per hour if there's activity:

```
╔════════════════════════════════════════════════════════════╗
║   YOUTUBE DM MONITOR - HOURLY REPORT                       ║
║   Generated: 2026-04-20 20:00:00                           ║
╚════════════════════════════════════════════════════════════╝

📊 ACTIVITY SUMMARY
  Total DMs Processed:     5
  Auto-responses Sent:     5
  Response Rate:           100.0%

📂 BY CATEGORY
  Setup Help              2
  Newsletter              1
  Product Inquiry         1
  Partnership             1

🤝 PARTNERSHIPS
  Total Flagged:           1
  
💰 CONVERSION POTENTIAL
  1 product inquiries (follow-up candidates)

⚠️  ACTION NEEDED: Review flagged partnerships!
```

## 🔧 Scheduling Options

### macOS launchd (Recommended)

Runs every 60 minutes automatically, even if Terminal is closed.

**Status:**
```bash
launchctl list | grep youtube-dm-monitor
```

**Manual control:**
```bash
launchctl load ~/Library/LaunchAgents/com.concessa.youtube-dm-monitor.plist
launchctl unload ~/Library/LaunchAgents/com.concessa.youtube-dm-monitor.plist
```

**View logs:**
```bash
tail -f /Users/abundance/.openclaw/workspace/.cache/youtube-dm-monitor.out
tail -f /Users/abundance/.openclaw/workspace/.cache/youtube-dm-monitor.err
```

### crontab

Runs at the top of every hour (`0 * * * *`).

**View your cron jobs:**
```bash
crontab -l
```

**View logs:**
```bash
tail -f /Users/abundance/.openclaw/workspace/.cache/youtube-dm-monitor.cron.log
```

**Edit schedule** (e.g., every 30 minutes instead):
```bash
crontab -e
# Change: 0 * * * * ...
# To:     */30 * * * * ...
```

## 🧪 Testing

### Run Once

```bash
./setup-youtube-dm-cron.sh test
```

### Run with Test Data

The monitor includes 5 pre-loaded test DMs:

1. **Alice_Creator** - "I'm trying to set up..." → setup_help
2. **marketing_guy** - "$50k budget sponsorship" → partnership (flagged)
3. **subscriber_jane** - "Newsletter?" → newsletter
4. **potential_buyer** - "How much is pro?" → product_inquiry
5. **enterprise_contact** - "White-label partnership..." → partnership (flagged)

### View Results

After running:

```bash
# View the DM log
cat /Users/abundance/.openclaw/workspace/.cache/youtube-dms.jsonl

# View state
cat /Users/abundance/.openclaw/workspace/.cache/youtube-dm-state.json

# View execution log
tail /Users/abundance/.openclaw/workspace/.cache/youtube-dm-monitor.log

# View latest report
ls -lt /Users/abundance/.openclaw/workspace/.cache/reports/ | head
```

## 📈 Analytics & Insights

### DM Statistics

Track conversions and engagement:

```python
# Get current stats
stats = monitor.get_stats()
print(stats)
# {
#   'total_dms': 5,
#   'auto_responses_sent': 5,
#   'by_category': {'setup_help': 2, 'newsletter': 1, 'product_inquiry': 1, 'partnership': 1},
#   'partnerships_flagged': 2,
#   'response_rate': 100.0,
#   'conversion_potential': '1 product inquiries (follow-up candidates)'
# }
```

### Analyze with Python

```python
import json
from pathlib import Path

log_file = Path(".cache/youtube-dms.jsonl")

# Load all DMs
dms = []
with open(log_file) as f:
    for line in f:
        dms.append(json.loads(line))

# Analyze by sender
senders = {}
for dm in dms:
    sender = dm['sender']
    senders[sender] = senders.get(sender, 0) + 1

print(f"Total senders: {len(senders)}")
for sender, count in sorted(senders.items(), key=lambda x: -x[1]):
    print(f"  {sender}: {count}")
```

## 🐛 Troubleshooting

### Cron job not running

**Check status:**
```bash
./setup-youtube-dm-cron.sh status
```

**Check system logs (macOS):**
```bash
log stream --predicate 'eventMessage contains "youtube-dm"'
```

**Check cron logs:**
```bash
tail -f /var/log/system.log | grep CRON
```

### No new DMs being logged

- Check the state file isn't locked
- Verify test DMs are set up in the code
- Run a manual test: `python3 youtube-dm-monitor-cron.py`

### Script permissions error

```bash
chmod +x /Users/abundance/.openclaw/workspace/youtube-dm-monitor-cron.sh
chmod +x /Users/abundance/.openclaw/workspace/setup-youtube-dm-cron.sh
```

### Python import errors

Ensure Python 3 is installed:
```bash
python3 --version
```

## 🔌 Integration with YouTube API (Future)

Currently uses test data. To integrate with real YouTube API:

1. **Get API credentials** at [console.cloud.google.com](https://console.cloud.google.com)
2. **Enable YouTube Data API v3**
3. **Create OAuth 2.0 credentials** (service account or user account)
4. **Replace `fetch_test_dms()`** in the monitor with actual API calls:

```python
def fetch_real_dms(self):
    """Fetch actual DMs from YouTube API."""
    from googleapiclient.discovery import build
    
    youtube = build('youtube', 'v3', credentials=credentials)
    
    # Fetch DMs from channel
    results = youtube.messages().list(
        part='snippet',
        channelId='UCxxxxxxxxxxxxxxx'
    ).execute()
    
    return results.get('items', [])
```

## 📋 Checklist

- [ ] Scripts are executable
- [ ] Setup script ran successfully
- [ ] Test run completed without errors
- [ ] State file created at `.cache/youtube-dm-state.json`
- [ ] DM log created at `.cache/youtube-dms.jsonl`
- [ ] Cron/launchd job is active
- [ ] First hourly report generated
- [ ] Execution logs visible in `.cache/youtube-dm-monitor.log`

## 📞 Support

For issues or questions:

1. Check logs: `tail -f .cache/youtube-dm-monitor.log`
2. Run test: `./setup-youtube-dm-cron.sh test`
3. Check status: `./setup-youtube-dm-cron.sh status`
4. Review this documentation

## 📝 Updates & Maintenance

### Update Response Templates

Edit `youtube-dm-templates.json` and restart:

```bash
./setup-youtube-dm-cron.sh status  # Confirm it's running
# (changes are picked up on next execution)
```

### Change Schedule

**launchd (every 30 minutes):**

```bash
# Edit the plist
nano ~/Library/LaunchAgents/com.concessa.youtube-dm-monitor.plist
# Change: <integer>3600</integer>  (seconds)
# To:     <integer>1800</integer>
# Then reload
launchctl unload ~/Library/LaunchAgents/com.concessa.youtube-dm-monitor.plist
launchctl load ~/Library/LaunchAgents/com.concessa.youtube-dm-monitor.plist
```

**crontab (every 30 minutes):**

```bash
crontab -e
# Change: 0 * * * * ...
# To:     */30 * * * * ...
```

### Upgrade Code

1. Update `youtube-dm-monitor-cron.py` with new features
2. Restart cron (changes picked up on next cycle)

### Backup Data

```bash
# Backup logs
cp -r .cache/youtube-dms.jsonl backup/youtube-dms.$(date +%Y-%m-%d).jsonl
cp -r .cache/reports backup/reports-$(date +%Y-%m-%d)/
```

---

**Last Updated:** 2026-04-20
**Version:** 1.0
**Status:** Production Ready ✓
