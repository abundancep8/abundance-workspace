# YouTube DM Monitor Setup

## Overview

The YouTube DM Monitor is a cron job that automatically monitors direct messages to the Concessa Obvius YouTube channel, categorizes incoming DMs, and sends templated auto-responses.

## Features

- **Automatic DM Monitoring**: Runs hourly to check for new messages
- **Smart Categorization**: Automatically sorts DMs into 4 categories:
  1. **Setup help** - How to use, technical support, confused users
  2. **Newsletter** - Email list signup, update subscriptions
  3. **Product inquiry** - Pricing, product selection, purchase intent
  4. **Partnership** - Collaboration, sponsorship, business proposals
- **Auto-Response Templates**: Sends appropriate responses based on category
- **Partnership Flagging**: Flags interesting partnership inquiries for manual review
- **Detailed Logging**: Records all DMs to `.cache/youtube-dms.jsonl`
- **Hourly Reports**: Generates summary reports with key metrics

## Installation & Configuration

### 1. YouTube API Setup (Recommended)

To use the official YouTube API:

```bash
# Create a service account in Google Cloud Console
# 1. Go to https://console.cloud.google.com
# 2. Create a new project: "YouTube DM Monitor"
# 3. Enable YouTube Data API v3
# 4. Create OAuth 2.0 credentials (service account)
# 5. Save the JSON key file

# Set environment variable
export YOUTUBE_API_KEY="your-api-key-here"

# Or add to ~/.bashrc or ~/.zshrc:
echo 'export YOUTUBE_API_KEY="your-api-key-here"' >> ~/.zshrc
```

### 2. Browser Automation Setup (Fallback)

If API is not configured, the system will use browser automation:

```bash
# Ensure OpenClaw browser is running
openclaw browser start

# The monitor will automatically use browser automation if API is unavailable
```

### 3. Customize Templates

Edit templates in `scripts/youtube-dm-monitor.js`:

```javascript
const TEMPLATES = {
  'Setup help': {
    subject: 'Help with Setup',
    body: `Your custom response here...`
  },
  // ... other categories
};
```

### 4. Customize Keywords

Adjust keyword matching in the same file:

```javascript
const KEYWORDS = {
  'Setup help': ['how to', 'confused', 'help', ...],
  // ... other categories
};
```

## Running the Monitor

### Manual Run

```bash
node /Users/abundance/.openclaw/workspace/scripts/youtube-dm-monitor.js
```

### Cron Job (Automatic Hourly)

The cron job ID `c1b30404-7343-46ff-aa1d-4ff84daf3674` runs:

```bash
# Every hour
node /Users/abundance/.openclaw/workspace/scripts/youtube-dm-monitor.js
```

### Output

After each run, check:

- **Cache File**: `.cache/youtube-dms.jsonl`
  - JSONL format (one JSON object per line)
  - Records: timestamp, sender, category, response sent, response text

- **Report File**: `.cache/youtube-dms-report.json`
  - Summary statistics
  - Breakdown by category
  - Flagged partnerships
  - New DMs processed

## Data Structure

### Cache Entry (JSONL)

```json
{
  "timestamp": "2026-04-21T04:03:00Z",
  "sender": "John Doe",
  "sender_id": "UCxxxxxx",
  "text": "How do I get started?",
  "category": "Setup help",
  "dm_id": "abc123def456",
  "response_sent": true,
  "response_subject": "Help with Setup",
  "response_text": "Hi! Thanks for reaching out..."
}
```

### Report Structure

```json
{
  "timestamp": "2026-04-21T04:03:00Z",
  "summary": {
    "total_dms_processed": 5,
    "auto_responses_sent": 5,
    "conversion_potential": 2,
    "partnerships_flagged": 1
  },
  "breakdown_by_category": {
    "Setup help": 2,
    "Product inquiry": 2,
    "Partnership": 1,
    "Newsletter": 0
  },
  "flagged_partnerships": [
    {
      "timestamp": "2026-04-21T04:00:00Z",
      "sender": "Brand Inc",
      "sender_id": "brand_001",
      "text": "We'd love to collaborate!"
    }
  ],
  "new_dms": [...]
}
```

## Metrics & Reporting

Each hour, the monitor tracks:

- **Total DMs Processed**: Number of new DMs received
- **Auto-Responses Sent**: Number of automatic responses sent
- **Conversion Potential**: Count of product inquiries (sales opportunity indicator)
- **Partnerships Flagged**: High-value partnership opportunities requiring review

## Troubleshooting

### No DMs Being Fetched

1. Check if API token is configured:
   ```bash
   echo $YOUTUBE_API_KEY
   ```

2. Verify browser is running:
   ```bash
   openclaw browser status
   ```

3. Check logs:
   ```bash
   tail -f ~/.openclaw/.cache/youtube-dm-monitor.log
   ```

### DMs Not Being Categorized Correctly

1. Review the DM text in the cache file
2. Adjust KEYWORDS in `youtube-dm-monitor.js`
3. Re-run the script

### Responses Not Being Sent

1. Verify YouTube authentication is working
2. Check if rate limits are being hit
3. Review error logs for specific API errors

## API Rate Limits

YouTube API has rate limits:
- **Default**: 10,000 units per 24 hours
- **Each DM fetch**: ~5-10 units
- **Hourly monitor**: ~50-100 units per day
- **Safe limit**: ✓ Well within quota for typical usage

## Privacy & Compliance

- All DMs are logged locally to `.cache/youtube-dms.jsonl`
- Responses use professional templates
- No data is sent to external services (API only to YouTube)
- Complies with YouTube's Terms of Service for creator tools

## Advanced: Custom Integration

To integrate with external systems (email, CRM, Slack):

```bash
# After the monitor runs, hook the report file
.cache/youtube-dms-report.json

# Example: Send to Slack
curl -X POST https://hooks.slack.com/... \
  -d @.cache/youtube-dms-report.json
```

## Support & Updates

For issues or improvements:

1. Check logs: `~/.openclaw/.cache/youtube-dm-monitor.log`
2. Review templates: `scripts/youtube-dm-monitor.js`
3. Test manually: `node scripts/youtube-dm-monitor.js`
4. Report bugs: Submit issue with logs and example DM text

---

**Last Updated**: April 21, 2026  
**Monitor ID**: c1b30404-7343-46ff-aa1d-4ff84daf3674  
**Next Run**: Every hour
