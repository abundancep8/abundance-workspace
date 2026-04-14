# YouTube Monitor Dashboard

Quick commands to check status and view reports.

---

## 🚀 Quick Start

### First Time Setup

```bash
# 1. Install dependencies
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# 2. Save OAuth2 credentials to ~/.openclaw/youtube-credentials.json
# (Download from Google Cloud Console)

# 3. Test the monitor
bash scripts/test-youtube-monitor.sh
# (Follow browser prompt to authorize)

# 4. Install scheduler (LaunchAgent on macOS)
cp com.youtube-monitor.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.youtube-monitor.plist
launchctl start com.youtube-monitor
```

---

## 📊 View Reports

### Last 20 Comments

```bash
tail -20 .cache/youtube-comments.jsonl | jq '.'
```

### Summary Stats

```bash
python3 - <<'EOF'
import json
from pathlib import Path
from collections import Counter

log = Path(".cache/youtube-comments.jsonl")
if not log.exists():
    print("No log file yet")
    exit()

data = [json.loads(line) for line in open(log) if line.strip()]

print(f"\n📊 YouTube Monitor Summary")
print(f"{'='*50}")
print(f"Total comments processed: {len(data)}")
print(f"")
print(f"By category:")
for cat, count in sorted(Counter(d['category'] for d in data).items()):
    print(f"  • {cat}: {count}")
print(f"")
print(f"Responses sent: {sum(1 for d in data if d['response_status'] == 'responded')}")
print(f"Flagged for review: {sum(1 for d in data if d['response_status'] == 'flagged_for_review')}")
print(f"Failed responses: {sum(1 for d in data if d['response_status'] == 'failed')}")
EOF
```

### Show Flagged Sales Inquiries

```bash
python3 - <<'EOF'
import json
from pathlib import Path

log = Path(".cache/youtube-comments.jsonl")
if not log.exists():
    print("No log file yet")
    exit()

data = [json.loads(line) for line in open(log) if line.strip()]
sales = [d for d in data if d['response_status'] == 'flagged_for_review']

print(f"\n🚩 Sales Inquiries ({len(sales)} total)")
print(f"{'='*50}")
for s in sales:
    print(f"\n• {s['commenter']}")
    print(f"  {s['text']}")
    print(f"  ({s['timestamp']})")
EOF
```

### Show Recent Questions (Unanswered)

```bash
python3 - <<'EOF'
import json
from pathlib import Path

log = Path(".cache/youtube-comments.jsonl")
if not log.exists():
    print("No log file yet")
    exit()

data = [json.loads(line) for line in open(log) if line.strip()]
questions = [d for d in data if d['category'] == 'question']

print(f"\n❓ Questions ({len(questions)} total)")
print(f"{'='*50}")
for q in questions[-10:]:  # Last 10
    status = "✅ Responded" if q['response_status'] == 'responded' else "⚠️  Failed/Pending"
    print(f"\n• {q['commenter']}")
    print(f"  {q['text']}")
    print(f"  {status} ({q['timestamp']})")
EOF
```

---

## 🔍 Monitor Status

### Check if LaunchAgent is Running

```bash
launchctl list | grep youtube-monitor
```

Output should show a PID like:
```
PID  Status  Label
123  -       com.youtube-monitor
```

### Check Last Execution

```bash
tail -20 .cache/youtube-monitor.log
```

### View Errors

```bash
tail -20 .cache/youtube-monitor-error.log
```

### Manual Run (Test)

```bash
bash scripts/youtube-monitor.sh
```

---

## 🛑 Manage Scheduler

### Stop Monitor

```bash
launchctl stop com.youtube-monitor
```

### Start Monitor

```bash
launchctl start com.youtube-monitor
```

### Unload (Disable)

```bash
launchctl unload ~/Library/LaunchAgents/com.youtube-monitor.plist
```

### Reload (After Changes)

```bash
launchctl unload ~/Library/LaunchAgents/com.youtube-monitor.plist
launchctl load ~/Library/LaunchAgents/com.youtube-monitor.plist
launchctl start com.youtube-monitor
```

---

## 📈 Advanced: Export Data

### Export to CSV

```bash
python3 - <<'EOF'
import json
import csv
from pathlib import Path

log = Path(".cache/youtube-comments.jsonl")
data = [json.loads(line) for line in open(log) if line.strip()]

with open(".cache/youtube-comments.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["timestamp", "commenter", "text", "category", "response_status"])
    writer.writeheader()
    writer.writerows(data)

print(f"✅ Exported {len(data)} comments to .cache/youtube-comments.csv")
EOF
```

### Export to JSON (Pretty)

```bash
python3 - <<'EOF'
import json
from pathlib import Path

log = Path(".cache/youtube-comments.jsonl")
data = [json.loads(line) for line in open(log) if line.strip()]

with open(".cache/youtube-comments.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"✅ Exported {len(data)} comments to .cache/youtube-comments.json")
EOF
```

---

## 🧹 Cleanup

### Clear Log (Start Fresh)

```bash
# Backup first!
cp .cache/youtube-comments.jsonl .cache/youtube-comments.jsonl.backup

# Clear
echo "" > .cache/youtube-comments.jsonl

echo "✅ Log cleared (backup saved)"
```

### Archive Old Logs

```bash
# Move current log to timestamped archive
mv .cache/youtube-comments.jsonl .cache/youtube-comments-$(date +%Y%m%d-%H%M%S).jsonl

echo "✅ Log archived"
```

---

## 🐛 Troubleshooting

### "No comments found"

Might be normal if:
- Channel has no new comments
- Comments weren't published since last check
- Check the execution log: `tail .cache/youtube-monitor.log`

### "Authorization failed"

Credentials may be expired:

```bash
# Remove token to force re-auth
rm ~/.openclaw/youtube-token.json

# Run manually to re-authorize
python3 scripts/youtube-comment-monitor.py
```

### Monitor not running

```bash
# Check status
launchctl list | grep youtube-monitor

# If not running, reload
launchctl unload ~/Library/LaunchAgents/com.youtube-monitor.plist
launchctl load ~/Library/LaunchAgents/com.youtube-monitor.plist
launchctl start com.youtube-monitor
```

---

## 📞 Support

See **YOUTUBE-MONITOR-SETUP.md** for detailed configuration and troubleshooting.

---

**Last Updated:** 2026-04-14
