# YouTube Comment Monitor Setup

## Quick Start

The YouTube Comment Monitor runs every 30 minutes, categorizes new comments on the "Concessa Obvius" channel, auto-responds to questions and praise, and flags sales inquiries for review.

### Step 1: Install Dependencies

```bash
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

### Step 2: Get YouTube API Credentials

You need a YouTube Data API key.

#### Option A: Simple API Key (Easiest)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **YouTube Data API v3**
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy the key

Then set it in your environment:

```bash
export YOUTUBE_API_KEY="your-api-key-here"
```

#### Option B: Service Account (For More Control)

1. In Google Cloud Console, go to **Credentials**
2. **Create Credentials** → **Service Account**
3. Give it a name (e.g., "youtube-monitor")
4. Skip the optional steps
5. Create a JSON key and download it
6. Set the path:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### Step 3: Set the Channel ID (Optional)

The monitor will auto-lookup "Concessa Obvius", but you can speed it up by providing the channel ID directly:

```bash
export YOUTUBE_CHANNEL_ID="UCxxxxxxxxx"  # Replace with actual channel ID
```

Find your channel ID:
1. Go to your YouTube channel
2. Click your profile → Settings
3. Copy the channel ID from the URL or settings page

### Step 4: Test the Monitor

```bash
cd /Users/abundance/.openclaw/workspace
YOUTUBE_API_KEY="your-key" python3 .cache/youtube-monitor.py
```

You should see:
```
🎬 YouTube Comment Monitor
Channel: Concessa Obvius
Time: 2026-04-21T00:00:00.000000

✅ Channel ID: UCxxxxxxxxx
Fetching comments...

Found X new comments. Processing...

============================================================
📊 REPORT
============================================================
Processed: X
Auto-responses sent: Y
Flagged for review: Z
Log file: .cache/youtube-comments.jsonl
============================================================
```

### Step 5: Set Up Cron Job (Every 30 minutes)

Edit your crontab:

```bash
crontab -e
```

Add this line:

```
*/30 * * * * cd /Users/abundance/.openclaw/workspace && YOUTUBE_API_KEY="your-api-key" python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1
```

Or, if using a service account:

```
*/30 * * * * cd /Users/abundance/.openclaw/workspace && GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json" python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1
```

### Step 6: Monitor the Logs

Check the cron log:

```bash
tail -f .cache/youtube-monitor.log
```

View processed comments:

```bash
cat .cache/youtube-comments.jsonl | jq .
```

View comments flagged for review:

```bash
cat .cache/youtube-comments.jsonl | jq 'select(.response_status == "flagged")'
```

---

## How It Works

### Comment Categories

1. **Questions** → Auto-responds with contextual answers
   - Triggers: "how", "what", "tools", "cost", "timeline", "start", etc.
   - Example: "How do I get started?" → Responds with getting started guide link

2. **Praise** → Auto-responds with gratitude
   - Triggers: "amazing", "love", "inspiring", "great", "thanks", etc.
   - Response: Generic thank you + "more content coming soon"

3. **Spam** → Logged but ignored
   - Triggers: "crypto", "bitcoin", "mlm", "affiliate", etc.
   - Action: Flagged in log, no response

4. **Sales** → Logged for manual review
   - Triggers: "partnership", "collaboration", "sponsorship", etc.
   - Action: Response marked as "flagged" in log, you review manually

### Output Files

- **`.cache/youtube-comments.jsonl`** — All comments (append-only log)
  - Fields: timestamp, commenter, text, category, response, response_status, video_id, comment_id

- **`.cache/youtube-monitor-state.json`** — Last checked time and processed comment IDs
  - Used to avoid processing the same comment twice

- **`.cache/youtube-monitor.log`** — Cron output and debug info

### Response Templates

Customize responses in the script's `RESPONSE_TEMPLATES` dict:

```python
RESPONSE_TEMPLATES = {
    "question": "Thanks for the great question! {answer} Feel free to reach out if you need more help.",
    "praise": "Thank you so much! We're thrilled you found this valuable. More great content coming soon!",
}
```

Edit the `generate_response()` method to add custom logic for different question types.

---

## Troubleshooting

### "YOUTUBE_API_KEY env var not set"

Set your API key:

```bash
export YOUTUBE_API_KEY="your-key"
```

Or add it to your `.bashrc` / `.zshrc`:

```bash
echo 'export YOUTUBE_API_KEY="your-key"' >> ~/.zshrc
source ~/.zshrc
```

### "Could not find channel: Concessa Obvius"

Either:
1. Provide the channel ID directly via `YOUTUBE_CHANNEL_ID` env var
2. Verify the channel name is exact and the API has access

### "Failed to post response"

This can happen if:
- The API key doesn't have YouTube write permissions (use a service account with the right scopes)
- The video has comments disabled
- You're hitting rate limits

The monitor will log "failed" and keep going.

### "Rate limit exceeded"

YouTube API has strict rate limits. If you hit them:
- Increase the time between runs (default: 30 min is reasonable)
- Use a service account instead of an API key (can have higher limits)
- Request additional quota from Google Cloud Console

---

## Example Query: Find Unanswered Questions

```bash
cat .cache/youtube-comments.jsonl | jq 'select(.category == "question" and .response_status == "failed")'
```

## Example: Delete Old Entries

Keep only comments from the last 7 days:

```bash
CUTOFF=$(date -u -d "7 days ago" +%Y-%m-%dT%H:%M:%S)
cat .cache/youtube-comments.jsonl | jq --arg cutoff "$CUTOFF" 'select(.timestamp > $cutoff)' > /tmp/filtered.jsonl
mv /tmp/filtered.jsonl .cache/youtube-comments.jsonl
```
