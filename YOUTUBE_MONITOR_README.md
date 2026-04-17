# YouTube Comment Monitor - Concessa Obvius

A complete, production-ready YouTube comment monitoring system that fetches comments from the Concessa Obvius channel, categorizes them intelligently, and auto-responds to specific categories.

## Features

✅ **Automatic Comment Fetching**
- Monitors the Concessa Obvius YouTube channel
- Fetches comments from videos uploaded in the last 30 minutes
- Tracks processed comments to avoid duplicates

✅ **Smart Categorization**
- **Questions (1)**: How-to, tools, cost, timeline, startup advice
- **Praise (2)**: Amazing, inspiring, great, love, etc.
- **Spam (3)**: Crypto, MLM, blackhat, get-rich-quick schemes
- **Sales (4)**: Partnership, collaboration, sponsorship, business inquiries

✅ **Auto-Response System**
- Responds to Questions with: "Thanks for the question! Check our FAQ at [link] or reply with specifics."
- Responds to Praise with: "Thank you so much! Really appreciate the support 🙏"
- Flags Sales inquiries for manual review (no auto-response)
- Skips spam completely

✅ **Comprehensive Logging**
- `.cache/youtube-comments.jsonl` - All comments with metadata (ISO timestamps, comment IDs, categories)
- `.cache/youtube-processed.json` - Set of processed comment IDs (prevents duplicates)
- `.cache/youtube-errors.log` - All API errors and system issues
- `.cache/youtube-report-[timestamp].txt` - Formatted report with statistics

✅ **Error Handling**
- Validates API key at startup
- Clear errors if channel not found
- Graceful API error handling with logging
- Detailed error messages to stderr + log file

## Setup

### 1. Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the YouTube Data API v3
4. Create an OAuth 2.0 API key or service account
5. Copy your API key

### 2. Set Environment Variable

```bash
export YOUTUBE_API_KEY="your-api-key-here"
```

Or add to `~/.zshrc` or `~/.bashrc`:
```bash
echo 'export YOUTUBE_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Run the Monitor

```bash
cd /Users/abundance/.openclaw/workspace
python3 youtube_monitor.py
```

## Output Files

All outputs go to `.cache/` directory:

### `youtube-comments.jsonl` (Line-delimited JSON)
```json
{"timestamp": "2026-04-16T19:30:44Z", "comment_id": "Ugx...", "commenter": "John Doe", "text": "How do you handle X?", "category": 1, "response_status": "sent"}
{"timestamp": "2026-04-16T19:31:02Z", "comment_id": "Ugx...", "commenter": "Jane Smith", "text": "This is amazing!", "category": 2, "response_status": "sent"}
```

### `youtube-processed.json`
```json
{
  "comment_ids": ["Ugx...", "Ugx...", "Ugx..."]
}
```

### `youtube-report-[timestamp].txt`
```
╔════════════════════════════════════════════════════════════════════╗
║          YouTube Comment Monitor Report                            ║
║          Channel: Concessa Obvius                                  ║
║          2026-04-16T19:30:44.059519                                ║
╚════════════════════════════════════════════════════════════════════╝

📊 SUMMARY
Total Comments Processed:      42

📂 CATEGORIZATION
  Questions (1):               15
  Praise (2):                  18
  Spam (3):                    5
  Sales Inquiries (4):         4

🤖 AUTO-RESPONSES
  Sent to Questions:           15
  Sent to Praise:              18
  Total Auto-Responses:        33

🚨 MANUAL REVIEW
  Flagged for Review:          4

⚠️  FILTERING
  Spam Filtered:               5

🔧 SYSTEM
  Errors:                      0
```

## Automation Options

### Option 1: Cron Job (Every 30 minutes)

```bash
crontab -e
```

Add line:
```
*/30 * * * * export YOUTUBE_API_KEY="your-api-key" && cd /Users/abundance/.openclaw/workspace && python3 youtube_monitor.py
```

### Option 2: OpenClaw Cron (Recommended)

In your OpenClaw workspace, create a cron task:
```
0 */30 * * * * /Users/abundance/.openclaw/workspace/youtube_monitor.py
```

### Option 3: Manual Execution

Run anytime:
```bash
python3 youtube_monitor.py
```

## API Requirements

The script uses these YouTube Data API endpoints:
- `youtube.search` - Find channel by name
- `youtube.channels` - Get channel uploads playlist
- `youtube.playlistItems` - Get recent videos
- `youtube.commentThreads` - Get comments from videos
- `youtube.comments` - Post replies to comments

**Note:** Posting replies requires proper OAuth authentication and the channel owner's permission.

## Troubleshooting

### "YOUTUBE_API_KEY environment variable is not set"
```bash
export YOUTUBE_API_KEY="your-key-here"
```

### "Channel 'Concessa Obvius' not found"
- Verify channel name spelling
- Check channel exists on YouTube
- Ensure API has permission to search channels

### "YouTube API error: 403"
- API key may be invalid or expired
- Check YouTube Data API is enabled in Google Cloud
- Verify quota limits not exceeded

### Comments not being fetched
- Check `.cache/youtube-errors.log` for details
- Verify channel has recent videos (last 30 minutes)
- Ensure API key has proper permissions

## Files

- `youtube_monitor.py` - Main script (self-contained, no external deps except requests)
- `YOUTUBE_MONITOR_README.md` - This documentation
- `.cache/youtube-comments.jsonl` - Comment history
- `.cache/youtube-processed.json` - Duplicate prevention
- `.cache/youtube-errors.log` - Error log
- `.cache/youtube-report-*.txt` - Reports

## Dependencies

```bash
pip install requests
```

Or install globally:
```bash
pip3 install requests
```

The script uses only standard library + requests (no heavy dependencies).

## Notes

- Comments are fetched from videos uploaded in the last **30 minutes**
- Auto-responses are posted as **replies to comments** (nested under original comment)
- Processed comment IDs are stored to avoid duplicate responses
- All timestamps are in **ISO 8601 format** (UTC)
- Reports include visual formatting with Unicode box-drawing characters

## Security

- API key should be stored in environment variables, never in code
- Responses are posted publicly under the channel owner's account
- Ensure proper OAuth authentication before posting replies
- Monitor `.cache/youtube-errors.log` for suspicious activity

## Future Enhancements

- [ ] Webhook integration for real-time notifications
- [ ] Dashboard with comment analytics
- [ ] Custom categorization rules per video
- [ ] Sentiment analysis for finer-grained categorization
- [ ] Integration with Discord/Slack for alerts
- [ ] Support for channel members-only comments
- [ ] Bulk export to CSV/Excel

---

Built with ❤️ for Concessa Obvius community engagement.
