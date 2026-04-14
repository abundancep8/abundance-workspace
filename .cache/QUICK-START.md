# YouTube Comment Monitor - Quick Start (5 Minutes)

## Step 1: Setup Dependencies (2 min)
```bash
bash ~/.openclaw/workspace/.cache/youtube-monitor-setup.sh
```

## Step 2: Get Credentials (3 min)
1. Go to: https://console.cloud.google.com
2. Create new project → Enable YouTube Data API v3
3. Credentials → OAuth 2.0 (Desktop app) → Download JSON
4. Save to: `~/.openclaw/secrets/youtube.json`

## Step 3: Test (1 min)
```bash
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py --dry-run
```

Expected: `✓ Credentials valid`

## Step 4: Run (< 1 min)
```bash
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

## Step 5: Check Results
```bash
# View comments
tail -5 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .

# View summary
tail -30 ~/.openclaw/workspace/.cache/youtube-monitor.log
```

---

## Commands Reference

| Task | Command |
|------|---------|
| **Test Setup** | `python3 ... --dry-run` |
| **Fetch 50 comments** | `python3 ... --max-comments 50` |
| **View Help** | `python3 ... --setup` |
| **View logs** | `tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log` |
| **View comments** | `tail -10 ~/.openclaw/workspace/.cache/youtube-comments.jsonl \| jq .` |
| **Count by category** | `jq -s 'group_by(.category) \| map({category: .[0].category, count: length})' ... /youtube-comments.jsonl` |
| **Find sales** | `grep 'sales' ~/.openclaw/workspace/.cache/youtube-comments.jsonl` |

---

## Integration

### Add to Heartbeat (HEARTBEAT.md)
```yaml
- Run YouTube comment monitor
  Command: python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

### Add to Cron (every 6 hours)
```bash
crontab -e
# Add: 0 */6 * * * cd ~/.openclaw/workspace && python3 .cache/youtube-comment-monitor.py >> .cache/youtube-monitor-cron.log 2>&1
```

---

## What Gets Logged

```json
{
  "timestamp": "2026-04-13T10:23:45Z",
  "commenter": "Jane Doe",
  "text": "Amazing tutorial! 🎉",
  "category": "praise",
  "response_sent": true
}
```

Categories:
- **question** → Auto-response (helpful template)
- **praise** → Auto-response (appreciation template)
- **sales** → ⚠️ Flagged for review
- **spam** → Filtered (no response)
- **other** → Logged only

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Credentials not found` | Run setup, save JSON to `~/.openclaw/secrets/youtube.json` |
| `No comments found` | Channel may have comments disabled or no videos |
| `403 Quota Exceeded` | Check Google Cloud Console → quotas |
| Python not found | Install Python 3.8+: `brew install python3` |

---

## Files

| File | Purpose |
|------|---------|
| `youtube-comment-monitor.py` | Main script (16 KB) |
| `youtube-credentials-template.json` | Credentials template |
| `YOUTUBE-MONITOR-README.md` | Full documentation |
| `youtube-monitor-setup.sh` | Setup helper |
| `youtube-monitor-openclaw-integration.md` | OpenClaw patterns |

---

## Support

```bash
# Full README
cat ~/.openclaw/workspace/.cache/YOUTUBE-MONITOR-README.md

# Setup help
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py --setup

# Integration guide
cat ~/.openclaw/workspace/.cache/youtube-monitor-openclaw-integration.md

# Logs
tail -50 ~/.openclaw/workspace/.cache/youtube-monitor.log
```

---

**Ready in 5 minutes. Deploy with confidence.** 🚀
