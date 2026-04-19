# YouTube Monitor - Cheat Sheet

Quick reference for common operations.

## Installation

```bash
# Install dependencies
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Run setup (handles everything)
python3 ~/.openclaw/workspace/.cache/setup-youtube-cron.py
```

## Monitoring

```bash
# Dashboard (stats, recent comments)
python3 ~/.openclaw/workspace/.cache/youtube-monitor-dashboard.py

# Live log
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log

# Cron execution log
tail -f ~/.openclaw/workspace/.cache/youtube-monitor-cron.log

# Manual run
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

## Queries

```bash
# View all comments (pretty-printed)
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | python3 -m json.tool

# Last 10 comments
tail -10 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | python3 -m json.tool

# Count by category
jq -r '.category' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | sort | uniq -c

# View questions only
jq 'select(.category == "question")' ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# View sales (flagged for review)
jq 'select(.category == "sales")' ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Find by commenter
jq 'select(.commenter == "Name Here")' ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# View auto-responses sent
jq 'select(.response_status == "auto_responded")' ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Export to CSV
jq -r '[.timestamp, .commenter, .category, .text] | @csv' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl > comments.csv
```

## Configuration

```bash
# Edit monitor script (response templates, patterns)
nano ~/.openclaw/workspace/.cache/youtube-comment-monitor.py

# Update cron frequency
crontab -e

# View cron job
crontab -l | grep youtube
```

## Cron Management

```bash
# Check if running
crontab -l | grep youtube

# Install cron job
*/30 * * * * /bin/bash /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh

# Remove cron job
crontab -e  # Remove the line and save

# Test manually
bash /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

## Credentials

```bash
# Reset OAuth token (force re-auth)
rm ~/.openclaw/workspace/.cache/youtube_token.json

# Verify credentials file exists
ls -la ~/.openclaw/workspace/.cache/youtube_credentials.json

# Check permissions
stat ~/.openclaw/workspace/.cache/youtube_token.json
```

## Troubleshooting

```bash
# Check logs for errors
grep -i error ~/.openclaw/workspace/.cache/youtube-monitor.log

# See recent activity
tail -20 ~/.openclaw/workspace/.cache/youtube-monitor.log

# Count comments processed
wc -l ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Verify script syntax
python3 -m py_compile ~/.openclaw/workspace/.cache/youtube-comment-monitor.py

# Test cron permissions
ls -la ~/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

## Commands by Frequency

### Daily
```bash
python3 ~/.openclaw/workspace/.cache/youtube-monitor-dashboard.py
```

### Weekly
```bash
# Review flagged sales comments
jq 'select(.response_status == "flagged_for_review")' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

### Monthly
```bash
# Archive old logs
cp ~/.openclaw/workspace/.cache/youtube-comments.jsonl \
   ~/.openclaw/workspace/.cache/youtube-comments-$(date +%Y-%m).jsonl

# Backup credentials
cp ~/.openclaw/workspace/.cache/youtube_credentials.json \
   ~/.openclaw/workspace/.cache/youtube_credentials.backup.json
```

## Quick Stats

```bash
# Total comments
jq -s 'length' ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# By category
jq -r '.category' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | sort | uniq -c

# Questions without response
jq -r 'select(.category == "question" and .response_status == "none")' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l

# Auto-responses sent
jq -r 'select(.response_status == "auto_responded")' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l

# Flagged for review
jq -r 'select(.response_status == "flagged_for_review")' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l
```

## File Locations

```
~/.openclaw/workspace/.cache/
├── youtube-comment-monitor.py          # Main script
├── youtube-monitor-cron.sh             # Cron wrapper
├── setup-youtube-cron.py               # Setup assistant
├── youtube-monitor-dashboard.py        # Dashboard viewer
├── youtube_credentials.json            # OAuth credentials (secret!)
├── youtube_token.json                  # OAuth token (secret!)
├── youtube-comments.jsonl              # All comments log
├── youtube-monitor.log                 # Monitor logs
├── youtube-monitor-cron.log            # Cron execution logs
├── youtube-monitor-state.json          # Last check time
├── README-YOUTUBE-MONITOR.md           # Full documentation
├── YOUTUBE-SETUP.md                    # Setup guide
└── YOUTUBE-CHEATSHEET.md               # This file
```

## Tips & Tricks

**Use aliases** in your shell:
```bash
alias ytmon='python3 ~/.openclaw/workspace/.cache/youtube-monitor-dashboard.py'
alias ytlog='tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log'
alias ytflagged='jq "select(.response_status == \"flagged_for_review\")" ~/.openclaw/workspace/.cache/youtube-comments.jsonl'
```

**Monitor in background:**
```bash
# Run dashboard and update every 30 seconds
watch -n 30 'python3 ~/.openclaw/workspace/.cache/youtube-monitor-dashboard.py'
```

**Alert on new flagged comments:**
```bash
# Run daily cron to email if flagged comments exist
0 9 * * * test $(jq 'select(.response_status == "flagged_for_review")' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l) -gt 0 && mail -s "YouTube: New flagged comments" user@example.com
```

---

**Questions?** See `YOUTUBE-SETUP.md` for detailed guide.
