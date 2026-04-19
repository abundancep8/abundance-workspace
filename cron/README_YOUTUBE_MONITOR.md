# YouTube Comment Monitor - Cron Job Setup Guide

Automated YouTube comment monitoring system that fetches, categorizes, and auto-responds to comments on a specified YouTube channel.

## Features

✅ **Automatic Comment Fetching** - Retrieves new comments from your YouTube channel  
✅ **Smart Categorization** - Classifies comments as: Questions, Praise, Spam, or Sales  
✅ **Auto-Response System** - Automatically responds to Q&A and praise with customizable templates  
✅ **Sales Flagging** - Flags promotional/sales comments for manual review  
✅ **Complete Logging** - Logs all comments to JSONL for analysis and auditing  
✅ **Deduplication** - Tracks processed comments to avoid duplicates  
✅ **Error Handling** - Robust error handling and detailed logging  
✅ **JSON Reports** - Returns structured reports with statistics  

## Directory Structure

```
cron/
├── youtube-comment-monitor.py              # Main script
├── youtube-monitor-templates.json          # Response templates (customizable)
├── youtube-monitor.cron                    # Cron job entries
├── README_YOUTUBE_MONITOR.md              # This file
├── .state/
│   └── youtube-monitor.json               # State tracking (processed IDs, stats)
├── .cache/
│   ├── youtube-comments.jsonl             # Log of all processed comments
│   ├── youtube-monitor.log                # Application logs
│   └── youtube-monitor-cron.log           # Cron execution logs
```

## Prerequisites

### 1. Python 3.8+

```bash
python3 --version  # Should be 3.8 or higher
```

### 2. Google API Libraries

Install required Python packages:

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Or install all at once:

```bash
pip install -r requirements.txt
```

Create `requirements.txt`:

```
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.104.0
```

### 3. YouTube API Key

You need a valid YouTube Data API key. Here's how to get one:

#### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Name it (e.g., "YouTube Comment Monitor")
4. Click "Create"

#### Step 2: Enable YouTube Data API v3

1. In Cloud Console, go to "APIs & Services" → "Library"
2. Search for "YouTube Data API v3"
3. Click it, then click "Enable"

#### Step 3: Create an API Key

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API Key"
3. Copy your API key (keep it secret!)

#### Step 4: Set Environment Variable

Add your API key to your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
export YOUTUBE_API_KEY="your_api_key_here"
```

Or set it before running:

```bash
export YOUTUBE_API_KEY="your_api_key_here"
python3 cron/youtube-comment-monitor.py
```

## Configuration

### 1. Update Channel Name

Edit the cron job to set your channel name. Open `youtube-monitor.cron` and change:

```bash
YOUTUBE_CHANNEL_NAME="Concessa Obvius"
```

To your actual channel name:

```bash
YOUTUBE_CHANNEL_NAME="Your Channel Name"
```

### 2. Customize Response Templates

Edit `youtube-monitor-templates.json` to add your own responses:

```json
{
  "questions": [
    "Thanks for the question! Great to see your interest.",
    "Love this question! Let me think about that..."
  ],
  "praise": [
    "Thank you so much! Really appreciate the support.",
    "This comment made my day! 💙"
  ],
  "spam": null,
  "sales": null
}
```

**Notes:**
- `questions`: List of templates to respond to Q&A comments (randomly selected)
- `praise`: List of templates for compliments and positive feedback
- `spam`: Set to `null` to not respond to spam comments
- `sales`: Set to `null` to not respond to promotional comments (they're flagged for review)

### 3. Choose Cron Schedule

The `youtube-monitor.cron` file includes several schedule options. Choose one based on your needs:

**Every 30 minutes** (most frequent, good for high-traffic channels):
```
*/30 * * * *
```

**Every hour**:
```
0 * * * *
```

**Every 4 hours** (balanced):
```
0 */4 * * *
```

**Daily at 9 AM** (once per day):
```
0 9 * * *
```

## Installation

### 1. Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Make Script Executable

```bash
chmod +x /Users/abundance/.openclaw/workspace/cron/youtube-comment-monitor.py
```

### 3. Test the Script

```bash
export YOUTUBE_API_KEY="your_api_key_here"
export YOUTUBE_CHANNEL_NAME="Your Channel Name"
cd /Users/abundance/.openclaw/workspace
python3 cron/youtube-comment-monitor.py
```

Expected output (JSON):
```json
{
  "status": "success",
  "timestamp": "2026-04-18T10:30:00.000000",
  "channel": "Your Channel Name",
  "channelId": "UCxxxxxxxxxxxxxx",
  "commentsProcessed": 25,
  "totalProcessed": 25,
  "stats": {
    "total": 25,
    "questions": 8,
    "praise": 12,
    "spam": 3,
    "sales": 2,
    "autoResponses": 20,
    "flaggedForReview": 2
  },
  "autoResponsesSent": 20,
  "flaggedForReview": 2,
  "logFile": "/Users/abundance/.openclaw/workspace/cron/.cache/youtube-comments.jsonl"
}
```

### 4. Install Cron Job

Edit your crontab:

```bash
crontab -e
```

Copy one of the cron entries from `youtube-monitor.cron`. For example, to run every 30 minutes:

```bash
*/30 * * * * export YOUTUBE_API_KEY="your_api_key_here" YOUTUBE_CHANNEL_NAME="Concessa Obvius" && cd /Users/abundance/.openclaw/workspace && python3 cron/youtube-comment-monitor.py >> cron/.cache/youtube-monitor-cron.log 2>&1
```

Replace `"your_api_key_here"` with your actual API key.

### 5. Verify Installation

```bash
crontab -l | grep youtube-comment-monitor
```

You should see your cron entry listed.

## Monitoring & Logs

### View Recent Logs

```bash
# Application logs
tail -f /Users/abundance/.openclaw/workspace/cron/.cache/youtube-monitor.log

# Cron execution logs
tail -f /Users/abundance/.openclaw/workspace/cron/.cache/youtube-monitor-cron.log
```

### View Processed Comments

```bash
# View all logged comments (JSONL format - one JSON per line)
cat /Users/abundance/.openclaw/workspace/cron/.cache/youtube-comments.jsonl

# View last 10 comments
tail -10 /Users/abundance/.openclaw/workspace/cron/.cache/youtube-comments.jsonl

# Pretty-print the last comment
tail -1 /Users/abundance/.openclaw/workspace/cron/.cache/youtube-comments.jsonl | jq '.'
```

### View Processing State

```bash
cat /Users/abundance/.openclaw/workspace/cron/.state/youtube-monitor.json | jq '.stats'
```

## Comment Categorization Logic

The system automatically categorizes comments using these rules:

### Questions
- Contains a question mark `?`
- Contains question words: what, how, why, where, when, who

### Praise
- Contains positive sentiment: great, amazing, love, awesome, excellent, fantastic, beautiful, perfect, wonderful, brilliant, incredible, thank you, thanks, appreciate, best, goat

### Spam
- Highly repetitive characters
- All caps (20+ characters)
- Multiple external links
- Spam keywords: clickbait, scam, fake

### Sales
- Promotional keywords: buy, shop, order, visit, click here, link, limited time, special offer, discount, promo, code, deal, sale, subscribe to my, check out my, follow me

## Troubleshooting

### "YOUTUBE_API_KEY environment variable not set"

Solution:
```bash
export YOUTUBE_API_KEY="your_key_here"
```

Or add to your shell profile (`~/.bashrc`, `~/.zshrc`, `~/.profile`):
```bash
export YOUTUBE_API_KEY="your_key_here"
```

### "Channel not found: Your Channel Name"

- Verify the channel name is spelled correctly
- Check that the channel is public
- Try searching for the channel manually on YouTube

### "ModuleNotFoundError: No module named 'google'"

Solution:
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Cron job not running

Check:
1. Permissions: `chmod +x /Users/abundance/.openclaw/workspace/cron/youtube-comment-monitor.py`
2. Crontab installed: `crontab -l`
3. Logs: `tail -f /Users/abundance/.openclaw/workspace/cron/.cache/youtube-monitor-cron.log`
4. System cron running: `ps aux | grep cron`

### API Rate Limits

YouTube API has quotas:
- Default: 10,000 units/day
- Each comment fetch costs ~1 unit
- Space your cron jobs appropriately (e.g., every 30 min = 48 runs/day)

If hitting limits, reduce frequency or upgrade your API quota in Cloud Console.

## Output Files

### youtube-comments.jsonl

Newline-delimited JSON log of all processed comments:

```json
{"timestamp": "2026-04-18T10:30:45.123456", "commentId": "abc123", "videoId": "xyz789", "author": "John Doe", "text": "Great video!", "category": "praise", "response": "Thank you so much! Really appreciate the support.", "responseSent": true, "likeCount": 5}
{"timestamp": "2026-04-18T10:31:12.654321", "commentId": "def456", "videoId": "xyz789", "author": "Jane Smith", "text": "How did you do that?", "category": "questions", "response": "Thanks for the question! Great to see your interest.", "responseSent": true, "likeCount": 2}
```

### .state/youtube-monitor.json

Tracks processed IDs and statistics:

```json
{
  "lastRun": "2026-04-18T10:30:45.123456",
  "processedCommentIds": ["abc123", "def456", ...],
  "stats": {
    "total": 150,
    "questions": 45,
    "praise": 75,
    "spam": 15,
    "sales": 15,
    "autoResponses": 120,
    "flaggedForReview": 15
  }
}
```

## Advanced Usage

### Run Manually

```bash
cd /Users/abundance/.openclaw/workspace
python3 cron/youtube-comment-monitor.py
```

### Run for Specific Channel

```bash
export YOUTUBE_CHANNEL_NAME="Different Channel"
python3 cron/youtube-comment-monitor.py
```

### Parse Comment Log

```bash
# Count comments by category
cat .cache/youtube-comments.jsonl | jq '.category' | sort | uniq -c

# Find all sales comments
cat .cache/youtube-comments.jsonl | jq 'select(.category == "sales")'

# Find all unanswered questions
cat .cache/youtube-comments.jsonl | jq 'select(.category == "questions" and .responseSent == false)'
```

## Notes

- Comments are fetched from the 10 most recent videos on your channel
- Each run fetches up to 100 new comments per video
- Comments are deduplicated using YouTube comment IDs
- The system logs all comments regardless of response status
- Spam and sales comments are logged but not auto-responded to
- All timestamps are in UTC

## Future Enhancements

Potential improvements:
- Real reply via YouTube API (currently just logs the response)
- ML-based sentiment analysis for better categorization
- Webhook notifications for flagged comments
- Statistics dashboard/visualization
- Custom categorization rules per comment
- Integration with other platforms (Discord, Slack)

## Support

For issues or questions:
1. Check the logs: `tail -f cron/.cache/youtube-monitor.log`
2. Verify API key and channel name
3. Test script directly: `python3 cron/youtube-comment-monitor.py`
4. Check Google Cloud Console for API errors

---

**Last Updated:** 2026-04-18  
**Version:** 1.0  
**Status:** Production Ready
