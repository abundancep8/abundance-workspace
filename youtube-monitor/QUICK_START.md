# Quick Start (5 Minutes)

Get the YouTube Comment Monitor running in 5 minutes flat.

## Step 1: Get API Key (3 minutes)

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Search for "YouTube Data API v3"
4. Click **Enable**
5. Go to Credentials → **+ Create Credentials** → **API Key**
6. Copy your key

## Step 2: Test Locally (1 minute)

```bash
cd youtube-monitor
YOUTUBE_API_KEY="your_api_key_here" python verify_setup.py
```

Should see ✓ green checkmarks. If red ✗, see SETUP.md.

## Step 3: First Run (1 minute)

```bash
YOUTUBE_API_KEY="your_api_key_here" python youtube_comment_monitor.py
```

Look for:
```
Processed: 12 | Auto-responses: 5 | Flagged for review: 2
```

## Step 4: Set Up Cron (Optional)

Every 30 minutes:

```bash
*/30 * * * * YOUTUBE_API_KEY="your_api_key_here" python /path/to/youtube_comment_monitor.py
```

Or use the wrapper:

```bash
chmod +x run_monitor.sh
*/30 * * * * /path/to/youtube_comment_monitor/run_monitor.sh
```

## Done! ✅

Check logs:
```bash
tail -f .cache/youtube-monitor.log
```

See README.md for full docs.
