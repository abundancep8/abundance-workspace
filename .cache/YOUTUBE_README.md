# YouTube Comment Monitor 🎬

Automated monitoring and categorization of YouTube channel comments with template-based auto-responses.

## Quick Start

### 1. Get YouTube API Credentials

Follow the setup guide: `cat .cache/YOUTUBE_SETUP.md`

**TL;DR:**
```bash
# Install dependencies
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Create Google Cloud project with YouTube Data API
# Download service account JSON to:
mkdir -p ~/.openclaw/credentials
# → save JSON as: ~/.openclaw/credentials/youtube.json

# Set your channel ID
export YOUTUBE_CHANNEL="UCOvviuslyTWXJSPvRCRl-rQ"  # Replace with yours
```

### 2. Test Locally

```bash
python .cache/youtube-monitor.py
```

Expected output:
```
📊 YouTube Comment Monitor Report
──────────────────────────────────────────────────
Total comments processed: 5 new
Auto-responses sent: 2
Flagged for review: 1

Categories:
  Question: 3
  Praise: 1
  Spam: 0
  Sales: 1
  Other: 0
──────────────────────────────────────────────────
```

### 3. Enable Cron (Every 30 Minutes)

**Option A: System crontab**
```bash
crontab -e

# Add this line:
*/30 * * * * cd /Users/abundance/.openclaw/workspace && \
  source ~/.bashrc && \
  python .cache/youtube-monitor.py >> .cache/youtube-cron.log 2>&1
```

**Option B: OpenClaw native cron**
```bash
# Edit the config file with your YouTube channel ID
vi .cache/cron-youtube-monitor.json

# Register with OpenClaw (when native cron support is available)
openclaw cron add .cache/cron-youtube-monitor.json
openclaw cron enable youtube-comment-monitor
```

## File Structure

```
.cache/
├── youtube-monitor.py          # Main monitoring script
├── youtube-report.py           # Report generator
├── YOUTUBE_SETUP.md            # Detailed setup guide
├── youtube-comments.jsonl      # All logged comments (auto-created)
├── youtube-monitor.log         # Monitoring statistics (auto-created)
└── youtube-cron.log            # Cron execution log (auto-created)
```

## Usage Examples

### View Latest Summary
```bash
python .cache/youtube-report.py --summary
```

### See New Comments (Last 24 Hours)
```bash
python .cache/youtube-report.py --new 24
```

### List Flagged Comments (Sales/Partnerships)
```bash
python .cache/youtube-report.py --flagged
```

### Overall Statistics
```bash
python .cache/youtube-report.py --stats
```

### Raw Comment Log
```bash
tail -20 .cache/youtube-comments.jsonl | jq .
```

## Comment Categories & Actions

| Category | Pattern Match | Auto-Response | Action |
|----------|---|---|---|
| **Question** | How, what, help, tool, cost, timeline, tutorial | ✅ Yes | Reply with FAQ template |
| **Praise** | Amazing, inspiring, love, thank you, helped me | ✅ Yes | Reply with thanks template |
| **Spam** | Crypto, bitcoin, MLM, forex, casino | ❌ No | Log & ignore |
| **Sales** | Partnership, collaboration, sponsor, brand deal | 🚩 Flag | Manual review required |
| **Other** | General comments that don't fit | ❌ No | Log only |

## JSON Log Format

Each comment is logged to `youtube-comments.jsonl` (one JSON object per line):

```json
{
  "timestamp": "2026-04-16T12:35:42Z",
  "commenter": "User Name",
  "commenter_id": "UCxxxxxxx...",
  "text": "How do I get started with this?",
  "category": "question",
  "response_status": "auto_response_sent",
  "response_template": "Great question! Thanks for asking...",
  "comment_id": "UgkxqwertyABC...",
  "likes": 5,
  "replies": 0
}
```

## Response Templates

Edit the templates in `youtube-monitor.py` (function `generate_response()`):

```python
responses = {
    'question': (
        "Great question! Thanks for asking. I'd recommend checking our FAQ at "
        "[link] or reaching out directly. Happy to help further! 🙌"
    ),
    'praise': (
        "Thank you so much! 🙏 Feedback like this keeps me going. "
        "I'm so glad this helped. Looking forward to creating more! ❤️"
    ),
}
```

Replace `[link]` with your actual FAQ/help resource.

## Monitoring Dashboard (Future)

Once you have comments logged, you can:

1. **View trending questions** → Identify common pain points
2. **Respond to sales inquiries** → Build partnerships
3. **Track praise sentiment** → Build social proof
4. **Monitor spam trends** → Adjust categorization rules
5. **Export for analysis** → CSV/JSON for deeper insights

```bash
# Convert to CSV for spreadsheet analysis
python .cache/youtube-report.py --new 7 | \
  jq -r '[.timestamp, .commenter, .category, .text] | @csv' > comments.csv
```

## Troubleshooting

### "No comments fetched"
- Verify channel ID is correct: `echo $YOUTUBE_CHANNEL`
- Check API quota: Google Cloud Console → YouTube API
- Ensure service account has channel access (Gmail + channel membership)

### "Permission denied" on JSON log
```bash
chmod 644 .cache/youtube-comments.jsonl
chmod 755 .cache
```

### Script keeps getting killed
- Cron permissions: `crontab -l` to verify entry exists
- Check cron logs: `log stream --predicate 'process == "cron"'`
- Ensure Python path in shebang: `which python3`

### API quota exceeded
- You get ~10,000 quota units/day with standard YouTube API
- Each comment fetch costs ~1-2 units
- At 30-min intervals, you use ~48 units/day (plenty of headroom)
- If exceeded: reduce frequency or request quota increase in Google Cloud Console

## Next Steps

1. ✅ Set up Google Cloud project + credentials
2. ✅ Test script locally
3. ✅ Enable cron job
4. ✅ Customize response templates
5. ✅ Review flagged comments weekly
6. 🔄 Build a dashboard (coming soon)
7. 🔄 Auto-post responses via API (requires auth flow)

## Support

- **Setup issues?** → Read `YOUTUBE_SETUP.md`
- **Script errors?** → Check `youtube-cron-error.log`
- **Comments not appearing?** → Verify channel ID & API quota
- **Want to customize?** → Edit `youtube-monitor.py` (clearly commented)

---

**Last updated:** 2026-04-16  
**Status:** Ready to deploy  
**Cron job:** Disabled (enable after setup)
