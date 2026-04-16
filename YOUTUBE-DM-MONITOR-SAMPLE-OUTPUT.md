# YouTube DM Monitor — Sample Hourly Output

This shows what you'll see in the logs and reports during each hourly run.

---

## 📋 Cron Log Output

**File:** `~/.cache/youtube-dm-monitor-cron.log`

```
[2026-04-15 04:00:00] =========================================
[2026-04-15 04:00:00] YouTube DM Monitor - Hourly Run
[2026-04-15 04:00:00] =========================================
[2026-04-15 04:00:01] Activating virtual environment...
[2026-04-15 04:00:02] Checking dependencies...
[2026-04-15 04:00:03] Starting DM monitor...
[2026-04-15 04:00:15] 🎬 YouTube DM Monitor
[2026-04-15 04:00:15] ⏰ Started at 2026-04-15T04:00:15.234567
[2026-04-15 04:00:20] ✓ Navigated to YouTube Studio messages
[2026-04-15 04:00:25] ✓ Extracted 3 DMs from YouTube Studio
[2026-04-15 04:00:26] ✅ Processed 3 new DMs
[2026-04-15 04:00:26]   • sender_alice: setup_help
[2026-04-15 04:00:26]   • marketing_guy: partnership
[2026-04-15 04:00:26]     🚩 Flagged for manual review
[2026-04-15 04:00:26]   • subscriber_jane: product_inquiry
[2026-04-15 04:00:27]
[2026-04-15 04:00:27] 📊 REPORT SUMMARY
[2026-04-15 04:00:27] Total DMs: 3
[2026-04-15 04:00:27] Auto-responses sent: 3
[2026-04-15 04:00:27] Categories: setup_help (1), partnership (1), product_inquiry (1)
[2026-04-15 04:00:27] Partnerships flagged: 1
[2026-04-15 04:00:27] Conversion potential: 1 product inquiry to follow up on
[2026-04-15 04:00:28]
[2026-04-15 04:00:28] ⭐ Interesting partnerships for manual review:
[2026-04-15 04:00:28]   • marketing_guy
[2026-04-15 04:00:28]     Hi! We're a small media company and would love to collaborate...
[2026-04-15 04:00:29] ✅ Completed at 2026-04-15 04:00:29
```

---

## 📊 DM Log Format

**File:** `~/.cache/youtube-dms.jsonl` (one JSON object per line)

```json
{"timestamp": "2026-04-15T04:00:23.456789", "sender": "alice_creator", "sender_id": "UC1234567890abc", "text": "Hi! I'm trying to set up your product but I'm confused on step 3 where you talk about API keys. Can you help?", "category": "setup_help", "response_sent": "Hey! 👋 Thanks for reaching out about setup.\n\n📚 Full setup guide: https://concessa.com/docs/setup\n🎥 Step-by-step video: https://concessa.com/setup-video\n💬 Common issues: https://concessa.com/faq\n\nIf you get stuck on API keys specifically, check this section: https://concessa.com/docs/setup#api-keys\n\nReply with what's giving you trouble!", "interesting_partnership": false, "raw_dm_id": "msg_abc123"}

{"timestamp": "2026-04-15T04:00:24.567890", "sender": "marketing_guy", "sender_id": "UC0987654321xyz", "text": "Hi! We're a small media company and would love to collaborate on a sponsorship deal. We have 50k YouTube subscribers. What are your rates and what kind of deals do you offer?", "category": "partnership", "response_sent": "Ooh, interesting! 🤝 I love hearing partnership ideas.\n\nFor collab/sponsorship inquiries, let's take this to email so we can dive deeper:\n📧 partnerships@concessa.com\n\nTell me a bit more about what you have in mind and we'll explore it!", "interesting_partnership": true, "raw_dm_id": "msg_def456"}

{"timestamp": "2026-04-15T04:00:25.678901", "sender": "subscriber_jane", "sender_id": "UC5555555555def", "text": "Hey! This looks cool. How much does it cost and which plan would be good for a startup team of 3 people?", "category": "product_inquiry", "response_sent": "Great question! 🎯\n\n📦 Product info & pricing: https://concessa.com/pricing\n💰 We have options for every budget\n\nFor a team of 3, I'd recommend checking out the Team Starter plan at $29/month. But let me know:\n- What's your main use case?\n- Any specific features you need?\n- What's your budget range?\n\nHappy to help you find the perfect fit!", "interesting_partnership": false, "raw_dm_id": "msg_ghi789"}
```

---

## 📈 Report JSON Format

**File:** `~/.cache/youtube-dm-report.json`

```json
{
  "timestamp": "2026-04-15T04:00:29.789012",
  "status": "completed",
  "total_dms_processed": 3,
  "auto_responses_sent": 3,
  "by_category": {
    "setup_help": 1,
    "partnership": 1,
    "product_inquiry": 1,
    "newsletter": 0
  },
  "partnerships_flagged": 1,
  "interesting_partnerships": [
    {
      "sender": "marketing_guy",
      "timestamp": "2026-04-15T04:00:24.567890",
      "preview": "Hi! We're a small media company and would love to collaborate on a sponsorship deal..."
    }
  ],
  "product_inquiries": 1,
  "conversion_potential": "1 product inquiry to follow up on"
}
```

---

## 💬 Discord Webhook Output (Optional)

**If you set up Discord integration**, you'll get this message every hour:

```
📊 **YouTube DM Monitor Report**
✓ **DMs Processed:** 3
✉️ **Auto-Responses:** 3
🤝 **Partnerships Flagged:** 1
🎯 **Conversion Potential:** 1 product inquiry to follow up on

⭐ **Interesting Partnership:**
• marketing_guy
  "Hi! We're a small media company and would love to collaborate on a sponsorship deal..."
```

---

## 📈 24-Hour Summary

After 24 hours (24 runs), you might see something like:

```json
{
  "period": "Last 24 hours",
  "total_runs": 24,
  "total_dms_processed": 48,
  "auto_responses_sent": 48,
  "by_category": {
    "setup_help": 18,
    "newsletter": 12,
    "product_inquiry": 14,
    "partnership": 4
  },
  "partnerships_flagged": 2,
  "product_inquiries_to_follow_up": 14,
  "estimated_conversion_value": "Depends on your product, but 14 warm leads is good!"
}
```

---

## 🎯 Key Metrics You'll Track

After the first week of runs, you'll be able to see:

| Metric | Example | Insight |
|--------|---------|---------|
| Total DMs | 336 (7 days × 48/day avg) | Engagement level |
| Setup Help % | 38% | People need better docs? |
| Newsletter % | 25% | Interest in staying updated |
| Product Inquiry % | 30% | Sales pipeline |
| Partnership % | 7% | Business opportunities |
| Partnerships Flagged | 3-5 per week | Follow-up action items |

---

## 🔍 How to Read the Logs

### Check last 10 lines:
```bash
tail -10 ~/.cache/youtube-dms.jsonl | jq '.sender, .category, .text'
```

### Find all setup help DMs:
```bash
grep 'setup_help' ~/.cache/youtube-dms.jsonl | jq '.'
```

### Find all flagged partnerships:
```bash
grep 'true' ~/.cache/youtube-dms.jsonl | jq '.sender, .text'
```

### Count DMs by category:
```bash
jq -s 'group_by(.category) | map({category: .[0].category, count: length})' ~/.cache/youtube-dms.jsonl
```

### Get total responses sent:
```bash
jq -s 'map(select(.response_sent != null)) | length' ~/.cache/youtube-dms.jsonl
```

---

## 💡 What to Expect

### First Run
- Browser opens, asks for YouTube login
- Processes any unread DMs
- Logs everything
- You see the report

### Subsequent Hourly Runs
- If DMs: You see categorization, auto-responses, flags
- If no DMs: Quick log saying "no new DMs"
- Reports accumulate in `.cache/youtube-dms.jsonl`

### Typical Patterns
- **Mornings:** Higher DM volume (timezones waking up)
- **Evenings:** Fewer DMs
- **Weekends:** Mix depending on content
- **New video launches:** Spike in DMs

---

## 🚨 Common Patterns to Watch For

**Spike in Setup Help?**
→ Your onboarding docs need improvement

**Many Product Inquiries?**
→ Good engagement signal, follow up within 24h for best conversion

**Partnerships Flagged?**
→ Review these manually within a few days before they move on

**Newsletter Sign-ups?**
→ Growing audience interested in updates — nurture this list!

---

## ✨ Example Use Cases

### Track Setup Friction
```bash
# How many setup help DMs this week?
grep 'setup_help' ~/.cache/youtube-dms.jsonl | wc -l

# What are people stuck on?
grep 'setup_help' ~/.cache/youtube-dms.jsonl | jq '.text'
```

### Find Hot Leads
```bash
# Product inquiries from last 24h
grep 'product_inquiry' ~/.cache/youtube-dms.jsonl | tail -20 | jq '.sender, .text'
```

### Review Partnerships
```bash
# All flagged partnerships
jq 'select(.interesting_partnership == true)' ~/.cache/youtube-dms.jsonl | jq '.sender, .timestamp, .text'
```

---

## 📞 Troubleshooting Output

**Cron log says "error"?**
→ Check: `tail -50 ~/.cache/youtube-dm-monitor-cron.log` for details

**Report file empty?**
→ First run requires YouTube login. Run manually: `python3 youtube-dm-monitor-live.py --report`

**DM log growing but report stays the same?**
→ Report only updates when cron runs. Check: `tail -1 ~/.cache/youtube-dm-report.json`

---

This is what success looks like. After a few days of hourly runs, you'll have a complete picture of your DM patterns and engagement. 🚀
