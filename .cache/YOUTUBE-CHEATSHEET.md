# 🎥 YouTube Monitor - Quick Reference

## Commands

### Run Monitor
```bash
python3 .cache/youtube-monitor.py
```
Fetch new comments, categorize, auto-respond, and log.

### View Analytics
```bash
python3 .cache/youtube-analytics.py
```
Detailed report with stats, timeline, top commenters.

### Export as JSON (last 10 comments)
```bash
python3 .cache/youtube-analytics.py --json 10
```

### Export as CSV
```bash
python3 .cache/youtube-analytics.py --csv > comments.csv
```

### Initial Setup
```bash
./.cache/youtube-setup.sh
```
Install deps, save credentials, set channel ID.

---

## Configuration

### Set Channel ID
```bash
export YOUTUBE_CHANNEL_ID="UCxxxxxxxxxxxxxxxxxxxxxxxx"
```

### Edit Auto-Response Templates
File: `youtube-monitor.py`
```python
TEMPLATES = {
    1: "Thanks for the question!",  # Questions
    2: "Thanks so much!",            # Praise
}
```

### Edit Categorization Logic
Function: `categorize_comment()` in `youtube-monitor.py`
- Add regex patterns for custom categories
- Adjust priority order (spam checks first, then sales, etc.)

---

## Files Reference

| File | What It Is |
|------|-----------|
| `.cache/youtube-monitor.py` | Main script |
| `.cache/youtube-analytics.py` | Analytics tool |
| `.cache/youtube-setup.sh` | Setup helper |
| `.cache/youtube-comments.jsonl` | Comment log |
| `.cache/youtube-monitor-state.json` | Last processed comment ID |
| `.cache/README-YOUTUBE.md` | Full guide (this repo) |
| `~/.openclaw/youtube-credentials.json` | API credentials (created by setup) |

---

## Categories

| # | Name | Examples | Action |
|---|------|----------|--------|
| 1 | Question | "How do I...?", "What's the cost?" | Auto-respond |
| 2 | Praise | "Amazing!", "Inspiring" | Auto-respond |
| 3 | Spam | "Buy crypto!", "Check my channel!" | Log only |
| 4 | Sales | "Partnership?", "Let's collaborate" | Flag for review |

---

## JSON Log Format

```json
{
  "timestamp": "2026-04-19T13:30:00+00:00",
  "comment_id": "Zxxxxxxxxxxxx",
  "commenter": "John Doe",
  "text": "This is amazing!",
  "category": 2,
  "response_status": "auto_response_queued"
}
```

---

## Response Statuses

- `none` — No response (spam)
- `auto_response_queued` — Template queued (questions/praise)
- `flagged_for_review` — Sales inquiry, awaiting review

---

## Cron Job

**ID:** `114e5c6d-ac8b-47ca-a695-79ac31b5c076`  
**Schedule:** Every 30 minutes  
**Command:** `python3 ~/.openclaw/workspace/.cache/youtube-monitor.py`

---

## Typical Workflow

1. **Setup once:**
   ```bash
   ./.cache/youtube-setup.sh
   ```

2. **Monitor runs automatically every 30 min**
   - Fetches comments
   - Auto-responds to Q&A
   - Flags sales inquiries

3. **Check daily:**
   ```bash
   python3 .cache/youtube-analytics.py
   ```
   Look for flagged items needing review.

4. **Customize as needed:**
   - Edit templates in `youtube-monitor.py`
   - Adjust categorization patterns
   - Enable auto-posting (requires auth)

---

## Environment Variables

```bash
# Required for monitor to run
export YOUTUBE_CHANNEL_ID="UCxxxxxxxxxxxxxxxxxxxxxxxx"

# Optional: for custom YouTube Data API quota project
export YOUTUBE_API_KEY="your-api-key-here"  # If using API key instead of OAuth
```

Add to `~/.zshrc` or `~/.bashrc` to persist.

---

## Troubleshooting Quick Fixes

| Problem | Fix |
|---------|-----|
| Credentials not found | `.cache/youtube-setup.sh` |
| No comments detected | Check channel ID and API quota |
| Import errors | `pip install google-auth-oauthlib google-api-python-client` |
| Cron not running | Check cron status: `crontab -l` |
| Comments not logging | Check `.cache/youtube-comments.jsonl` permissions |

---

**Remember:** Monitor runs every 30 minutes automatically. Manually run to test or force an immediate check.
