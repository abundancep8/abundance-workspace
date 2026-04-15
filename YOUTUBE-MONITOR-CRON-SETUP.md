# YouTube Comment Monitor - Cron Setup Guide

## Quick Setup (Choose One)

### Option A: System Crontab (Recommended)

Run this command in your terminal:

```bash
(crontab -l 2>/dev/null || echo "") | cat - << 'EOF' | crontab -
# YouTube Comment Monitor - Every 30 minutes
*/30 * * * * cd /Users/abundance/.openclaw/workspace && bash scripts/youtube-monitor-cron.sh >> .cache/youtube-monitor.log 2>&1
EOF
```

**Verify installation:**
```bash
crontab -l | grep youtube
```

### Option B: OpenClaw Native Cron

If you're using OpenClaw with cron support, the monitor is ready. Just run:

```bash
openclaw cron add youtube-monitor "*/30 * * * *" "cd /Users/abundance/.openclaw/workspace && bash scripts/youtube-monitor-cron.sh"
```

Or use the manifest:
```bash
openclaw deploy .youtube-monitor-manifest.json
```

### Option C: LaunchAgent (macOS - Runs in Background)

Create a LaunchAgent that runs every 30 minutes:

```bash
cat > ~/Library/LaunchAgents/com.openclaw.youtube-monitor.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.youtube-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/abundance/.openclaw/workspace/scripts/youtube-monitor-cron.sh</string>
    </array>
    <key>StartInterval</key>
    <integer>1800</integer>
    <key>StandardOutPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log</string>
</dict>
</plist>
EOF

# Load the agent
launchctl load ~/Library/LaunchAgents/com.openclaw.youtube-monitor.plist

# Verify
launchctl list | grep youtube
```

To stop:
```bash
launchctl unload ~/Library/LaunchAgents/com.openclaw.youtube-monitor.plist
```

## Pre-Flight Checks

Before any cron setup, ensure:

1. ✓ Monitor script is executable:
   ```bash
   ls -l /Users/abundance/.openclaw/workspace/scripts/youtube-monitor-cron.sh
   ```

2. ✓ Python 3 is in PATH:
   ```bash
   which python3
   ```

3. ✓ YouTube credentials exist:
   ```bash
   ls -l /Users/abundance/.openclaw/workspace/.secrets/youtube-*.json
   ```

4. ✓ Authentication token is fresh (run this first):
   ```bash
   python3 /Users/abundance/.openclaw/workspace/scripts/youtube-setup-auth.py
   ```

## Monitoring Your Cron Job

### View logs in real-time:
```bash
tail -f /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log
```

### Count successful runs:
```bash
grep "Monitor complete" /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log | wc -l
```

### Last 5 runs:
```bash
tail -100 /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.log | grep -E "(Starting YouTube|Monitor complete|Error)"
```

### View processed comments:
```bash
tail -20 /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .
```

### Count auto-responses by hour:
```bash
jq -r '.timestamp | split("T")[1]' /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl | \
  awk -F: '{print $1}' | sort | uniq -c
```

## Troubleshooting

### "Permission denied" when installing crontab

Try adding sudo:
```bash
sudo crontab -e
```

Or use the LaunchAgent method instead.

### Cron job not running

Check system log:
```bash
log stream --predicate 'process == "cron"' --level debug
```

### "YouTube authentication failed"

Re-authenticate:
```bash
python3 /Users/abundance/.openclaw/workspace/scripts/youtube-setup-auth.py
```

### Check if Python can import required libraries

```bash
python3 -c "from googleapiclient.discovery import build; print('✓ Google API installed')"
```

## Logs & Diagnostics

All logs append to `.cache/youtube-monitor.log`. The monitor rotates the file when it exceeds 5MB.

**Log format example:**
```
[HH:MM:SS] Starting YouTube comment monitor...
  Channel ID: UCxxxxxxxxxxxxxxxx
  Found 3 new comments
  ✓ Auto-replied to question: User123
  ⚠️  Flagged for review (sales): Partner456
[HH:MM:SS] Monitor complete.
```

## Disable/Enable

### Disable temporarily:
```bash
# Comment out in crontab
crontab -e
# Find the line and add a # at the start
```

### Disable permanently:
```bash
# Remove from crontab
crontab -e
# Delete the YouTube monitor line and save
```

### Re-enable:
```bash
# Re-add the line using Option A above
```

---

**Status:** Monitor system ready. Complete authentication, then pick your preferred cron method (A, B, or C) to start.
