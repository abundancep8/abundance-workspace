# YouTube Comment Monitor - Quick Reference

## 🎯 One-Liner Start

```bash
cd ~/.openclaw/workspace/.cache/youtube_comment_monitor && python3 run.py --workspace ~/.openclaw/workspace
```

## 📝 Key Files

| File | Purpose |
|------|---------|
| `monitor.py` | Main orchestrator (14.6 KB) |
| `categorizer.py` | Comment classifier (6.0 KB) |
| `responder.py` | Auto-reply engine (4.5 KB) |
| `logger.py` | JSONL logging (6.6 KB) |
| `run.py` | CLI entry point (4.6 KB) |

## 📂 Data Files

| File | Purpose |
|------|---------|
| `youtube-comments.jsonl` | All comments (audit trail) |
| `.youtube-monitor-state.json` | Tracks last check, processed IDs |
| `youtube-comments-report.json` | Summary statistics |
| `logs/youtube-comment-monitor-*.log` | Debug logs |

## 🎯 Categories

```
1_questions  → Auto-reply with template
2_praise     → Auto-reply with template
3_spam       → Skip/delete
4_sales      → Flag for manual review
```

## ⚙️ Config

Edit: `~/.openclaw/workspace/.cache/youtube-monitor-config.json`

```json
{
  "categories": {
    "1_questions": {"keywords": ["how", "what", "cost"]},
    "2_praise": {"keywords": ["amazing", "awesome"]},
    "3_spam": {"keywords": ["crypto", "bitcoin"]},
    "4_sales": {"keywords": ["partnership", "sponsor"]}
  },
  "auto_response_templates": {
    "question_template": "Thanks for asking!...",
    "praise_template": "Thank you!..."
  }
}
```

## 🚀 Commands

```bash
# Manual run
python3 run.py --workspace ~/.openclaw/workspace --max-results 100

# Run tests
python3 test_monitor.py

# Deploy & schedule cron
./deploy.sh

# View logs
tail -f logs/youtube-comment-monitor-$(date +%Y%m%d).log

# Check latest report
cat ~/.openclaw/workspace/.cache/youtube-comments-report.json | jq .
```

## 🔍 Cron Status

```bash
# View cron job
crontab -l | grep youtube_comment_monitor

# Test manual execution
cd ~/.openclaw/workspace/.cache && python3 -m youtube_comment_monitor.run

# Check cron log
tail -f logs/youtube-monitor-cron.log
```

## 📊 API Integration

```python
from youtube_comment_monitor import YouTubeCommentMonitor

monitor = YouTubeCommentMonitor(
    config_path='~/.../youtube-monitor-config.json',
    credentials_path='~/.../youtube-credentials.json'
)
result = monitor.run(max_results=100)
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| No credentials | Set `YOUTUBE_API_KEY` or place credentials.json |
| API errors | Check Google Cloud Console quotas |
| Comments not fetching | Verify channel ID in config |
| Tests failing | Run `python3 test_monitor.py` to diagnose |

## 📈 Monitoring Checklist

- [ ] Run manual test once
- [ ] Check logs daily for 1 week
- [ ] Review report statistics
- [ ] Adjust templates based on actual comments
- [ ] Monitor cron execution via logs

## ✅ Status

✅ All 4/4 tests passing  
✅ Production-ready  
✅ Ready for deployment  

---

**Location**: `~/.openclaw/workspace/.cache/youtube_comment_monitor/`  
**Version**: 1.0.0  
**Channel**: Concessa Obvius
