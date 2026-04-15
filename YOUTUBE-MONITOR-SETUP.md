# YouTube Comment Monitor - Setup & Configuration

**Channel:** Concessa Obvius  
**Monitor Interval:** Every 30 minutes  
**Status:** Configured (awaiting authentication)

## Quick Start

### 1. Authenticate with YouTube API

Run the authentication setup script (requires a browser window):

```bash
python3 scripts/youtube-setup-auth.py
```

This will:
- Open your browser for YouTube authorization
- Save the authentication token to `.secrets/youtube-token.json`
- Confirm the setup is complete

### 2. Test the Monitor

Run a manual test:

```bash
python3 scripts/youtube-comment-monitor.py
```

Expected output on first run:
- Scans Concessa Obvius channel for comments
- Creates `.cache/youtube-comments.jsonl` log file
- Generates summary report

### 3. Cron Configuration (Runs Every 30 Minutes)

The cron job is already configured via OpenClaw. To verify:

```bash
# Check OpenClaw cron status
openclaw cron list
```

Manual cron entry (if needed):
```
*/30 * * * * cd /Users/abundance/.openclaw/workspace && bash scripts/youtube-monitor-cron.sh
```

## How It Works

### Comment Categorization

1. **Questions** (auto-respond)
   - Detects: "how", "what", "help", "cost", "timeline", "tools"
   - Response: Helpful template + link to resources

2. **Praise** (auto-respond)
   - Detects: "amazing", "awesome", "inspiring", "thank you"
   - Response: Gratitude template

3. **Spam** (logged, no response)
   - Detects: crypto, MLM, forex, "click here"
   - Action: Logged in JSONL, not responded

4. **Sales** (flagged for review)
   - Detects: "partnership", "collaboration", "sponsorship"
   - Action: Flagged in log, awaits manual review

5. **General** (logged, no response)
   - All other comments

### Logging

Comments are logged to `.cache/youtube-comments.jsonl` with:
- Timestamp (ISO 8601)
- Commenter name
- Comment text
- Category (question, praise, spam, sales, general)
- Response status (auto_replied, flagged, logged)
- Response ID (if replied)

### State Management

The monitor tracks:
- Last check time (prevents duplicate processing)
- Processed comment IDs (idempotent across runs)
- Stored in `.cache/.youtube-monitor-state.json`

## Monitoring the Monitor

### View Recent Comments

```bash
tail -f .cache/youtube-comments.jsonl | jq .
```

### View Recent Logs

```bash
tail -f .cache/youtube-monitor.log
```

### Count Auto-Responses (This Session)

```bash
grep '"response_status": "auto_replied"' .cache/youtube-comments.jsonl | wc -l
```

### Find Flagged Sales

```bash
grep '"category": "sales"' .cache/youtube-comments.jsonl | jq .
```

## Response Templates

You can customize responses by editing the `RESPONSE_TEMPLATES` dictionary in the script:

```python
RESPONSE_TEMPLATES = {
    "question": """Thanks for the question! 🎯
{question_summary}
[Your custom message here]
—Concessa Team""",
    
    "praise": """Thank you so much! 🙏
[Your custom message here]
—Concessa Team""",
}
```

## Troubleshooting

### "invalid_client: The provided client secret is invalid."

The OAuth token has expired. Re-authenticate:

```bash
python3 scripts/youtube-setup-auth.py
```

### "Channel 'Concessa Obvius' not found"

The channel name doesn't match. Find the correct name:

```bash
# Edit the script and change CHANNEL_NAME to the exact channel name
nano scripts/youtube-comment-monitor.py
```

Look for: `CHANNEL_NAME = "Concessa Obvius"`

### No comments processed

Check:
1. Is the channel public?
2. Are there recent comments on videos?
3. Are they newer than last check time?

View state:
```bash
cat .cache/.youtube-monitor-state.json | jq .
```

## Files & Paths

```
/Users/abundance/.openclaw/workspace/
├── scripts/
│   ├── youtube-comment-monitor.py      # Main monitor script
│   ├── youtube-setup-auth.py           # Auth setup (run once)
│   └── youtube-monitor-cron.sh         # Cron wrapper
├── .secrets/
│   ├── youtube-credentials.json        # API credentials
│   └── youtube-token.json              # OAuth token (auto-created)
├── .cache/
│   ├── youtube-comments.jsonl          # Comment log (append-only)
│   ├── youtube-monitor.log             # Run logs (rotates at 5MB)
│   └── .youtube-monitor-state.json     # State tracking
└── YOUTUBE-MONITOR-SETUP.md            # This file
```

## Report Format

After each run, the monitor outputs:

```
📊 YouTube Comment Monitor Report
Time: 2026-04-14 07:30:45 (Pacific)

📈 Statistics:
  • Total comments processed: 5
  • Auto-responses sent: 3
  • Flagged for review (sales): 1
  • Net logged: 1

🔄 Next check: In 30 minutes
```

---

**Next Step:** Run `python3 scripts/youtube-setup-auth.py` to authenticate.
