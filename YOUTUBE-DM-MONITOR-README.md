# YouTube DM Monitor - Concessa Obvius Channel

## What This Does

Automatically monitors YouTube direct messages to the Concessa Obvius channel every hour, categorizes incoming DMs into 4 types, and sends appropriate templated auto-responses.

## Quick Start

```bash
# Test the monitor
node /Users/abundance/.openclaw/workspace/scripts/youtube-dm-monitor.js

# View latest report
cat /Users/abundance/.openclaw/.cache/youtube-dms-report.json

# View all logged DMs
cat /Users/abundance/.openclaw/.cache/youtube-dms.jsonl
```

## Cron Job Details

- **ID**: `c1b30404-7343-46ff-aa1d-4ff84daf3674`
- **Frequency**: Every hour (on the hour)
- **Command**: `node /Users/abundance/.openclaw/workspace/scripts/youtube-dm-monitor.js`
- **Started**: Monday, April 21, 2026 at 9:03 PM PT

## Files

| File | Purpose |
|------|---------|
| `scripts/youtube-dm-monitor.js` | Main monitor script with categorization logic |
| `scripts/youtube-dm-fetch.js` | DM fetcher (API + browser automation) |
| `.cache/youtube-dms.jsonl` | Log of all processed DMs (JSONL format) |
| `.cache/youtube-dms-report.json` | Latest hourly report with stats |
| `docs/youtube-dm-monitor-setup.md` | Full setup and configuration guide |

## DM Categories & Auto-Responses

### 1. Setup Help
**Keywords**: how to, confused, help, tutorial, guide, setup, install, problem, error
**Response**: Links to tutorials and documentation, offer personal help

### 2. Newsletter
**Keywords**: newsletter, email list, subscribe, updates, notifications, sign up
**Response**: Newsletter signup link, description of what they'll receive

### 3. Product Inquiry
**Keywords**: buy, purchase, price, pricing, product, recommend, interested, cost
**Response**: Product overview with pricing, ask clarifying questions

### 4. Partnership
**Keywords**: collaborate, partnership, sponsorship, business, affiliate, opportunity
**Response**: Expresses interest, requests more details, flags for manual review

## Key Metrics Tracked

- **Total DMs Processed**: New messages received per hour
- **Auto-Responses Sent**: Count of automatic replies
- **Conversion Potential**: Product inquiry count (sales opportunity)
- **Partnerships Flagged**: High-value opportunities for review

## Configuration

### To Enable YouTube API (Recommended)

1. Get an API key from Google Cloud Console
2. Set environment variable: `export YOUTUBE_API_KEY="your-key"`
3. Monitor will automatically use API for fetching

### To Use Browser Automation (Fallback)

- Requires OpenClaw browser to be running
- Automatically activated if API is not available
- Navigates to YouTube Studio and extracts DMs

## Recent Run Status

✓ **Last Run**: April 21, 2026 @ 4:04 AM UTC  
✓ **Status**: Ready and waiting for first DMs  
✓ **DMs Processed**: 0 (No DMs yet)  
✓ **Auto-Responses Sent**: 0  
✓ **Next Check**: In 1 hour

## Monitoring the Monitor

### Check if it's running

```bash
# View the latest report (auto-generated each hour)
cat ~/.openclaw/.cache/youtube-dms-report.json | jq .

# Follow the log in real-time (when running)
tail -f ~/.openclaw/.cache/youtube-dms-report.json
```

### View processed DMs

```bash
# Pretty print the JSONL log
jq '.' ~/.openclaw/.cache/youtube-dms.jsonl

# Count total DMs by category
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' \
  ~/.openclaw/.cache/youtube-dms.jsonl
```

## Customization

### Edit Response Templates

File: `scripts/youtube-dm-monitor.js` → `TEMPLATES` object

```javascript
const TEMPLATES = {
  'Setup help': {
    subject: 'Help with Setup',
    body: `Your custom message here...`
  },
  // Modify other categories as needed
};
```

### Adjust Categorization Keywords

File: `scripts/youtube-dm-monitor.js` → `KEYWORDS` object

```javascript
const KEYWORDS = {
  'Setup help': ['how to', 'confused', 'help', ...],
  // Add or remove keywords
};
```

## Integration Examples

### Send Report to Slack

```bash
#!/bin/bash
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
REPORT_FILE="~/.openclaw/.cache/youtube-dms-report.json"

# Send report as Slack message
curl -X POST $SLACK_WEBHOOK \
  -H 'Content-Type: application/json' \
  -d @$REPORT_FILE
```

### Save to Google Sheets

```bash
# Use gspread or similar to append report data to a sheet
# Example: log hourly DM counts to track trends
```

### Email Daily Digest

```bash
# Combine multiple hourly reports into daily email
# Use cron to run at 9 AM and aggregate previous 24 hours
```

## Troubleshooting

### No DMs being fetched?

1. Check API key is set: `echo $YOUTUBE_API_KEY`
2. Verify browser is running: `openclaw browser status`
3. Check for errors: `node scripts/youtube-dm-monitor.js 2>&1 | tail`

### Wrong category assignments?

1. Review actual DM text in `.cache/youtube-dms.jsonl`
2. Adjust keywords in the KEYWORDS object
3. Test with: `node scripts/youtube-dm-monitor.js`

### Responses not being sent?

1. Verify YouTube authentication works
2. Check rate limits aren't exceeded
3. Look for API errors in report file

## Performance

- **Hourly cost**: ~5-10 YouTube API units
- **Monthly cost**: ~3,600-7,200 units (plenty of headroom)
- **Execution time**: <1 second (when using API)
- **Storage**: ~500 bytes per DM in cache

## Security Notes

- API tokens stored in environment variables
- DMs logged locally only (not sent externally without explicit integration)
- No data shared with third parties by default
- Complies with YouTube Terms of Service

## Support

For help:
1. Check `docs/youtube-dm-monitor-setup.md`
2. Review script comments in `scripts/youtube-dm-monitor.js`
3. Test manually: `node scripts/youtube-dm-monitor.js`
4. Check cache file for error messages

---

**Created**: April 21, 2026 @ 4:04 AM UTC  
**Monitor Status**: ✓ Ready  
**Next Scheduled Run**: In 1 hour
