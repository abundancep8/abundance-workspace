# YouTube Comment Monitor - Deployment Package 📦

**Created:** 2026-04-16 05:30 AM PT  
**Status:** Ready for setup & deployment  
**Cron Schedule:** Every 30 minutes  
**Target Channel:** Concessa Obvius  

## 📋 What You Got

Complete automated YouTube comment monitoring system with:

✅ **Comment Categorization**
- Questions (How-to, tools, costs, timelines)
- Praise (Amazing, inspiring, helpful)
- Spam (Crypto, MLM, scams)
- Sales (Partnerships, collaborations)

✅ **Auto-Responses**
- Template responses for questions & praise
- Flagged comments for manual sales review
- Customizable response text

✅ **Logging & Analytics**
- JSON log of all comments (`.jsonl` format)
- Monitoring statistics (success/failure tracking)
- Report generator for insights

✅ **Cron Automation**
- Runs every 30 minutes automatically
- Minimal API quota usage (~48 units/day vs 10,000 limit)
- Error logging for troubleshooting

## 📂 Files Delivered

```
.cache/
├── youtube-monitor.py             Main monitoring script (460 lines)
├── youtube-report.py              Report generation tool (200 lines)
├── cron-youtube-monitor.json      OpenClaw cron config
├── YOUTUBE_README.md              User guide & examples
├── YOUTUBE_SETUP.md               Step-by-step setup (detailed)
├── YOUTUBE_CHECKLIST.md           Quick setup checklist
└── YOUTUBE_DEPLOYMENT.md          This file
```

## 🚀 Quickstart

### 1. Setup (45 minutes)
Follow: `cat .cache/YOUTUBE_CHECKLIST.md`

Key steps:
- Create Google Cloud project + service account
- Download credentials JSON to `~/.openclaw/credentials/youtube.json`
- Set `YOUTUBE_CHANNEL` env variable
- Install Python dependencies

### 2. Test (5 minutes)
```bash
cd ~/.openclaw/workspace
python .cache/youtube-monitor.py
```

### 3. Enable Cron (2 minutes)
```bash
crontab -e
# Add: */30 * * * * cd /Users/abundance/.openclaw/workspace && \
#        python .cache/youtube-monitor.py >> .cache/youtube-cron.log 2>&1
```

## 📊 Expected Output

### First Run
```
📊 YouTube Comment Monitor Report
──────────────────────────────────────────────────
Total comments processed: 0 new (first run, cache empty)
Auto-responses sent: 0
Flagged for review: 0

Categories:
  Question: 0
  Praise: 0
  Spam: 0
  Sales: 0
  Other: 0
──────────────────────────────────────────────────
```

### After 30+ Minutes
```
📊 YouTube Comment Monitor Report
──────────────────────────────────────────────────
Total comments processed: 5 new
Auto-responses sent: 3
Flagged for review: 1

Categories:
  Question: 3
  Praise: 1
  Spam: 0
  Sales: 1
  Other: 0
──────────────────────────────────────────────────
```

## 📈 Monitoring Examples

**View summary:**
```bash
python .cache/youtube-report.py --summary
```

**See new comments:**
```bash
python .cache/youtube-report.py --new 24      # Last 24 hours
python .cache/youtube-report.py --new 1       # Last 1 hour
```

**Flag review:**
```bash
python .cache/youtube-report.py --flagged     # All sales/partnerships
```

**Statistics:**
```bash
python .cache/youtube-report.py --stats       # Overall breakdown
```

**Raw data:**
```bash
tail -10 .cache/youtube-comments.jsonl | jq .
```

## 🔧 Customization

### Change Response Templates
Edit `youtube-monitor.py` line ~145:
```python
responses = {
    'question': "Your custom response here",
    'praise': "Your custom thank you here",
}
```

### Adjust Categorization Rules
Edit `youtube-monitor.py` line ~80 (`categorize_comment()` function):
```python
# Add more keywords for your channel's specific questions
question_keywords = ['how', 'what', ..., 'your_word_here']
```

### Use Different Channel
```bash
export YOUTUBE_CHANNEL="UC_your_channel_id"
```

## 📁 Log Files (Auto-Created)

| File | Purpose | Format |
|------|---------|--------|
| `.cache/youtube-comments.jsonl` | All comments ever logged | JSON-lines |
| `.cache/youtube-monitor.log` | Stats from each run | JSON-lines |
| `.cache/youtube-cron.log` | Cron execution output | Text |
| `.cache/youtube-cron-error.log` | Cron error messages | Text |

## 🔑 Configuration Files

| File | Purpose |
|------|---------|
| `~/.openclaw/credentials/youtube.json` | Google service account (create during setup) |
| `~/.bashrc` or `~/.zshrc` | Environment variables (add during setup) |
| `crontab` entry | Scheduler (add during setup) |

## ⚠️ Important Notes

**API Quota:**
- You get 10,000 quota units/day (free tier)
- Each run uses ~1-2 units
- 48 runs/day = ~48-96 units used (plenty of room)
- No quota issues expected

**Limitations:**
- Comments appear in YouTube API ~5-30 minutes after posting
- Auto-responses are logged but not auto-posted (would need separate auth)
- Service account needs channel membership/access to view comments

**First Run:**
- First run will have 0 new comments (cache is empty)
- After 30 min, you'll see the first batch
- Cache prevents duplicate processing

## 🐛 Troubleshooting

**"Credentials not found"**
```bash
ls ~/.openclaw/credentials/youtube.json
# If missing, follow YOUTUBE_SETUP.md step 1-12
```

**"Channel not found"**
- Verify correct channel ID: `echo $YOUTUBE_CHANNEL`
- Should start with "UC": `UCxxxxxxxxxxxxxxx`

**"No comments fetched"**
- Check API is enabled: Google Cloud Console
- Verify service account has channel access
- Try manual run: see full errors

**Cron not running**
- Verify crontab entry: `crontab -l | grep youtube`
- Check logs: `tail -100 .cache/youtube-cron.log`
- Ensure credentials file readable by cron: `chmod 600 ~/.openclaw/credentials/youtube.json`

## 📞 Support Resources

1. **Detailed setup:** `YOUTUBE_SETUP.md`
2. **Quick checklist:** `YOUTUBE_CHECKLIST.md`
3. **Full user guide:** `YOUTUBE_README.md`
4. **Script help:** `python youtube-monitor.py --help` (add if needed)

## 🎯 Success Criteria

You'll know it's working when:

- ✅ First manual run completes without errors
- ✅ Comments are logged to `.cache/youtube-comments.jsonl`
- ✅ Report shows comment counts and categories
- ✅ Cron runs automatically every 30 minutes
- ✅ Monitor log shows consistent runs
- ✅ Flagged comments appear for sales inquiries

## 🚦 Next Steps

1. **This week:** Complete setup checklist (45 min)
2. **After setup:** Run manually once & verify
3. **After verification:** Enable cron job
4. **After 1 week:** Review stats and categorization accuracy
5. **After 1 month:** Optimize response templates based on comment patterns

## 📞 Questions?

All the answers are in the included docs. Start with the checklist, then refer to the README for deeper questions.

---

**Deployed:** April 16, 2026  
**Cron Status:** Ready (disabled until you activate)  
**Next Run:** When you enable cron or run manually  
**Estimated Setup Time:** 45 minutes  
**Estimated Maintenance:** 10 minutes/week
