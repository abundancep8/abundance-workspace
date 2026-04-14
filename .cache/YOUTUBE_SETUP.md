# YouTube Comment Monitor Setup

## Status: Ready for Configuration

The monitoring script is ready but requires YouTube API setup before it can run.

## Prerequisites

### 1. Install Python Dependencies
```bash
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### 2. Get YouTube Data API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable "YouTube Data API v3":
   - Search for "YouTube Data API"
   - Click "Enable"
4. Create API credentials:
   - Go to "Credentials" → "Create Credentials" → "API Key"
   - Copy the API key

### 3. Set Environment Variable

Add to your shell profile (~/.zshrc or ~/.bash_profile):
```bash
export YOUTUBE_API_KEY="your-api-key-here"
```

Then reload:
```bash
source ~/.zshrc
```

## Running the Monitor

### Manual Test
```bash
python .cache/youtube-monitor.py
```

### Automated (Cron)
The cron job is already configured to run every 30 minutes.

## Output

- **Log file:** `.cache/youtube-comments.jsonl`
  - Each line is a JSON object with: timestamp, commenter, text, category, response_status
  
- **State file:** `.cache/youtube-monitor-state.json`
  - Tracks last check time to avoid duplicates

## Categories

1. **Question** - How-to, tools, cost, timeline questions
2. **Praise** - Positive, inspiring, appreciative comments
3. **Spam** - Crypto, MLM, promotional spam
4. **Sales** - Partnership, collaboration inquiries (flagged for manual review)
5. **General** - Everything else

## Auto-Responses

- **Questions**: Template response with FAQ link
- **Praise**: Thank you message
- **Sales**: Flagged for review (no auto-response)
- **Spam/General**: No response

## Current Status

**API Key:** ❌ Not configured  
**Dependency:** google-api-python-client  
**Lookback Window:** 35 minutes (30 min + 5 min buffer)

Once API key is set, the monitor will be fully operational.
