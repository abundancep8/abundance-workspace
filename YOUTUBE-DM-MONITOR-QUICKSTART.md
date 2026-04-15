# YouTube DM Monitor - Quick Start (5 min)

## Install

```bash
cd ~/.openclaw/workspace
python3 -m pip install --user playwright
python3 -m playwright install
```

## Test

```bash
python3 youtube-dm-monitor-live.py --test
```

✅ Should show test DMs being categorized

## Customize (Edit This File)

Open `youtube-dm-monitor-live.py` and find `TEMPLATES` dict. Update:

- `setup_help` → Add your setup guide link
- `newsletter` → Add your newsletter signup URL
- `product_inquiry` → Add your pricing page
- `partnership` → Add your partnership email

## Run Live

```bash
# See browser window, test with real YouTube DMs
python3 youtube-dm-monitor-live.py --report

# Or run in headless mode (no window)
python3 youtube-dm-monitor-live.py --report --headless
```

✅ Should fetch real DMs from Concessa Obvius channel

## Activate Cron (Runs Hourly)

```bash
# Add to crontab
crontab -e

# Paste this line:
0 * * * * /Users/abundance/.openclaw/workspace/cron-youtube-dm-monitor-live.sh

# Save and exit (Ctrl+O, Enter, Ctrl+X in nano)
```

✅ Will now run every hour automatically

## View Logs

```bash
# Watch in real-time
tail -f ~/.cache/youtube-dm-monitor.log

# View DMs
tail -10 ~/.cache/youtube-dms.jsonl | jq '.'

# View flagged partnerships
grep '"interesting_partnership": true' ~/.cache/youtube-dms.jsonl | jq '{sender: .sender, text: .text}'
```

## Discord Alerts (Optional)

```bash
# Set webhook
export YOUTUBE_MONITOR_WEBHOOK="https://discord.com/api/webhooks/YOUR_URL_HERE"

# Make persistent
echo 'export YOUTUBE_MONITOR_WEBHOOK="https://discord.com/api/webhooks/YOUR_URL_HERE"' >> ~/.bash_profile
```

---

## Done!

Monitor is now:
- ✅ Categorizing DMs (Setup Help, Newsletter, Product Inquiry, Partnership)
- ✅ Auto-responding with templates
- ✅ Logging to `.cache/youtube-dms.jsonl`
- ✅ Flagging interesting partnerships
- ✅ Reporting metrics (total DMs, responses sent, conversion potential)
- ✅ Running hourly via cron

---

## Files

- **Main script:** `youtube-dm-monitor-live.py`
- **Scheduler:** `cron-youtube-dm-monitor-live.sh`
- **Setup guide:** `YOUTUBE-DM-MONITOR-SETUP.md` (detailed)
- **Status:** `YOUTUBE-DM-MONITOR-STATUS.md` (checklist)
- **Logs:** `~/.cache/youtube-dms.jsonl` (all DMs)
- **Report:** `~/.cache/youtube-dm-report.json` (latest stats)
- **Cron log:** `~/.cache/youtube-dm-monitor.log` (execution history)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Playwright not installed" | `python3 -m pip install --user playwright && python3 -m playwright install` |
| DMs not fetching | Run with `--debug` flag, may need browser login first |
| Cron not running | `crontab -l` to verify, `chmod +x` script, check logs |
| Need help | Read `YOUTUBE-DM-MONITOR-SETUP.md` |

---

That's it! 🚀
