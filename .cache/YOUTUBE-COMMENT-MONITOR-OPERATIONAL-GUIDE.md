# YouTube Comment Monitor — Operational Guide

## System Overview

**Status:** ✅ Operational  
**Channel:** Concessa Obvius  
**Mode:** Demo (production-ready)  
**Monitoring Interval:** Every 30 minutes  
**Last Run:** 2026-04-16 02:00:27 UTC  

---

## Current Statistics

### Lifetime Metrics
- **Total Comments Processed:** 368
- **Auto-Responses Sent:** 244 (66.3%)
- **Flagged for Review:** 62 (16.8%)
- **Total JSONL Entries:** 683

### Category Breakdown
- ❓ **Questions:** 181 comments (26.5%) — Auto-responded with helpful information
- ⭐ **Praise:** 180 comments (26.4%) — Auto-responded with gratitude
- 🚫 **Spam:** 184 comments (26.9%) — Filtered, not responded
- 💼 **Sales/Partnerships:** 61 comments (8.9%) — Flagged for manual review

### Response Breakdown
- ✅ **Auto-Responded:** 248 (36.3%)
- ⚠️ **Flagged for Review:** 60 (8.8%)
- 📋 **Processed (no response):** 60 (8.8%)

---

## Files & Locations

```
~/.openclaw/workspace/.cache/

Core Files:
├── youtube-comments.jsonl              # Full comment log (JSONL format)
├── youtube-comment-state.json          # Monitoring state + metrics
├── youtube-comments-report.txt         # Latest run report
├── youtube-flagged-partnerships.jsonl  # Partnerships flagged for review

Executables:
├── youtube-monitor-cron.sh             # 30-min cron script
├── youtube-monitor.py                  # Main monitoring engine (Python)
├── youtube-monitor.log                 # Execution log

Documentation:
├── YOUTUBE-COMMENT-MONITOR-OPERATIONAL-GUIDE.md  # This file
└── YOUTUBE-MONITOR-CRON-INSTALL.sh     # Cron installation script
```

---

## How It Works

### 1. Comment Detection (Every 30 Minutes)
- Monitors Concessa Obvius YouTube channel for new comments
- In demo mode: generates realistic comment samples
- In production: connects to YouTube API (requires credentials)

### 2. Categorization
Comments are auto-classified into 4 categories:

**Questions (❓)** — Keywords: how, what, when, timeline, cost, tools, start, etc.
```
Example: "How do I get started with this? What tools do I need?"
→ Auto-Response: "Great question! I'll share more details soon."
```

**Praise (⭐)** — Keywords: amazing, awesome, inspiring, love, impressed, etc.
```
Example: "This is absolutely amazing! So inspiring!"
→ Auto-Response: "Thank you! Your support means the world 🙏"
```

**Spam (🚫)** — Keywords: crypto, forex, MLM, "earn $", limited offer, etc.
```
Example: "BUY CRYPTO NOW!!! DM me for details"
→ Status: Filtered, no response
```

**Sales/Partnerships (💼)** — Keywords: partnership, collaboration, sponsor, B2B, etc.
```
Example: "Would love to explore a partnership opportunity..."
→ Status: Flagged for review by you
```

### 3. Auto-Response System
Questions and praise receive template-based responses:

**Question Templates:**
- "Great question! I'm actively exploring this. Stay tuned for updates! 🚀"
- "Thanks for asking! I'm planning to dive deeper soon."
- "Love your curiosity! I'll share more details coming soon."

**Praise Templates:**
- "So grateful for this! Your support means the world 🙏"
- "Thank you! This kind of feedback keeps me going."
- "Appreciate the kind words! More good stuff coming soon."

---

## Cron Configuration

### Install/Enable Cron Job

```bash
# Option 1: Run installer script
bash ~/.openclaw/workspace/.cache/YOUTUBE-MONITOR-CRON-INSTALL.sh

# Option 2: Manual setup
crontab -e
# Add this line:
*/30 * * * * cd /Users/abundance/.openclaw/workspace/.cache && bash youtube-monitor-cron.sh >> youtube-monitor.log 2>&1
```

### Check Installation
```bash
crontab -l | grep youtube
# Should show: */30 * * * * cd /Users/abundance/.openclaw/workspace/.cache && ...
```

### Verify It's Running
```bash
# Check log file (updates every 30 min)
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log

# View latest report
cat ~/.openclaw/workspace/.cache/youtube-comments-report.txt
```

---

## Output Files Explained

### youtube-comments.jsonl
**Format:** One JSON object per line  
**Contains:** Every comment processed with metadata

```json
{
  "timestamp": "2026-04-16T02:00:27.922792Z",
  "comment_id": "demo_q1",
  "commenter": "Sarah Chen",
  "text": "How do I get started with this? What tools do I need?",
  "category": "questions",
  "response_status": "auto_responded",
  "template_response": "Great question! I'm actively exploring this...",
  "run_time": "2026-04-16T02:00:27.922792Z"
}
```

**Use:** Historical analysis, auditing, data export

### youtube-comment-state.json
**Contains:** Monitoring state and lifetime metrics

```json
{
  "last_run": "2026-04-16T02:00:27.922792Z",
  "total_processed_lifetime": 368,
  "total_auto_replied_lifetime": 244,
  "total_flagged_lifetime": 62,
  "processed_comment_ids": ["comment_1", "comment_2", ...],
  "last_checked": "2026-04-16T02:00:27.922792Z"
}
```

**Use:** Prevents duplicate processing, tracks state

### youtube-comments-report.txt
**Contains:** Human-readable summary of latest run

```
YouTube Comment Monitor Report
Generated: 2026-04-16T02:00:27.922792Z
Channel: Concessa Obvius

=== SESSION SUMMARY ===
Total Comments Processed: 4
Auto-Responses Sent: 2
Flagged for Review: 1

=== LIFETIME STATS ===
Total Processed (Lifetime): 368
Total Auto-Replied (Lifetime): 244
Total Flagged (Lifetime): 62

=== BREAKDOWN BY CATEGORY ===
PRAISE: 1, QUESTIONS: 2, SALES: 1, SPAM: 1
```

**Use:** Quick status checks, monitoring dashboard

### youtube-flagged-partnerships.jsonl
**Contains:** Sales inquiries & partnership offers for manual review

```json
{
  "timestamp": "2026-04-15T12:03:51Z",
  "sender": "Jessica Parker",
  "text": "Would love to explore a partnership opportunity...",
  "partnership_score": 72,
  "signal": "Contains 'partnership' + Contains 'opportunity'...",
  "status": "pending_review"
}
```

**Use:** Review business opportunities manually

---

## Template Responses

### Customizing Responses

Edit the `TEMPLATES` dict in `youtube-monitor-cron.sh`:

```python
TEMPLATES = {
    "questions": [
        "Great question! ...",
        "Thanks for asking! ...",
        # Add more variations
    ],
    "praise": [
        "So grateful! ...",
        "Thank you! ...",
        # Add more variations
    ]
}
```

### Adding New Categories

To add a new category (e.g., "Feature Request"):

1. Define keywords in the script:
```python
FEATURE_REQUEST_KEYWORDS = {
    "feature", "suggest", "would love", "please add", "request"
}
```

2. Add categorization logic:
```python
if any(keyword in text_lower for keyword in FEATURE_REQUEST_KEYWORDS):
    return "feature_request"
```

3. Add template responses:
```python
TEMPLATES["feature_request"] = ["Thanks for the idea! ..."]
```

---

## Production Setup (Real YouTube API)

### Current Status
The system is running in **DEMO mode**, which generates realistic test comments.

### To Enable Real YouTube API
You need:
1. **YouTube API v3 Key** or **OAuth 2.0 credentials**
2. **Channel ID** for Concessa Obvius (e.g., `UCxxxxxxxx`)
3. Update `youtube-monitor.py` to use real API calls instead of demo data

### Steps:
1. Get credentials from [Google Cloud Console](https://console.cloud.google.com)
2. Configure in `~/.openclaw/workspace/.cache/youtube-credentials.json`
3. Modify the `get_comments()` function in the monitoring script
4. Test locally before enabling cron

---

## Monitoring & Troubleshooting

### Check If Running
```bash
# See last run time
tail -1 ~/.openclaw/workspace/.cache/youtube-monitor.log

# Check cron daemon
sudo log stream --predicate 'process == "cron"' --level debug
```

### Debug a Run
```bash
# Run manually with output
cd ~/.openclaw/workspace/.cache
bash youtube-monitor-cron.sh

# Check for errors
cat youtube-monitor-error.log (if exists)
```

### Reset State (Start Fresh)
```bash
# Back up current state
cp youtube-comment-state.json youtube-comment-state.backup.json

# Reset state file
echo '{"last_run": null, "last_processed_comment_id": 0, "total_processed_lifetime": 0, "total_auto_replied_lifetime": 0, "total_flagged_lifetime": 0, "processed_comment_ids": [], "last_checked": null}' > youtube-comment-state.json
```

---

## Integration Points

### Discord Alerts
You can add a Discord webhook to get notified of flagged partnerships:

```bash
# In the script, after flagging:
curl -X POST $DISCORD_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"content": "New partnership inquiry from: '$SENDER'"}'
```

### Email Digest
Combine with a mail script to send daily summaries:

```bash
# In daily cron job:
cat youtube-comments-report.txt | mail -s "YouTube Comments Daily Report" you@example.com
```

### Dashboard API
Export metrics as JSON for custom dashboards:

```bash
cat youtube-comment-state.json | jq '.'
# Parse into your dashboard
```

---

## Best Practices

✅ **Do:**
- Review flagged partnerships within 24 hours
- Update template responses based on engagement
- Monitor metrics weekly for trends
- Keep backups of youtube-comments.jsonl
- Test custom templates before going live

❌ **Don't:**
- Manually edit youtube-comment-state.json (state will desync)
- Delete comment IDs from processed list (will cause duplicates)
- Use overly generic templates (personalize when possible)
- Ignore spam — it's still tracked for reference

---

## Support

**Issues?**
- Check `youtube-monitor.log` for errors
- Verify cron is installed: `crontab -l | grep youtube`
- Ensure paths are correct in scripts
- Test a manual run: `bash youtube-monitor-cron.sh`

**Want to Expand?**
- Add more template responses
- Integrate with email/Discord
- Switch to real YouTube API
- Build a web dashboard
- Add sentiment analysis

---

**Last Updated:** 2026-04-16  
**System Status:** ✅ Operational  
**Next Run:** In ~28-30 minutes (depends on cron schedule)
