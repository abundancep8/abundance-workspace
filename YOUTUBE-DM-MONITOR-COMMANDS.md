# YouTube DM Monitor - Quick Reference

## 🚀 First Time Setup

```bash
# 1. Install dependencies
pip install playwright
python -m playwright install chromium

# 2. Activate hourly cron
crontab ~/.openclaw/workspace/.crontab

# 3. Authenticate (one-time, opens browser)
python3 ~/.openclaw/workspace/youtube-dm-monitor-live.py --report
```

---

## 📊 Run Anytime

```bash
# See current state + report
python3 ~/.openclaw/workspace/youtube-dm-monitor-live.py --report

# Quiet mode (no report output)
python3 ~/.openclaw/workspace/youtube-dm-monitor-live.py
```

---

## 📈 Check Results

```bash
# View cron execution log
tail -50 ~/.openclaw/workspace/.cache/youtube-dm-monitor-cron.log

# View latest report (JSON)
cat ~/.openclaw/workspace/.cache/youtube-dm-report.json | jq .

# Verify cron is registered
crontab -l | grep youtube
```

---

## 🔍 Query DMs

```bash
# All DMs
jq . ~/.openclaw/workspace/.cache/youtube-dms.jsonl

# Setup help requests
jq 'select(.category == "setup_help")' ~/.openclaw/workspace/.cache/youtube-dms.jsonl

# Product inquiries (conversion potential)
jq 'select(.category == "product_inquiry")' ~/.openclaw/workspace/.cache/youtube-dms.jsonl

# Partnership opportunities (flagged for manual review)
jq 'select(.interesting_partnership == true)' ~/.openclaw/workspace/.cache/youtube-dms.jsonl

# Newsletter signups
jq 'select(.category == "newsletter")' ~/.openclaw/workspace/.cache/youtube-dms.jsonl

# Count by category
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' \
  ~/.openclaw/workspace/.cache/youtube-dms.jsonl

# Most recent 5 DMs
tail -5 ~/.openclaw/workspace/.cache/youtube-dms.jsonl | jq .

# DMs from today
jq "select(.timestamp | startswith(\"$(date +%Y-%m-%d)\"))" \
  ~/.openclaw/workspace/.cache/youtube-dms.jsonl

# Top senders (who DMs most)
jq -s 'group_by(.sender) | map({sender: .[0].sender, count: length}) | sort_by(-.count) | .[0:10]' \
  ~/.openclaw/workspace/.cache/youtube-dms.jsonl
```

---

## 🔧 Customize

```bash
# Edit response templates
nano ~/.openclaw/workspace/youtube-dm-monitor-live.py
# Edit TEMPLATES dict (lines ~50-75)

# Edit categorization keywords
nano ~/.openclaw/workspace/youtube-dm-monitor-live.py
# Edit CATEGORY_PATTERNS (lines ~80-95)

# Change cron schedule
nano ~/.openclaw/workspace/.crontab
# Edit the schedule (0 = hourly, see crontab docs)

# Reinstall cron after changes
crontab ~/.openclaw/workspace/.crontab
```

---

## 📋 Cron Schedules

Replace `0 * * * *` in `.crontab` with:

| Schedule | Meaning |
|----------|---------|
| `0 * * * *` | Every hour (current) |
| `*/15 * * * *` | Every 15 minutes |
| `*/30 * * * *` | Every 30 minutes |
| `0 6,12,18 * * *` | At 6am, noon, 6pm |
| `0 9 * * *` | Every day at 9am |
| `0 0 * * 0` | Every Sunday at midnight |

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| "Playwright not installed" | `pip install playwright && python -m playwright install chromium` |
| Cron not running | `crontab -l` to verify; reinstall with `crontab ~/.openclaw/workspace/.crontab` |
| No new DMs | Check `.cache/youtube-dms.jsonl` - DMs may not be new |
| Need to re-authenticate | Run `python3 youtube-dm-monitor-live.py --report` again |
| Want to see all past DMs | `wc -l ~/.openclaw/workspace/.cache/youtube-dms.jsonl` for count |

---

## 📂 Important Files

| File | Purpose |
|------|---------|
| `youtube-dm-monitor-live.py` | Main script |
| `.crontab` | Cron job definition |
| `.cache/youtube-dms.jsonl` | DM log (append-only) |
| `.cache/youtube-dm-report.json` | Latest report |
| `.cache/youtube-dm-monitor-cron.log` | Cron execution history |
| `docs/YOUTUBE-DM-MONITOR-SETUP.md` | Full setup guide |

---

## 📊 Report Contents

Each run generates a report with:
- **Total DMs processed** (all-time)
- **DMs this run** (new messages)
- **Auto-responses sent** (count)
- **Category breakdown** (setup, newsletter, product, partnership)
- **Partnerships flagged** (count + details)
- **Conversion potential** (product inquiry leads ready to follow up)

---

## ⏱️ Monitor the System

Watch live (refreshes every 60 seconds):
```bash
watch -n 60 'python3 ~/.openclaw/workspace/youtube-dm-monitor-live.py --report'
```

---

## 💡 Pro Tips

- **Export to CSV for analysis:** `jq -r '[.timestamp, .sender, .category] | @csv' ~/.openclaw/workspace/.cache/youtube-dms.jsonl > dms.csv`
- **Filter by date range:** Use `jq 'select(.timestamp >= "2026-04-01" and .timestamp < "2026-04-15")'`
- **Watch for interesting partnerships:** `jq '.interesting_partnerships[] | @text' ~/.openclaw/workspace/.cache/youtube-dm-report.json`
- **Count responses by category:** `jq 'group_by(.category) | map({category: .[0].category, responded: (map(select(.response_sent)) | length)})' ~/.openclaw/workspace/.cache/youtube-dms.jsonl`

---

## 📞 Support

See `docs/YOUTUBE-DM-MONITOR-SETUP.md` for full guide.
Cron logs saved to `.cache/youtube-dm-monitor-cron.log`.
