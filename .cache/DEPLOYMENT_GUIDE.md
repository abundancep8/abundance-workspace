# YouTube Comment Monitor - Deployment Guide

**Status:** ✅ Ready to deploy on schedule  
**Cron ID:** `114e5c6d-ac8b-47ca-a695-79ac31b5c076`  
**Schedule:** Every 30 minutes  
**Channel:** Concessa Obvius  

---

## Quick Start (5 minutes)

### 1. Verify Installation

```bash
ls -la /Users/abundance/.openclaw/workspace/.cache/
# Should show:
# - youtube-monitor.py
# - youtube-monitor-config.json
# - youtube-monitor-cron.sh
# - youtube-comments.jsonl
# - youtube-dashboard.py
# - YOUTUBE_MONITOR_README.md
```

### 2. Test Script

```bash
cd /Users/abundance/.openclaw/workspace/.cache
python3 youtube-monitor.py
```

**Expected output:**
```
🔍 Checking YouTube comments on Concessa Obvius...
   Found 7 total comments
   Processed 7 new comments
   ✅ Logged to JSONL

============================================================
📊 YouTube Comment Monitor Report
[stats here...]
============================================================
```

### 3. View Dashboard

```bash
python3 youtube-dashboard.py
```

**Shows:**
- Total comments processed
- Breakdown by category
- Response statistics
- Recent comments

### 4. Deploy to Cron

```bash
# Edit crontab
crontab -e

# Add this line (runs every 30 minutes):
*/30 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh >> /Users/abundance/.openclaw/workspace/.cache/logs/youtube-cron.log 2>&1

# Verify
crontab -l | grep youtube-monitor
```

---

## File Structure

```
.cache/
├── youtube-monitor.py                    # Main script
├── youtube-monitor-config.json           # Configuration (categories, keywords, templates)
├── youtube-monitor-cron.sh              # Cron wrapper
├── youtube-dashboard.py                  # Analytics dashboard
├── youtube-comments.jsonl               # Audit log (append-only)
├── youtube-monitor-stats.json           # Latest stats
├── logs/
│   ├── youtube-monitor.log             # Script output log
│   └── youtube-cron.log                # Cron execution log
├── YOUTUBE_MONITOR_README.md           # Full documentation
└── DEPLOYMENT_GUIDE.md                 # This file
```

---

## What Each Component Does

### `youtube-monitor.py`

**Purpose:** Main monitoring engine  
**Frequency:** Run every 30 minutes via cron  
**Runtime:** ~2-5 seconds (simulation mode)  

**Process:**
1. Fetch recent comments (real API or simulation)
2. Categorize each comment
3. Generate auto-responses for Q&A + Praise
4. Flag sales inquiries for review
5. Delete/block spam
6. Log everything to JSONL
7. Save statistics

### `youtube-monitor-config.json`

**Purpose:** Define categories and responses  
**Edit to:**
- Add/remove keywords
- Change auto-response templates
- Enable/disable auto-responses
- Adjust categorization rules

### `youtube-comments.jsonl`

**Purpose:** Immutable audit trail  
**Format:** One JSON record per line  
**Append:** New comments appended, never deleted  
**Size:** ~1KB per comment, grows steadily  

### `youtube-dashboard.py`

**Purpose:** Human-readable analytics  
**Outputs:**
- Total comments processed
- Category breakdown
- Response statistics
- Recent comments
- Comments by date

---

## Monitoring & Maintenance

### Daily Check

```bash
# Quick stats
python3 /Users/abundance/.openclaw/workspace/.cache/youtube-dashboard.py

# Watch for errors
tail -20 /Users/abundance/.openclaw/workspace/.cache/logs/youtube-monitor.log
```

### Weekly Review

```bash
# Count new comments
tail -100 /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l

# Review flagged items
grep '"flagged_for_review"' /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl | tail -20

# Check auto-response rate
grep '"auto_response' /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl | wc -l
```

### Monthly Cleanup

```bash
# Archive old logs
gzip /Users/abundance/.openclaw/workspace/.cache/logs/youtube-monitor.log
mv /Users/abundance/.openclaw/workspace/.cache/logs/youtube-monitor.log.gz /Users/abundance/.openclaw/workspace/.cache/logs/youtube-monitor-$(date +%Y-%m-%d).log.gz

# Backup JSONL
cp /Users/abundance/.openclaw/workspace/.cache/youtube-comments.jsonl /Users/abundance/.openclaw/workspace/.cache/youtube-comments-$(date +%Y-%m-%d).jsonl.bak
```

---

## Customization Guide

### Change Schedule

**Current:** Every 30 minutes

**To change to 15 minutes:**
```cron
*/15 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

**To change to 1 hour:**
```cron
0 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

**To change to 9 AM daily:**
```cron
0 9 * * * /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

### Add Keywords

Edit `youtube-monitor-config.json`:

```json
{
  "categories": {
    "1_questions": {
      "keywords": [
        "how do i",
        "how to",
        "where can",
        "cost",
        "timeline",
        "YOUR_NEW_KEYWORD_HERE"
      ]
    }
  }
}
```

### Custom Response Template

```json
{
  "categories": {
    "1_questions": {
      "template": "Hey! Thanks for asking. 👋\n\nHere's what I'd recommend:\n1. Check [docs link]\n2. Review [resource]\n3. Reach out if you have more questions!\n\nBuilding! 🚀"
    }
  }
}
```

### Disable Auto-Responses

```json
{
  "categories": {
    "1_questions": {
      "auto_respond": false
    }
  }
}
```

---

## Troubleshooting

### Cron Not Running

**Symptoms:** Script doesn't run at scheduled time

**Fix:**
```bash
# Check cron is running
ps aux | grep cron

# Check your crontab
crontab -l

# Verify script is executable
ls -la /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh
# Should show: -rwxr-xr-x (executable)

# Test manually
/Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh

# Check system logs (macOS)
log stream --predicate 'process == "cron"' --level debug
```

### Script Fails

**Check logs:**
```bash
tail -50 /Users/abundance/.openclaw/workspace/.cache/logs/youtube-monitor.log
```

**Common issues:**
- Python not found: `which python3` (must return a path)
- File permissions: `chmod +x youtube-monitor.py`
- Config file: Check `youtube-monitor-config.json` is valid JSON

### API Key Issues

**If using real YouTube API:**

```bash
# Set environment variable (permanent)
# Add to ~/.zshrc or ~/.bash_profile:
export YOUTUBE_API_KEY="your-key-here"

# Or set in cron (add to beginning of cron.sh):
export YOUTUBE_API_KEY="your-key-here"
/Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py
```

### No Comments Found

```bash
# Verify you're in simulation mode (expected if no API key)
grep "YOUTUBE_API_KEY" /Users/abundance/.openclaw/workspace/.cache/youtube-monitor.py

# Script automatically uses demo data if API key not set
# This is fine for testing, production should use real API
```

---

## Monitoring Success

### Healthy Symptoms

✅ Script runs every 30 minutes  
✅ New comments appear in JSONL every run  
✅ Dashboard shows increasing totals  
✅ Auto-responses increasing (Questions & Praise)  
✅ Logs are clean with no errors  
✅ Cron output shows "Run: YYYY-MM-DD HH:MM:SS"  

### Problematic Symptoms

❌ Script hasn't run in several hours  
❌ JSONL file not growing  
❌ Repeated errors in logs  
❌ Dashboard shows "Never" for last update  
❌ Cron logs show "command not found"  

---

## Metrics to Track

### Weekly
- Comments processed per 30-min interval
- Average response time (auto-responses/total)
- Spam vs. legitimate comments ratio

### Monthly
- Total comments processed
- Categories breakdown
- Flagged items for review (sales inquiries)
- Auto-response effectiveness

### Quarterly
- Trends in comment volume
- Most common question types
- ROI on auto-responses (if tracked downstream)

---

## Advanced: Real YouTube API Setup

### 1. Create Service Account

```bash
# Go to Google Cloud Console
# Create Project > Enable YouTube API v3 > Create Service Account
# Download JSON credentials

# Set env var:
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
export YOUTUBE_API_KEY="your-api-key"
```

### 2. Install Dependencies

```bash
pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 3. Test Real API

```bash
export YOUTUBE_API_KEY="your-key-here"
python3 youtube-monitor.py
# Should now fetch REAL comments instead of demo data
```

---

## Support Checklist

Before troubleshooting, verify:

- [ ] Script is executable: `ls -la youtube-monitor.py`
- [ ] Config is valid JSON: `python3 -m json.tool youtube-monitor-config.json`
- [ ] Python is installed: `which python3`
- [ ] Cron is running: `ps aux | grep cron`
- [ ] Crontab is set: `crontab -l | grep youtube`
- [ ] Directory exists: `ls -la /Users/abundance/.openclaw/workspace/.cache/`
- [ ] JSONL is writeable: `touch youtube-comments.jsonl` (succeeds)
- [ ] Test run works: `python3 youtube-monitor.py` (completes)

---

## Key Takeaways

1. **Deploy:** Add cron job (`*/30 * * * * ...`)
2. **Monitor:** Use dashboard (`python3 youtube-dashboard.py`)
3. **Maintain:** Check logs weekly, clean up monthly
4. **Customize:** Edit config as needed (no restart required)
5. **Track:** Review flagged items for sales opportunities

---

## Next Actions

- [ ] Verify all files are in place
- [ ] Run test script successfully
- [ ] Add to crontab
- [ ] Verify cron runs after 30 minutes
- [ ] Check logs for errors
- [ ] Set up weekly dashboard review
- [ ] (Optional) Set up real YouTube API

---

**Status:** Ready for production  
**Last Updated:** 2026-04-17  
**Confidence:** High ✅
