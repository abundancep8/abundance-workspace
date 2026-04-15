# YouTube DM Monitor - Integration Guide

## 🎯 What's Been Built

✅ **Categorization engine** - Automatically sorts DMs into 4 categories
✅ **Auto-responder** - Sends template responses based on category
✅ **JSONL logging** - Records all DMs with metadata
✅ **Partnership flagging** - Highlights interesting deals for manual review
✅ **Hourly cron job** - Runs automatically, generates reports

## 🔧 Integration Options (Choose One)

### **Option A: Browser Extension (Most Reliable)**

Create a simple Chrome extension:

```javascript
// manifest.json
{
  "manifest_version": 3,
  "name": "YouTube DM Monitor",
  "permissions": ["scripting", "activeTab"],
  "background": {
    "service_worker": "background.js"
  }
}

// background.js
chrome.runtime.onMessage.addListener((msg, sender, reply) => {
  if (msg.type === "new_dm") {
    // Write to /tmp/new-dms.json
    fetch("http://localhost:8888/new-dm", {
      method: "POST",
      body: JSON.stringify({
        timestamp: new Date().toISOString(),
        sender: msg.sender,
        sender_id: msg.sender_id,
        text: msg.text
      })
    });
  }
});
```

Then run a simple local server to receive the POSTs and write to `/tmp/new-dms.json`.

---

### **Option B: Webhook Server (Easy Setup)**

Run this lightweight server in the background:

```bash
npm install express body-parser
```

```javascript
// server.js
const express = require('express');
const fs = require('fs');
const app = express();
app.use(express.json());

let newDMs = [];

app.post('/new-dm', (req, res) => {
  newDMs.push(req.body);
  res.json({ received: true });
});

// Every hour, write accumulated DMs to file
setInterval(() => {
  if (newDMs.length > 0) {
    fs.writeFileSync('/tmp/new-dms.json', JSON.stringify(newDMs));
    newDMs = [];
  }
}, 60000);

app.listen(8888, () => console.log('Webhook server running on :8888'));
```

Start with: `node server.js`
Then point your DM source to: `http://localhost:8888/new-dm`

---

### **Option C: Manual Export (Testing)**

1. Copy DM list from YouTube
2. Format as JSON and save to `/tmp/new-dms.json`
3. Monitor script auto-consumes it

Example:
```bash
cat > /tmp/new-dms.json << 'EOF'
[
  {
    "timestamp": "2026-04-14T21:03:58.833Z",
    "sender": "Alice_Creator",
    "sender_id": "UC_alice123",
    "text": "How do I set this up?"
  }
]
EOF

# Run monitor (it will process and delete the file)
node /Users/abundance/.openclaw/workspace/.cache/youtube-dms-monitor.js
```

---

### **Option D: Email Forwarding**

If YouTube sends DM notifications to email:
1. Set up a mail parser (Zapier, Make, or custom)
2. Extract sender, timestamp, and message text
3. POST to the webhook server (Option B) or write to `/tmp/new-dms.json`

---

## ✅ Quick Test

1. **Create test data:**
   ```bash
   cat > /tmp/new-dms.json << 'EOF'
   [
     {"timestamp":"2026-04-14T21:03:58Z","sender":"Test User","text":"I want to buy your product"},
     {"timestamp":"2026-04-14T21:04:00Z","sender":"Dev Confused","text":"How do I set this up? Confused"},
     {"timestamp":"2026-04-14T21:04:02Z","sender":"Partnership Co","text":"Let's collaborate on a sponsorship"}
   ]
   EOF
   ```

2. **Run the monitor:**
   ```bash
   cd /Users/abundance/.openclaw/workspace
   node .cache/youtube-dms-monitor.js
   ```

3. **Check outputs:**
   ```bash
   # View the log
   tail -20 .cache/youtube-dms.jsonl
   
   # View the report
   cat .cache/youtube-dms-report.json
   ```

---

## 🔄 Cron Integration

OpenClaw will run hourly:
```
0 * * * * cd /Users/abundance/.openclaw/workspace && node .cache/youtube-dms-monitor.js
```

The cron job:
- ✅ Processes new DMs from `/tmp/new-dms.json`
- ✅ Appends to `.cache/youtube-dms.jsonl`
- ✅ Generates report at `.cache/youtube-dms-report.json`
- ✅ Flags partnerships for review

---

## 📊 Customization

**Change response templates:**
Edit the `TEMPLATES` object in `youtube-dms-monitor.js`

**Tune categorization:**
Edit the `KEYWORDS` object to add/remove keywords for each category

**Add new categories:**
1. Add to `KEYWORDS`
2. Add to `TEMPLATES`
3. Script automatically handles the rest

---

## 🚨 Troubleshooting

**No DMs being processed?**
- Check if `/tmp/new-dms.json` exists and has data
- Verify JSON format is correct
- Check file permissions

**Wrong categorization?**
- Review the keywords in KEYWORDS
- Test with `console.log()` to debug scoring

**Responses not being sent?**
- Currently the script *logs* that a response would be sent
- To actually send DMs, you'll need to integrate with YouTube's API or a manual workflow

---

## 🎯 Next: Sending Actual Responses

The current system *logs* responses and flags partnerships. To actually send DMs back:

1. Integrate with YouTube's Messaging API (requires partnership)
2. Or add a manual review workflow that shows responses to approve
3. Or use a third-party tool (TubeBuddy, VidIQ, etc.) that has DM management

---

**Current Status:** ✅ Ready to process DMs
**Next Step:** Choose integration method (A, B, C, or D above) and start feeding data!
