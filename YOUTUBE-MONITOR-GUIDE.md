# YouTube Comment Monitor - Quick Reference

## ⚡ Quick Start (5 minutes)

```bash
bash ~/.openclaw/workspace/.cache/youtube-monitor-install.sh
```

This will:
1. Install Python dependencies
2. Prompt for YouTube credentials
3. Ask for your channel ID
4. Run first test
5. Install cron job

---

## 📋 What It Does

**Every 30 minutes:**
- ✅ Fetches new comments from your YouTube channel
- 🏷️ Categorizes each comment automatically
- 💬 Sends auto-responses to Questions & Praise
- 🚩 Flags Sales inquiries for manual review
- 📝 Logs everything to `.cache/youtube-comments.jsonl`
- 📊 Reports stats

---

## 🏷️ Comment Categories

| Icon | Category | Auto-Respond? | Example |
|------|----------|---------------|---------|
| ❓ | **questions** | ✅ Yes | "How do I get started?" |
| 👍 | **praise** | ✅ Yes | "This is amazing!" |
| 🚫 | **spam** | ❌ No | Crypto, MLM, etc. |
| 🚩 | **sales** | ❌ No | "Partnership inquiry" |
| ℹ️ | **neutral** | ❌ No | General comments |

---

## 🔧 Commands

### Run Manually
```bash
python ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

### View Logs
```bash
# Real-time log
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log

# All comments
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq '.'

# Last 5 comments
tail -5 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq '.'
```

### Generate Reports
```bash
# All-time summary
python ~/.openclaw/workspace/.cache/youtube-monitor-report.py

# Last 2 hours
python ~/.openclaw/workspace/.cache/youtube-monitor-report.py 120

# Last 24 hours
python ~/.openclaw/workspace/.cache/youtube-monitor-report.py 1440
```

### Query Comments (jq)
```bash
# Count by category
jq -s 'group_by(.category) | map({cat: .[0].category, count: length})' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Find sales inquiries
jq 'select(.category == "sales")' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Search by author
jq 'select(.commenter | contains("John"))' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Recent 10 comments with responses
jq 'select(.response_sent == true)' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl | tail -10
```

---

## 🛠️ Configuration

**Config file:** `youtube-monitor-config.json`

```json
{
  "channel_id": "UCxxxxxxxxxxxxxxxxxxxxxx",
  "templates": {
    "questions": "Thanks for asking! ...",
    "praise": "Thank you so much! ..."
  }
}
```

**Customize:**
- Edit response templates
- Add/remove keyword detection
- Adjust category thresholds

---

## 📊 Log Files

| File | Purpose |
|------|---------|
| `youtube-comments.jsonl` | All monitored comments |
| `seen-comment-ids.json` | IDs already processed |
| `youtube-monitor.log` | Cron execution log |
| `youtube-monitor-config.json` | Configuration |

---

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Channel not found" | Check channel_id in config (format: UCxxxx...) |
| OAuth token expired | Delete `youtube-token.json`, re-run script |
| "API quota exceeded" | YouTube limits to ~10K requests/day. Wait or check quotas. |
| No new comments | Monitor checks 5 most recent videos, sorted by relevance |
| Cron not running | Check: `crontab -l` \| verify path is absolute |

---

## 📈 Metrics to Track

- **Auto-responses sent:** Questions answered automatically ✅
- **Flagged for review:** Sales inquiries requiring attention 🚩
- **Engagement rate:** % of comments getting responses
- **Category breakdown:** What types of comments you get
- **Top commenters:** Most engaged viewers

---

## 🎯 Next Steps

1. **Run setup:**
   ```bash
   bash ~/.openclaw/workspace/.cache/youtube-monitor-install.sh
   ```

2. **Wait for first run (cron runs every 30 min)**

3. **Check results:**
   ```bash
   python ~/.openclaw/workspace/.cache/youtube-monitor-report.py
   ```

4. **Review sales inquiries** flagged for manual response

5. **Customize templates** in `youtube-monitor-config.json`

---

## 📖 Full Documentation

See: `youtube-monitor-setup.md` in your workspace
