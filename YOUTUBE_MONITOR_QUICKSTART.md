# ⚡ YouTube Monitor - Quick Start Checklist

**Objective:** Monitor Concessa Obvius channel, auto-respond to comments, flag sales inquiries.

**Status:** ✅ System created | ⏳ Awaiting credentials | ⏸️ Not active yet

---

## 🎯 Activation Checklist

### Step 1: Get YouTube API Credentials _(5 minutes)_

- [ ] Go to [Google Cloud Console](https://console.cloud.google.com/)
- [ ] Create new project or select existing one
- [ ] Enable **YouTube Data API v3**
- [ ] Create **OAuth 2.0 Desktop** credentials
- [ ] Download JSON file
- [ ] Save to: `.cache/youtube-credentials.json`

**💡 Tip:** Detailed guide in `docs/youtube-monitor-setup.md`

### Step 2: Install Dependencies _(1 minute)_

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

- [ ] Confirm installation: `pip list | grep google`

### Step 3: First Run & Authentication _(2 minutes)_

```bash
python3 scripts/youtube-monitor.py
```

What happens:
- Browser opens for authentication
- Token saved automatically
- First comments processed
- Report displayed

- [ ] Authenticated successfully
- [ ] Can see comments in `.cache/youtube-comments.jsonl`

### Step 4: Check Dashboard _(1 minute)_

```bash
python3 scripts/youtube-stats.py
```

See stats:
- Total comments processed
- Auto-responses sent
- Flagged for review

- [ ] Dashboard working

### Step 5: Confirm Cron Setup _(automatic)_

The cron job is **already configured** to run every 30 minutes.

- [ ] Monitor running every 30 minutes
- [ ] Can verify by checking `.cache/youtube-state.json` timestamp

---

## 📊 What You Get

### ✅ Auto-Responses
- **Questions** (how, what, cost, tools, timeline) → Auto-reply
- **Praise** (amazing, inspiring, love, great) → Auto-reply

### 📌 Manual Review
- **Sales** (partnership, sponsor, collaboration) → Flagged in `.cache/youtube-comments.jsonl`
- **Spam** (crypto, mlm, bitcoin) → Logged but not responded

### 📈 Logging
Every comment logged with:
- Timestamp, author, text
- Category, response status
- Video ID, comment ID

### 📉 Reporting
- Dashboard shows: processed, auto-responses, flagged
- Breakdown by category
- 7-day activity history

---

## 🔧 Customization

### Change Auto-Response Templates

Edit `.youtube-monitor.config.json`:

```json
"auto_responses": {
  "question": "Your custom question response...",
  "praise": "Your custom praise response..."
}
```

Or edit `scripts/youtube-monitor.py` → `RESPONSES` dict.

### Add/Change Keywords

Edit `.youtube-monitor.config.json` → `categorization`:

```json
"question_keywords": ["how", "what", "cost", ...],
"praise_keywords": ["amazing", "inspiring", ...]
```

### Adjust Check Frequency

Edit `.youtube-monitor.config.json`:

```json
"check_interval_minutes": 30  // Change to 15, 60, etc.
```

---

## 🚀 Files Reference

| File | Purpose |
|------|---------|
| `scripts/youtube-monitor.py` | Main monitoring script |
| `scripts/youtube-stats.py` | Statistics dashboard |
| `scripts/youtube-monitor.sh` | Cron wrapper script |
| `.youtube-monitor.config.json` | Configuration file |
| `.cache/youtube-comments.jsonl` | All comments (append-only log) |
| `.cache/youtube-state.json` | Last check time, processed IDs |
| `YOUTUBE_MONITOR.md` | Full documentation |
| `docs/youtube-monitor-setup.md` | Setup guide with troubleshooting |

---

## ⚡ Quick Commands

```bash
# View today's comments
tail -20 .cache/youtube-comments.jsonl | jq

# View sales inquiries (flagged for review)
cat .cache/youtube-comments.jsonl | jq 'select(.response_status=="flagged")'

# Count by category
cat .cache/youtube-comments.jsonl | jq -r '.category' | sort | uniq -c

# Get dashboard stats
python3 scripts/youtube-stats.py

# Run monitor manually (also tests setup)
python3 scripts/youtube-monitor.py

# Check last run time
jq '.last_check' .cache/youtube-state.json
```

---

## ✅ Success Criteria

- [ ] Credentials file in place
- [ ] Dependencies installed
- [ ] First run completed successfully
- [ ] Comments appearing in log file
- [ ] Dashboard shows stats
- [ ] Cron running (every 30 min)
- [ ] Auto-responses being sent to questions/praise
- [ ] Sales inquiries flagged for review

---

## 🆘 Troubleshooting

**Problem:** "Credentials not found"
→ Download from Google Cloud Console, save to `.cache/youtube-credentials.json`

**Problem:** "Channel not found"
→ Verify channel name is exactly "Concessa Obvius" in config

**Problem:** "Token expired"
→ Delete `.cache/youtube-token.json`, run monitor again

**Problem:** "Nothing happening"
→ Check `.cache/youtube-state.json` for `last_check` timestamp

**More help:** See `docs/youtube-monitor-setup.md`

---

## 📈 Once You're Up and Running

### Daily
- Monitor runs automatically every 30 min
- Check dashboard: `python3 scripts/youtube-stats.py`

### Weekly
- Review flagged sales inquiries
- Adjust response templates as needed
- Check API usage: https://console.cloud.google.com/apis/dashboard

### As Needed
- Edit keywords in config file
- Update channel name if monitoring different channel
- Export logs for analysis

---

**Ready?** Start with Step 1 above. Takes ~10 minutes total. 🚀

**Questions?** Check `YOUTUBE_MONITOR.md` or `docs/youtube-monitor-setup.md`
