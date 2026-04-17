# YouTube DM Monitor - Setup Summary

**Date Created:** 2026-04-16  
**Status:** Ready to configure  
**Cron Job ID:** c1b30404-7343-46ff-aa1d-4ff84daf3674

## What Was Built

A Python-based automated system to monitor, categorize, and auto-respond to Concessa Obvius YouTube channel DMs.

### Features

✅ **DM Categorization** - 4 categories:
- Setup Help (how-to, confused, errors)
- Newsletter (email list, updates)
- Product Inquiry (buy, pricing, selection)
- Partnership (collaborate, sponsor)

✅ **Auto-Response** - Templated replies for each category

✅ **Logging** - All DMs saved to `.cache/youtube-dms.jsonl` with:
- Timestamp
- Sender
- Original text
- Category
- Response sent

✅ **Reporting** - Hourly report with:
- Total DMs processed
- Auto-responses sent
- Breakdown by category
- Partnership flags (for manual review)
- Conversion potential (product inquiries × 15% assumed rate)

## Files Created

| File | Purpose |
|------|---------|
| `scripts/youtube-dm-monitor.py` | Main Python script (1,100+ lines) |
| `scripts/youtube-dm-monitor-launcher.sh` | Cron wrapper with logging |
| `scripts/youtube-dm-status.sh` | Quick status/reporting dashboard |
| `docs/YOUTUBE-DM-MONITOR-SETUP.md` | Full setup & integration guide |
| `.cache/youtube-dms.jsonl` | DM log (created on first run) |
| `.cache/youtube-dm-report.txt` | Latest report (created on first run) |

## Next Steps to Enable

### 1. Set Up Google OAuth
- Create Google Cloud project
- Enable YouTube Data API v3
- Download OAuth credentials → `.cache/youtube-credentials.json`
- See: `docs/YOUTUBE-DM-MONITOR-SETUP.md` (Step 1-2)

### 2. Install Dependencies
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. Test Manually
```bash
python ~/.openclaw/workspace/scripts/youtube-dm-monitor.py
```
(First run will open browser for OAuth auth)

### 4. Add to Crontab
```bash
crontab -e
```
Add line:
```
0 * * * * bash ~/.openclaw/workspace/scripts/youtube-dm-monitor-launcher.sh
```

## Important Notes

### YouTube API Limitation
YouTube doesn't expose channel DMs via the public API. Script supports three integration modes:
1. **Community Tab Polling** (recommended) - uses standard YouTube API
2. **Manual CSV Import** - export from YouTube Studio periodically
3. **YouTube Partner Webhooks** (premium) - if eligible

See setup doc for detailed integration options.

## Customization

Edit `scripts/youtube-dm-monitor.py` to:
- Change channel name: Line ~35 `CHANNEL_NAME = "Concessa Obvius"`
- Customize responses: Lines ~60-85 in `TEMPLATES` dict
- Adjust keywords: `categorize_dm()` method around line ~140

## Monitoring

Check status anytime:
```bash
bash ~/.openclaw/workspace/scripts/youtube-dm-status.sh
```

Query DMs:
```bash
# View partnerships
jq 'select(.category == "partnership")' ~/.openclaw/workspace/.cache/youtube-dms.jsonl

# Count by category
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' \
  ~/.openclaw/workspace/.cache/youtube-dms.jsonl
```

## Test Run Results

Script includes placeholder data for testing. Sample report output:
```
📊 SUMMARY
  Total DMs processed: 3
  Auto-responses sent: 3

📂 BY CATEGORY
  • Setup Help: 1
  • Product Inquiry: 1
  • Partnership: 1

💰 CONVERSION POTENTIAL
  Product inquiries: 1
  Est. conversion (15%): 0.2 potential customers
```

---

**Status:** Ready to integrate with YouTube API. Waiting for OAuth credentials setup.
