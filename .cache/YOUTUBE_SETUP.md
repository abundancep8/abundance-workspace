# YouTube Comment Monitor Setup

## Prerequisites

1. **YouTube API Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable the YouTube Data API v3
   - Create an API key (or OAuth2 credentials)

2. **Find Your Channel ID**
   - Visit your channel
   - Look at the URL: `youtube.com/channel/UC...`
   - Copy the ID part

3. **Python Dependencies**
   ```bash
   pip install google-api-python-client
   ```

## Configuration

Set environment variables in your shell profile or cron environment:

```bash
export YOUTUBE_API_KEY="your_api_key_here"
export YOUTUBE_CHANNEL_ID="UCxxxxxxxxxxxxx"
```

## Files

- `youtube-monitor.py` - Main monitoring script
- `youtube-comments.jsonl` - Log file (auto-created)
- `youtube-monitor-state.json` - State tracking (auto-created)

## Manual Test

```bash
cd /Users/abundance/.openclaw/workspace
python3 .cache/youtube-monitor.py
```

## Cron Setup (Every 30 minutes)

Add to crontab with:
```bash
crontab -e
```

Then add:
```cron
*/30 * * * * export YOUTUBE_API_KEY="your_key"; export YOUTUBE_CHANNEL_ID="your_id"; cd /Users/abundance/.openclaw/workspace && python3 .cache/youtube-monitor.py >> .cache/youtube-monitor.log 2>&1
```

## Template Customization

Edit the `RESPONSES` dict in `youtube-monitor.py`:

```python
RESPONSES = {
    "question": {
        "template": "Your custom question response template...",
        "enabled": True
    },
    "praise": {
        "template": "Your custom praise response template...",
        "enabled": True
    }
}
```

## Logs

- **JSONL Log**: `.cache/youtube-comments.jsonl` (one JSON object per line)
- **Run Log**: `.cache/youtube-monitor.log` (when run via cron)
- **State**: `.cache/youtube-monitor-state.json` (tracks last_check time)

## Categories

1. **Question** - How-to, tools, costs, timelines → Auto-respond with template
2. **Praise** - Compliments, inspiration → Auto-respond with template
3. **Spam** - Crypto, MLM, phishing → Logged, no response
4. **Sales** - Partnerships, sponsorships → Flagged for manual review
5. **Unknown** - Default category → Treated as spam (no response)

## Monitoring Dashboard

View recent comments:
```bash
tail -20 .cache/youtube-comments.jsonl | jq '.'
```

Get today's stats:
```bash
grep "2026-04-20" .cache/youtube-comments.jsonl | jq -s 'group_by(.category) | map({category: .[0].category, count: length})'
```

## Troubleshooting

**"Channel not found"**
- Verify YOUTUBE_CHANNEL_ID is correct
- Check API key has YouTube Data API v3 enabled

**"No module named googleapiclient"**
- Run: `pip install google-api-python-client`

**"Quota exceeded"**
- YouTube API has quotas. Monitor usage in Cloud Console
- Default quota is 10,000 units/day
- Each comment fetch ≈ 1-2 units

**No comments being found**
- First run may take time
- Check that the channel has recent videos with comments
- Verify you're using the uploads playlist ID correctly

## Example JSONL Output

```json
{"timestamp": "2026-04-20T06:00:00.000000", "video_id": "dQw4w9WgXcQ", "commenter": "Alice", "text": "How do I start with this?", "category": "question", "response_status": "auto_responded", "published_at": "2026-04-20T05:55:00Z"}
{"timestamp": "2026-04-20T06:00:01.000000", "video_id": "dQw4w9WgXcQ", "commenter": "Bob", "text": "This is amazing!", "category": "praise", "response_status": "auto_responded", "published_at": "2026-04-20T05:56:00Z"}
{"timestamp": "2026-04-20T06:00:02.000000", "video_id": "dQw4w9WgXcQ", "commenter": "Spammer", "text": "Free Bitcoin! Click here", "category": "spam", "response_status": "pending", "published_at": "2026-04-20T05:57:00Z"}
{"timestamp": "2026-04-20T06:00:03.000000", "video_id": "dQw4w9WgXcQ", "commenter": "Brand", "text": "Partnership opportunity", "category": "sales", "response_status": "flagged_for_review", "published_at": "2026-04-20T05:58:00Z"}
```

## Next Steps

1. Get YouTube API credentials
2. Find your channel ID
3. Edit environment variables in crontab
4. Test manually: `python3 .cache/youtube-monitor.py`
5. Customize response templates
6. Add to crontab (every 30 minutes)
7. Monitor `.cache/youtube-monitor.log` for issues
