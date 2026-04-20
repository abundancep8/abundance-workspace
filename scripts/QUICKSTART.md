# 🚀 YouTube Comment Monitor - Quick Start

Get the monitor running in 5 minutes.

## Step 1: Install Dependencies
```bash
cd /Users/abundance/.openclaw/workspace
pip install google-auth-oauthlib google-api-python-client
```

## Step 2: Get Credentials (2 minutes)

### Get API Key
1. Visit https://console.cloud.google.com/
2. Create new project (or use existing)
3. Enable **YouTube Data API v3**
4. Create **API Key** credential
5. Copy the key

### Get Channel ID
1. Go to your YouTube channel
2. Copy the ID from URL: `https://www.youtube.com/channel/UCxxxxxxxxxx`

## Step 3: Configure

Option A - Environment Variables:
```bash
export YOUTUBE_API_KEY="paste-your-key-here"
export YOUTUBE_CHANNEL_ID="UCxxxxxxxxxx"
```

Option B - .env File:
```bash
cat > .env << EOF
YOUTUBE_API_KEY=paste-your-key-here
YOUTUBE_CHANNEL_ID=UCxxxxxxxxxx
EOF
```

## Step 4: Test
```bash
python scripts/youtube-comment-monitor.py
```

Expected output:
```
============================================================
YOUTUBE COMMENT MONITOR REPORT
============================================================
Timestamp: 2026-04-20T06:00:00.000000
Channel: UCxxxxxxxxxx

Comments Processed: 5
  - Questions: 2
  - Praise: 2
  - Spam (filtered): 1
  - Sales/Partnerships: 0
  - Uncategorized: 0

Auto-Responses Sent: 4
Flagged for Review: 0
Log File: .cache/youtube-comments.jsonl
Review File: .cache/youtube-review.txt
============================================================
```

## Step 5: Automate with Cron

```bash
crontab -e
```

Add this line (runs every 30 minutes):
```
*/30 * * * * /Users/abundance/.openclaw/workspace/scripts/youtube-monitor-cron.sh >> /Users/abundance/.openclaw/workspace/.cache/monitor.log 2>&1
```

Save and exit.

## Step 6: Monitor

Check status anytime:
```bash
bash scripts/youtube-monitor-status.sh
```

View recent comments:
```bash
tail -5 .cache/youtube-comments.jsonl | jq .
```

View flagged for review:
```bash
cat .cache/youtube-review.txt
```

## That's It! 🎉

Your monitor is now:
- ✅ Running every 30 minutes
- ✅ Categorizing comments
- ✅ Auto-replying to questions & praise
- ✅ Flagging partnerships for review
- ✅ Logging everything to `.cache/youtube-comments.jsonl`

## Troubleshooting

**"Script doesn't run from cron"**
- Check: `tail .cache/monitor.log`
- Run manually: `bash scripts/youtube-monitor-cron.sh`

**"Permission denied" replying to comments**
- API Key doesn't support replies
- Either: Use OAuth 2.0 or disable auto-reply

**"No comments found"**
- Verify YOUTUBE_CHANNEL_ID is correct
- Wait for new comments on your videos

**"Rate limited"**
- YouTube API quota hit
- Wait 24h or upgrade quota in Google Cloud Console

## Files Created

```
scripts/
  ├── youtube-comment-monitor.py        # Main script
  ├── youtube-monitor-cron.sh           # Cron wrapper
  ├── youtube-monitor-status.sh         # Status check
  ├── YOUTUBE-MONITOR-README.md         # Full docs
  ├── youtube-monitor-setup.md          # Setup guide
  └── QUICKSTART.md                     # This file

.cache/
  ├── youtube-comments.jsonl            # All comments (log)
  ├── youtube-review.txt                # Flagged for review
  ├── youtube-monitor.json              # Internal state
  └── monitor.log                       # Cron output

.env.youtube-example                    # Config template
```

## Next Steps

1. Customize response templates in `scripts/youtube-comment-monitor.py`
2. Add more keywords for better categorization
3. Review flagged comments in `.cache/youtube-review.txt` daily
4. Check stats: `bash scripts/youtube-monitor-status.sh`

## Full Documentation

See `scripts/YOUTUBE-MONITOR-README.md` for:
- Detailed customization
- API limits & scaling
- Security best practices
- Advanced usage

---

**Questions?** Check the README or run the status script.
