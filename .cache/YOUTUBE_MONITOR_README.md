# 🎥 YouTube Comment Monitor

Automated comment monitoring for the **Concessa Obvius** YouTube channel. Categorizes, auto-responds, and logs all activity.

## ⚡ Quick Start

### 1. Install Dependencies
```bash
pip install google-auth-oauthlib google-api-python-client
```

### 2. Set Up YouTube API
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create project → Enable YouTube Data API v3
- Create OAuth 2.0 Desktop credentials
- Save as: `~/.openclaw/youtube-credentials.json`

### 3. Configure
Edit `.cache/youtube-monitor.py`:
```python
CHANNEL_ID = "UC..."  # Get from channel "About" tab
```

### 4. Test It
```bash
cd /Users/abundance/.openclaw/workspace
python3 .cache/youtube-monitor.py
```

You should see a report with comment counts.

### 5. Set Up Cron (Every 30 minutes)
```bash
crontab -e
```
Add this line:
```cron
*/30 * * * * cd /Users/abundance/.openclaw/workspace && python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1
```

## 📁 Files

| File | Purpose |
|------|---------|
| `youtube-monitor.py` | Main monitoring script |
| `youtube-monitor-report.py` | Analysis & reporting CLI |
| `youtube-monitor-setup.md` | Detailed setup guide |
| `youtube-comments.jsonl` | Full comment log (auto-created) |
| `youtube-monitor-state.json` | Tracking state (auto-created) |
| `youtube-monitor.log` | Cron execution log |

## 📊 Usage

### View All Comments
```bash
cat .cache/youtube-comments.jsonl | jq .
```

### Get Full Report
```bash
python3 .cache/youtube-monitor-report.py
```

### Recent Activity (Last 6 Hours)
```bash
python3 .cache/youtube-monitor-report.py recent 6
```

### Top Commenters
```bash
python3 .cache/youtube-monitor-report.py commenters 15
```

### Sales Opportunities (Flagged)
```bash
python3 .cache/youtube-monitor-report.py sales
```

### Unanswered Questions
```bash
python3 .cache/youtube-monitor-report.py questions
```

### Filter by Category
```bash
cat .cache/youtube-comments.jsonl | jq 'select(.category == "questions")'
```

### Get High-Engagement Comments
```bash
cat .cache/youtube-comments.jsonl | jq 'select(.likes > 10)' | head -20
```

## 🤖 How It Works

1. **Fetch** - Gets recent comments from 5 latest videos
2. **Categorize** - Uses regex patterns to classify:
   - **Questions** (how to, tools, cost, timeline)
   - **Praise** (amazing, inspiring, love)
   - **Spam** (crypto, MLM, suspicious links)
   - **Sales** (partnership, collaboration, brand deals)
   - **Other** (everything else)
3. **Respond** - Auto-replies to Questions & Praise with templates
4. **Flag** - Marks Sales inquiries for human review
5. **Log** - Records everything to JSONL for analysis

## ⚙️ Customization

### Edit Response Templates
In `youtube-monitor.py`, modify:
```python
TEMPLATES = {
    "question": "Your custom question response...",
    "praise": "Your custom praise response..."
}
```

### Modify Categories
Add or adjust patterns in:
```python
CATEGORIES = {
    "your_category": {
        "patterns": [r"pattern1", r"pattern2"],
        "priority": 1
    }
}
```

## 📈 Report Format

Each logged comment has:
```json
{
  "timestamp": "2026-04-20T06:30:00",          // When processed
  "comment_timestamp": "2026-04-19T22:15:00Z", // When posted
  "commenter": "User Name",
  "text": "Full comment text",
  "category": "questions|praise|spam|sales|other",
  "response_status": "none|sent|flagged",
  "likes": 5,
  "video_id": "abc123xyz"
}
```

## 🔒 Privacy & Permissions

- **Channel ID Only**: Doesn't read private/unlisted videos
- **Public Comments**: Only processes publicly visible comments
- **OAuth Scoped**: YouTube API limited to comment operations only
- **Local Logging**: All data stored locally in `.cache/`

## 📞 Support

**API Rate Limits:** 10,000 units/day. This script uses ~1,500/day at 30-min intervals (safe).

**First Run Slow?** OAuth token generation can take a minute. Subsequent runs are fast.

**Not Finding Comments?** 
- Verify CHANNEL_ID
- Check that recent videos have comments
- Wait 30 min for next cron run

## 🚀 Integration

### With HEARTBEAT.md
Add to your heartbeat checklist:
```markdown
- YouTube comments: `python3 .cache/youtube-monitor-report.py recent 6`
```

### Slack/Discord Notifications
Extend `youtube-monitor.py` to send alerts:
```python
# After response_status check:
if category == "sales":
    notify_slack(f"🚨 Sales lead from {commenter}: {text[:50]}")
```

---

**Last Updated:** April 19, 2026 | **Monitor Interval:** Every 30 minutes
