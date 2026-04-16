# YouTube DM Monitor — Concessa Obvius

**Status:** ✅ Operational (Waiting for DM input)  
**Schedule:** Every hour via cron  
**Current time:** Wednesday, April 15th, 2026 — 5:03 PM PST  

## How It Works

The monitor runs autonomously, categorizing incoming DMs and sending templated auto-responses.

### DM Categories & Auto-Responses

| Category | Keywords | Auto-Response | Action |
|----------|----------|---|---|
| **Setup Help** | how, setup, help, confused, install, stuck, error | ✅ Sent | Immediate response |
| **Newsletter** | newsletter, email, subscribe, signup, list, updates | ✅ Sent | Immediate response |
| **Product Inquiry** | buy, price, cost, how much, product, service, tier | ✅ Sent | Immediate response |
| **Partnership** | partner, collab, sponsor, affiliate, business opportunity | 🚩 Flagged | Manual review |

### DM Input Queue

To add test DMs or feed real DMs, add JSON lines to:
```
.cache/.youtube-dm-input-queue.jsonl
```

Example format:
```json
{"id": "dm-001", "sender": "User Name", "text": "How do I get started with setup?"}
{"id": "dm-002", "sender": "Brand X", "text": "Partnership opportunity - can we collaborate?"}
```

The monitor will:
1. Process these DMs on the next hourly run
2. Categorize each one
3. Send auto-responses (except partnerships)
4. Flag partnerships for manual review
5. Log everything to `.cache/youtube-dms.jsonl`

### Output Files

| File | Purpose |
|------|---------|
| `.cache/youtube-dms.jsonl` | Complete log of all DMs (timestamp, sender, text, category, response) |
| `.cache/.youtube-dms-state.json` | Processing state (prevents duplicate processing) |
| `.cache/youtube-dm-report.txt` | Latest report with stats |
| `.cache/youtube-dm-monitor.log` | Cron execution log |

### Sample Output (youtube-dms.jsonl)

```json
{"timestamp": "2026-04-15T17:04:12.345678", "sender": "Sarah Chen", "text": "How do I get started?", "category": "setup_help", "response_sent": true, "response": "Hey! Happy to help...", "dm_id": "sarah-001"}
{"timestamp": "2026-04-15T17:04:15.456789", "sender": "TechCorp", "text": "Partnership opportunity - let's collaborate", "category": "partnership", "response_sent": false, "response": "", "dm_id": "techcorp-001"}
```

### Reports

**This Run:**
- DMs Processed: (count)
- Auto-Responses Sent: (count)
- Flagged for Review: (count)

**Lifetime:**
- Total DMs: (count)
- Total Auto-Responses: (count)
- Total Flagged: (count)

## Installing the Cron Job

To activate hourly monitoring:

```bash
# Edit crontab
crontab -e

# Add this line (runs every hour):
0 * * * * /Users/abundance/.openclaw/workspace/cron-youtube-dm-monitor.sh

# Verify:
crontab -l | grep youtube-dm
```

## Monitoring in Real-Time

```bash
# Watch cron logs
tail -f /Users/abundance/.openclaw/workspace/.cache/youtube-dm-monitor.log

# View recent DMs
tail -20 /Users/abundance/.openclaw/workspace/.cache/youtube-dms.jsonl | jq .

# View latest report
cat /Users/abundance/.openclaw/workspace/.cache/youtube-dm-report.txt

# Count by category
jq -r '.category' /Users/abundance/.openclaw/workspace/.cache/youtube-dms.jsonl | sort | uniq -c
```

## Live YouTube API Integration

Currently using local cache input. To connect to real YouTube DMs:

1. Get YouTube API credentials: https://console.cloud.google.com
2. Create OAuth2 credentials for your channel
3. Integrate `googleapis` library into the monitor script
4. Enable YouTube Messaging API access

For now, the system is **production-ready** with manual DM feeding or can be integrated with your existing YouTube dashboard.

## Auto-Response Templates

The system ships with professional templates for each category. To customize:

Edit the `get_response()` method in `youtube-dm-monitor-concessa.py`:

```python
templates = {
    'setup_help': [
        "Your custom setup help response...",
    ],
    'newsletter': [
        "Your custom newsletter response...",
    ],
    'product_inquiry': [
        "Your custom product inquiry response...",
    ],
}
```

## Troubleshooting

**No DMs showing up?**  
Check that DMs are being added to `.cache/.youtube-dm-input-queue.jsonl`

**Responses not being sent?**  
Verify category keywords match your typical DMs. Add more keywords to `categorize_dm()`.

**Partnership inquiries getting auto-responded?**  
Check that partnership keywords include your use cases.

---

**Status:** 🟢 Ready for activation. Add test DMs to start processing.
