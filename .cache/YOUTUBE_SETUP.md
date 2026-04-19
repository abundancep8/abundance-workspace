# YouTube Comment Monitor - Setup Guide

## Prerequisites

1. **Python 3.8+**
2. **pip** (Python package manager)

## Step 1: Install Dependencies

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Step 2: Set Up YouTube API Credentials

### 2a. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Select a Project" → "New Project"
3. Enter project name: `YouTube Comment Monitor`
4. Click "Create"

### 2b. Enable YouTube Data API v3

1. In the Cloud Console, go to "APIs & Services" → "Library"
2. Search for "YouTube Data API v3"
3. Click it and press "Enable"

### 2c. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. You may need to configure the OAuth consent screen first:
   - Click "Configure Consent Screen"
   - Choose "External" user type
   - Fill in the form (app name = "YouTube Comment Monitor")
   - Add scopes: Search for "YouTube Data API v3" and select `https://www.googleapis.com/auth/youtube.force-ssl`
   - Save and continue

4. Back to credentials, create "OAuth 2.0 Client ID":
   - Application type: **Desktop application**
   - Click "Create"
   - Click "Download" (JSON)

### 2d. Install Credentials

```bash
# Save the downloaded JSON file to:
mkdir -p ~/.openclaw
mv ~/Downloads/client_secret_*.json ~/.openclaw/youtube-credentials.json
```

## Step 3: Test the Monitor

```bash
cd ~/.openclaw/workspace
python3 .cache/youtube-monitor.py
```

**First run:** You'll be prompted to authorize in your browser. This creates a token file.

## Step 4: Set Up Cron Job

### Using OpenClaw's cron system:

The monitor is configured as a cron task that runs every 30 minutes. It will:
1. Fetch new comments from the channel
2. Categorize them
3. Auto-respond to questions and praise
4. Flag sales inquiries for review
5. Log everything to `.cache/youtube-comments.jsonl`

### Manual cron (alternative):

```bash
# Edit crontab
crontab -e

# Add this line (runs every 30 minutes):
*/30 * * * * cd ~/.openclaw/workspace && python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1
```

## Step 5: Check Results

```bash
# View comment log (JSONL format)
tail -f .cache/youtube-comments.jsonl

# View latest report
tail -20 .cache/youtube-monitor.log
```

## Customization

### Auto-Response Templates

Edit the `TEMPLATES` dict in `youtube-monitor.py`:

```python
TEMPLATES = {
    'question': "Your custom question response...",
    'praise': "Your custom praise response..."
}
```

### Categorization Rules

Modify `CATEGORY_RULES` to customize keyword-based categorization:

```python
CATEGORY_RULES = {
    'spam': {
        'keywords': [...],
        'phrases': [...]
    },
    'sales': {
        'keywords': [...],
        'phrases': [...]
    }
}
```

### Channel Name

Change this line:

```python
CHANNEL_NAME = "Your Channel Name"
```

## Troubleshooting

### "youtube-credentials.json not found"
- Ensure you downloaded the OAuth JSON and saved it to `~/.openclaw/youtube-credentials.json`
- Check the path is correct: `ls ~/.openclaw/youtube-credentials.json`

### "Channel not found"
- Verify the channel name matches exactly (case-insensitive but spelling must match)
- Try searching for the channel on YouTube and copying its exact name

### "HttpError 403"
- YouTube API quotas exceeded (YouTube Data API v3 has daily quota limits)
- Check your quota usage in Google Cloud Console → APIs & Services → YouTube Data API v3 → Quotas
- Default quota: 10,000 units/day

### "No new comments found"
- This is normal if the monitor just ran recently
- Check `.cache/youtube-monitor-state.json` to see when it last ran
- The state file tracks already-processed comments to avoid duplicates

## API Quota Costs

Each operation costs quota units:
- **Search for channel:** 100 units
- **Get channel uploads:** 1 unit
- **List playlist items:** 1 unit per video checked
- **Get comments:** 1 unit per 100 comments

**Recommendation:** With 10,000 units/day, this monitor can process ~500-1000 comments daily. If you exceed quota, increase the `maxResults` in `fetch_new_comments()` or reduce check frequency.

## Architecture

```
youtube-monitor.py
├── YouTubeCommentMonitor class
│   ├── _authenticate() → OAuth2 flow
│   ├── get_channel_id() → Search for channel
│   ├── fetch_new_comments() → Get new comments from latest videos
│   ├── categorize_comment() → Rules-based categorization
│   ├── auto_respond() → Queue responses (questions/praise)
│   ├── log_comment() → Write to JSONL
│   └── run() → Main loop
├── State tracking (.cache/youtube-monitor-state.json)
├── Comment logging (.cache/youtube-comments.jsonl)
└── Cron execution (every 30 minutes)
```

## Log Format

Comments are logged as JSONL (one JSON object per line):

```json
{
  "timestamp": "2026-04-19T01:00:00.123456",
  "comment_id": "xyz123",
  "video_id": "abc456",
  "commenter": "John Doe",
  "text": "This is amazing! How did you...",
  "category": "question",
  "response_status": "queued"
}
```

## Next Steps

- [ ] Set up Google Cloud credentials
- [ ] Test the monitor manually
- [ ] Review auto-response templates
- [ ] Customize categorization rules
- [ ] Enable cron job
- [ ] Monitor `.cache/youtube-comments.jsonl` for results
