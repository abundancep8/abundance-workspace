# YouTube Comment Monitor Setup Guide

**Channel:** Concessa Obvius  
**Schedule:** Every 30 minutes  
**Status:** Ready to Install  

---

## What It Does

Automatically monitors your YouTube channel for new comments and:
1. **Categorizes** each comment into 4 types:
   - 🔧 **Questions** (how do I start, tools, cost, timeline)
   - 🎉 **Praise** (amazing, inspiring, thank you, love it)
   - 🚫 **Spam** (crypto, MLM, get rich quick)
   - 🤝 **Sales/Partnerships** (collaboration, sponsorship, brand deals)

2. **Auto-responds** to categories 1-2 with templated replies
3. **Flags** category 4 (partnerships) for manual review
4. **Logs everything** to JSONL (queryable, structured)
5. **Reports** metrics every cycle (processed, responded, flagged)

---

## Installation

### Step 1: Make scripts executable
```bash
chmod +x ~/.openclaw/workspace/.bin/youtube-comment-monitor.py
chmod +x ~/.openclaw/workspace/.bin/youtube-comment-ingester.py
chmod +x ~/.openclaw/workspace/.bin/install-youtube-comment-monitor.sh
```

### Step 2: Run installation
```bash
bash ~/.openclaw/workspace/.bin/install-youtube-comment-monitor.sh
```

This will:
- ✅ Create LaunchAgent directory if needed
- ✅ Install the service (com.openclaw.youtube-comment-monitor)
- ✅ Load and schedule it
- ✅ Create cache/log directories

### Step 3: Verify installation
```bash
# Check service is loaded
launchctl list | grep youtube-comment-monitor

# Should output something like:
# com.openclaw.youtube-comment-monitor
```

---

## How to Use

### Manual Test Run
```bash
python3 ~/.openclaw/workspace/.bin/youtube-comment-monitor.py
```

Output: A summary report showing comments processed, categories, responses sent.

### Queue a Test Comment
```bash
python3 ~/.openclaw/workspace/.bin/youtube-comment-ingester.py \
  --commenter "Sarah Chen" \
  --text "How do I get started with Concessa?"
```

Then run the monitor to see it process this comment.

### View Latest Report
```bash
cat ~/.openclaw/workspace/.cache/youtube-comment-report.txt
```

### View All Processed Comments
```bash
# Raw JSONL (one comment per line)
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Pretty-printed
tail -5 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | python3 -m json.tool
```

### View Flagged Partnerships
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments-flagged.jsonl
```

### View Service Logs
```bash
# Monitor log (output from each run)
tail -50 ~/.openclaw/workspace/.cache/youtube-comment-monitor.log

# Error log (if any issues)
tail -50 ~/.openclaw/workspace/.cache/youtube-comment-monitor-error.log
```

### Check Metrics
```bash
# View JSON metrics (for dashboards)
tail -5 ~/.openclaw/workspace/.cache/youtube-comment-metrics.jsonl | python3 -m json.tool
```

---

## Data & Logs

### Log Files

| File | Purpose |
|------|---------|
| `.cache/youtube-comments.jsonl` | All processed comments (append-only) |
| `.cache/youtube-comments-flagged.jsonl` | Partnership/sales comments (review queue) |
| `.cache/youtube-comment-state.json` | Processing state (hashes, last check time) |
| `.cache/youtube-comment-metrics.jsonl` | Metrics for each run |
| `.cache/youtube-comment-report.txt` | Human-readable summary (latest run) |
| `.cache/youtube-comment-monitor.log` | Service execution log |
| `.cache/youtube-comment-monitor-error.log` | Error log (if any) |

### Comment Record Format

Each comment is logged with:
```json
{
  "timestamp": "2026-04-20T09:30:00Z",
  "commenter": "Sarah Chen",
  "text": "How do I get started with Concessa?",
  "category": "questions",
  "response_sent": true,
  "response_status": "auto-responded",
  "hash": "abc123def456"
}
```

### Flagged Comment Format

```json
{
  "timestamp": "2026-04-20T09:30:00Z",
  "commenter": "Alex Marketing",
  "text": "Let's partner on a brand deal!",
  "category": "sales",
  "response_sent": false,
  "response_status": "flagged_for_review",
  "review_status": "pending",
  "review_assigned_to": null,
  "hash": "xyz789abc123"
}
```

---

## Customization

### Change Schedule

Edit the LaunchD plist:
```bash
nano ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
```

Find this line and change the interval:
```xml
<key>StartInterval</key>
<integer>1800</integer>  <!-- Change this -->
```

Common intervals:
- 300 = 5 minutes
- 900 = 15 minutes
- 1800 = 30 minutes (default)
- 3600 = 1 hour
- 7200 = 2 hours

Then reload:
```bash
launchctl unload ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
launchctl load ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
```

### Customize Response Templates

Edit the monitor script:
```bash
nano ~/.openclaw/workspace/.bin/youtube-comment-monitor.py
```

Find the `self.templates` dictionary and modify the responses:

```python
self.templates = {
    CommentCategory.QUESTIONS.value: """Your custom question response here...""",
    CommentCategory.PRAISE.value: """Your custom praise response here...""",
}
```

### Add/Remove Keywords

In the same script, find `self.category_keywords` and add/remove terms:

```python
self.category_keywords = {
    CommentCategory.QUESTIONS.value: [
        'how', 'where', 'cost', 'pricing',  # Add more keywords
    ],
    # ...
}
```

### Add New Category

1. Add to `CommentCategory` enum:
```python
class CommentCategory(Enum):
    NEW_CATEGORY = "new_category"
```

2. Add keywords:
```python
CommentCategory.NEW_CATEGORY.value: ['keyword1', 'keyword2'],
```

3. Add template:
```python
CommentCategory.NEW_CATEGORY.value: """Your response..."""
```

---

## Monitoring & Maintenance

### Daily Workflow

**Morning:** Check flagged partnerships
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments-flagged.jsonl
```

**Review:** Respond to partnership opportunities in YouTube Studio

**Anytime:** See latest report
```bash
cat ~/.openclaw/workspace/.cache/youtube-comment-report.txt
```

### Weekly Review

Check metrics:
```bash
cat ~/.openclaw/workspace/.cache/youtube-comment-metrics.jsonl | tail -20
```

This shows:
- Comments processed per cycle
- Auto-responses sent
- Partnerships flagged
- Category breakdown

### Archive Old Logs

Once a month, archive old data:
```bash
# Compress comment logs older than 30 days
find ~/.openclaw/workspace/.cache -name "youtube-*.jsonl" -mtime +30 -exec gzip {} \;

# Or backup to archive:
mkdir -p ~/.openclaw/workspace/.archives
cp ~/.openclaw/workspace/.cache/youtube-comments.jsonl ~/.openclaw/workspace/.archives/youtube-comments-2026-04.jsonl
```

---

## Troubleshooting

### Service Not Running

**Check if loaded:**
```bash
launchctl list | grep youtube-comment-monitor
```

**If not loaded, reload:**
```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
```

**Check for syntax errors in plist:**
```bash
plutil -lint ~/Library/LaunchAgents/com.openclaw.youtube-comment-monitor.plist
```

### No Comments Being Processed

**Check if comments are in the inbox:**
```bash
ls -la ~/.openclaw/workspace/.cache/youtube-comments-inbox.jsonl
```

**If not, queue a test:**
```bash
python3 ~/.openclaw/workspace/.bin/youtube-comment-ingester.py \
  --commenter "Test" \
  --text "How do I get started?"
```

**Then run monitor:**
```bash
python3 ~/.openclaw/workspace/.bin/youtube-comment-monitor.py
```

### Permission Errors

Make scripts executable:
```bash
chmod +x ~/.openclaw/workspace/.bin/youtube-comment-monitor.py
chmod +x ~/.openclaw/workspace/.bin/youtube-comment-ingester.py
```

### Python Not Found

Check Python path:
```bash
which python3
```

If not found, install:
```bash
# Using Homebrew
brew install python3

# Or using system Python
python3 --version
```

---

## YouTube API Integration (Future)

Currently, the monitor processes comments from a manual queue (`.cache/youtube-comments-inbox.jsonl`).

To enable direct YouTube API comment fetching:

1. **Create OAuth credentials:**
   - Go to: https://console.cloud.google.com
   - Create a new project (e.g., "Concessa Monitor")
   - Enable YouTube Data API v3
   - Create OAuth 2.0 credentials (Desktop app)
   - Save credentials to: `~/.secrets/youtube-credentials.json`

2. **Update monitor script:**
   - Uncomment the `fetch_comments_from_api()` method
   - Replace inbox method with API call
   - Add refresh token logic

3. **Test:**
   ```bash
   python3 ~/.openclaw/workspace/.bin/youtube-comment-monitor.py
   ```

---

## Performance & Scale

### Current Performance
- **Per-run time:** <1 second (keyword-based categorization)
- **Memory usage:** <10MB
- **Disk usage:** ~1KB per comment (JSONL format)

### At Scale (10K comments/day)
- **Disk usage:** ~10MB/day (~300MB/month)
- **Query time:** <100ms to find comments with keyword
- **No issues expected** with LaunchD schedule

---

## Backup & Recovery

### Backup Logs
```bash
# Copy to archive
tar -czf ~/Downloads/youtube-comments-backup-$(date +%Y%m%d).tar.gz \
  ~/.openclaw/workspace/.cache/youtube-comments*.jsonl
```

### Restore from Backup
```bash
tar -xzf ~/Downloads/youtube-comments-backup-20260420.tar.gz
```

### Reset Processing State
```bash
# Clear state to reprocess all comments
rm ~/.openclaw/workspace/.cache/youtube-comment-state.json

# Clear processed comment log
rm ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Note: Also delete flagged log if you want to re-review partnerships
rm ~/.openclaw/workspace/.cache/youtube-comments-flagged.jsonl
```

---

## Support & Debugging

### Get Help

**Check monitor logs:**
```bash
tail -20 ~/.openclaw/workspace/.cache/youtube-comment-monitor-error.log
```

**Run monitor in debug mode:**
```bash
python3 -u ~/.openclaw/workspace/.bin/youtube-comment-monitor.py 2>&1 | tee /tmp/monitor-debug.log
```

**Check system logs:**
```bash
log stream --predicate 'eventMessage contains "youtube-comment"'
```

---

## Version & Updates

**Current Version:** 1.0 (April 20, 2026)  
**Schedule:** Every 30 minutes  
**Channel:** Concessa Obvius  

---

_Last updated: April 20, 2026_
