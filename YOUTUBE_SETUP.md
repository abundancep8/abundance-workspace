# Quick Start: YouTube Comment Monitor

## 🚀 Setup (5 minutes)

### 1. Get API Key
```bash
# Go to: https://console.cloud.google.com
# 1. Create new project
# 2. Enable YouTube Data API v3
# 3. Create API Key (restrict to YouTube API)
# 4. Copy the key
```

### 2. Set Environment Variable
```bash
# Add to ~/.zshrc or ~/.bashrc:
export YOUTUBE_API_KEY="your-key-here"

# Then reload:
source ~/.zshrc
```

### 3. Verify Setup
```bash
python3 scripts/youtube-comment-monitor.py
```

If successful, you'll see:
```
[2026-04-20T...] Starting YouTube comment monitor...
Found X videos
Found Y new comments
============================================================
REPORT
============================================================
Total comments processed: Y
...
```

## 📊 What It Does

**Every 30 minutes**, this monitor:

1. **Fetches** new comments from Concessa Obvius channel videos
2. **Categorizes** them:
   - 🤔 **Questions** → Auto-respond with FAQ template
   - 👏 **Praise** → Auto-respond with thank you
   - 🚫 **Spam** → Log only (no response)
   - 💼 **Sales/Partnerships** → Flag for manual review
   - 📝 **Other** → Log only

3. **Logs everything** to `.cache/youtube-comments.jsonl`
4. **Reports** stats (total processed, auto-responses, flagged items)

## 🔍 Query Your Comments

```bash
# Overall stats
./scripts/query-youtube-comments.sh stats

# Last 20 comments
./scripts/query-youtube-comments.sh recent 20

# All flagged comments (review these!)
./scripts/query-youtube-comments.sh flagged

# Search for specific text
./scripts/query-youtube-comments.sh search "pricing"

# Export as CSV
./scripts/query-youtube-comments.sh export csv > comments.csv
```

## 📂 Files Created

```
workspace/
├── scripts/
│   ├── youtube-comment-monitor.py      ← Main script
│   └── query-youtube-comments.sh       ← Query tool
├── .cron/
│   └── youtube-comment-monitor         ← Cron job
├── .cache/
│   ├── youtube-comments.jsonl          ← All logged comments
│   └── youtube-monitor-state.json      ← Last run timestamp
├── YOUTUBE_MONITOR_CONFIG.md           ← Full documentation
└── YOUTUBE_SETUP.md                    ← This file
```

## 🎯 What "Auto-Response" Means

The script **categorizes and logs** responses it would send. To actually post responses to YouTube, you'd need to add the YouTube Comments API integration (separate step). For now:

- ✅ Comments are categorized correctly
- ✅ Log shows which ones would get auto-responses
- ✅ Sales inquiries are flagged for you to handle manually
- 🔄 Template responses are ready to copy+paste

## 🔧 Customization

### Change Response Templates

Edit `youtube-comment-monitor.py`, find `TEMPLATES`:

```python
TEMPLATES = {
    "question": """Your custom question response here...""",
    "praise": """Your custom praise response here...""",
}
```

### Add Detection Patterns

Edit `CATEGORY_PATTERNS` in the script to improve categorization:

```python
CATEGORY_PATTERNS = {
    "questions": [
        r'\byour.pattern\b',
        # add more regex patterns
    ],
}
```

### Change Check Interval

Edit `.cron/youtube-comment-monitor` to adjust frequency (currently 30 min).

## 📈 Example Report Output

```
============================================================
REPORT
============================================================
Total comments processed: 42
  - Questions: 15
  - Praise: 18
  - Spam: 5
  - Sales: 3
  - Other: 1
Auto-responses sent: 33
Flagged for review: 3
Logged to: .cache/youtube-comments.jsonl
============================================================
```

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| "No videos found" | Check channel name spelling in script |
| "API error" | Verify API key is set: `echo $YOUTUBE_API_KEY` |
| "No comments found" | Channel may have comments disabled or no recent activity |
| Script not running | Check cron logs: `cat .cron/logs/youtube-comment-monitor.log` |

## 📞 Next Steps

1. ✅ Set `YOUTUBE_API_KEY`
2. ✅ Test: `python3 scripts/youtube-comment-monitor.py`
3. ✅ Check: `./scripts/query-youtube-comments.sh stats`
4. ✅ Review: Look at `.cache/youtube-comments.jsonl` structure
5. ✅ Customize templates if needed
6. ✅ **Done!** Monitor runs automatically every 30 minutes

## 📚 Learn More

See `YOUTUBE_MONITOR_CONFIG.md` for full documentation.
