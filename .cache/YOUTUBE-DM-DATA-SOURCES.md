# YouTube DM Monitor - Data Source Integration Guide

## Overview

The monitor is **operational and ready**, but it needs a data source for real YouTube DMs. Here are the best approaches to feed DMs into the system.

---

## ✅ Recommended: Method 1 - Email Forwarding (Simplest)

YouTube can send DM notifications to your Gmail inbox. We can parse those emails to extract DMs.

### Setup Steps

1. **Enable YouTube Email Notifications**
   - Go to YouTube Studio → Settings → Notifications
   - Enable "Direct messages" email notifications
   - Set frequency to "All new messages"

2. **Create Gmail Filter**
   - Go to Gmail → Settings → Filters and Blocked Addresses
   - Create filter for: `from:(noreply@youtube.com) subject:"New message"`
   - Action: Forward to a dedicated parsing address (or label it)

3. **Get Gmail API Credentials** (if parsing automatically)
   - Go to Google Cloud Console
   - Create project, enable Gmail API
   - Create OAuth credentials (Desktop app)
   - Download credentials.json

4. **Use Email Parser Script**
   ```bash
   python3 .cache/youtube-dm-email-parser.py
   ```
   This will read YouTube DM emails from Gmail and add them to the queue.

**Pros:**
- Works without YouTube API
- Email arrives immediately
- Easy to test

**Cons:**
- Adds slight delay (email delivery)
- Requires Gmail API setup

---

## ⭐ Alternative: Method 2 - Browser Automation (Most Reliable)

Use browser automation to log into YouTube Studio and fetch DMs from the web interface.

### Setup Steps

1. **Install Selenium + Chrome Driver**
   ```bash
   pip3 install selenium
   # Download chromedriver: https://chromedriver.chromium.org/
   ```

2. **Create Automation Script**
   ```python
   # .cache/youtube-dm-browser.py
   from selenium import webdriver
   from selenium.webdriver.common.by import By
   import json
   from datetime import datetime
   
   def fetch_youtube_dms():
       """Fetch DMs from YouTube Studio web interface"""
       driver = webdriver.Chrome()
       
       try:
           # Navigate to YouTube Studio messages
           driver.get("https://studio.youtube.com/")
           
           # (Would need to handle authentication here)
           # (Then extract DMs from page)
           
           dms = []  # Extract from page
           
           # Save to temp queue
           with open("/tmp/new-dms.json", "w") as f:
               json.dump(dms, f)
       finally:
           driver.quit()
   
   if __name__ == "__main__":
       fetch_youtube_dms()
   ```

3. **Run Periodically**
   ```bash
   # Add to crontab
   */15 * * * * python3 /Users/abundance/.openclaw/workspace/.cache/youtube-dm-browser.py
   ```

**Pros:**
- Direct access to YouTube interface
- No API needed
- Can scroll through DM history

**Cons:**
- Requires browser automation
- Slower than API
- YouTube may rate-limit

---

## 🔗 Advanced: Method 3 - Webhook Integration

Set up a webhook to receive DMs in real-time from an external YouTube integration service.

### Using a Third-Party Service (e.g., Discord Bot Relay)

1. **Set up a simple webhook receiver** (example with Flask):
   ```python
   # .cache/youtube-dm-webhook.py
   from flask import Flask, request, jsonify
   import json
   from pathlib import Path
   
   app = Flask(__name__)
   
   @app.route('/youtube-dm', methods=['POST'])
   def receive_dm():
       """Receive DM from webhook"""
       data = request.json
       
       # Validate signature (if using service)
       # ...
       
       # Add to queue
       with open("/tmp/new-dms.json", "w") as f:
           json.dump([data], f)
       
       return jsonify({"status": "received"}), 200
   
   if __name__ == "__main__":
       app.run(port=5000)
   ```

2. **Start webhook server**
   ```bash
   python3 .cache/youtube-dm-webhook.py &
   ```

3. **Configure YouTube Integration**
   - Point your YouTube DM integration to `http://your-server:5000/youtube-dm`

**Pros:**
- Real-time
- Can scale
- No polling needed

**Cons:**
- Requires external integration service
- Need server running 24/7
- Public endpoint needed

---

## 🧪 Testing Without Real YouTube Data

### Send Test DMs Manually

Use this to test the monitor without real YouTube data:

```bash
cat > /tmp/new-dms.json << 'EOF'
[
  {
    "timestamp": "2026-04-15T10:30:00Z",
    "sender": "Test Setup Help",
    "sender_id": "test_setup",
    "text": "Hi! I'm trying to install this but keep getting an error. Can you help?",
    "dm_id": "test_setup_001"
  },
  {
    "timestamp": "2026-04-15T10:35:00Z",
    "sender": "Test Newsletter",
    "sender_id": "test_newsletter",
    "text": "I want to subscribe to your newsletter. How do I sign up?",
    "dm_id": "test_newsletter_001"
  },
  {
    "timestamp": "2026-04-15T10:40:00Z",
    "sender": "Test Partner Agency",
    "sender_id": "test_partner",
    "text": "We're an agency with 150k followers interested in partnership with your brand. Can we discuss collaboration opportunities?",
    "dm_id": "test_partner_001"
  },
  {
    "timestamp": "2026-04-15T10:45:00Z",
    "sender": "Test Product Buyer",
    "sender_id": "test_buyer",
    "text": "I want to buy your premium plan. What's the pricing?",
    "dm_id": "test_buyer_001"
  }
]
EOF

# Run the monitor
cd /Users/abundance/.openclaw/workspace
python3 .cache/youtube-dm-monitor-standalone.py

# Check results
echo "=== REPORT ===" && cat .cache/youtube-dms-report.txt
echo "" && echo "=== LOGGED DMS ===" && tail -4 .cache/youtube-dms.jsonl | jq .
echo "" && echo "=== FLAGGED PARTNERSHIPS ===" && tail -1 .cache/youtube-flagged-partnerships.jsonl | jq .
```

---

## 📊 Recommended Setup (Step-by-Step)

### Quick Start (Email Notifications)

1. **In YouTube Studio:**
   ```
   Settings → Notifications → Enable "Direct messages"
   ```

2. **In Gmail:**
   ```
   Create filter to label DM emails
   ```

3. **Run Monitor Hourly:**
   ```bash
   # Install to crontab
   (crontab -l 2>/dev/null || echo "") | grep -v youtube-dm > /tmp/cron.tmp
   echo "0 * * * * /Users/abundance/.openclaw/workspace/.cache/youtube-dm-monitor-cron.sh" >> /tmp/cron.tmp
   crontab /tmp/cron.tmp
   ```

4. **Test**
   ```bash
   # Manually send test DMs (see Testing section above)
   # Then run: python3 .cache/youtube-dm-monitor-standalone.py
   ```

### Production Setup (Real-Time Webhook)

1. **Set up webhook receiver** (see Method 3 above)
2. **Configure YouTube integration service** to post to webhook
3. **Monitor automatically processes** DMs in real-time
4. **Keep webhook running** with process manager (systemd, supervisord, etc.)

---

## 🔐 Security Considerations

When using real YouTube data:

1. **API Credentials**
   - Store in environment variables or `.env` file
   - Never commit credentials to version control
   - Use separate credentials for testing vs production

2. **Email Parsing**
   - Gmail API requires OAuth (user login)
   - Store refresh tokens securely
   - Rotate tokens periodically

3. **Webhook Security**
   - Validate webhook signatures (if provided by service)
   - Use HTTPS only
   - Rate limit endpoints
   - Log all received data

---

## 📋 Comparison Table

| Method | Setup Time | Real-Time | Reliability | Cost | Complexity |
|--------|-----------|-----------|-------------|------|-----------|
| Email Forwarding | 10 min | ~5 min delay | 95% | Free | ⭐ Low |
| Browser Automation | 30 min | Polling | 90% | Free | ⭐⭐ Medium |
| Webhook | 20 min | Instant | 99% | Varies* | ⭐⭐⭐ High |

*Cost depends on third-party service; can be free if self-hosted

---

## 🚀 Recommended Path

1. **Start with:** Email forwarding + manual testing (no external dependencies)
2. **Test thoroughly:** Run monitor with test DMs for 24 hours
3. **Go production:** Set up email parser for real YouTube DMs
4. **Scale:** Move to webhook when volume increases

---

## 📞 Troubleshooting

### "No DMs appearing"
- Check email forwarding is enabled in YouTube Studio
- Check filter is creating emails
- Manually test with `/tmp/new-dms.json` file

### "Monitor not finding emails"
- Verify Gmail API credentials are configured
- Check email parser script permissions
- Run manually to see errors: `python3 .cache/youtube-dm-email-parser.py`

### "Webhook not receiving data"
- Test webhook with curl: `curl -X POST http://localhost:5000/youtube-dm -H "Content-Type: application/json" -d '{"test":"data"}'`
- Check firewall/port configuration
- Verify external URL is accessible

---

## 💡 Quick Commands Reference

```bash
# Test the monitor with sample data
cat > /tmp/new-dms.json << 'EOF'
[{"timestamp":"2026-04-15T10:30:00Z","sender":"Test","sender_id":"test","text":"How do I get started?"}]
EOF
cd /Users/abundance/.openclaw/workspace && python3 .cache/youtube-dm-monitor-standalone.py

# View latest report
cat /Users/abundance/.openclaw/workspace/.cache/youtube-dms-report.txt

# Check flagged partnerships
cat /Users/abundance/.openclaw/workspace/.cache/youtube-flagged-partnerships.jsonl | jq .

# Monitor cron logs
tail -f /Users/abundance/.openclaw/workspace/.cache/youtube-dms-cron.log

# View current metrics
cat /Users/abundance/.openclaw/workspace/.cache/youtube-dms-state.json | jq .

# Test cron job manually
/Users/abundance/.openclaw/workspace/.cache/youtube-dm-monitor-cron.sh
```

---

**Status:** Ready for data source integration  
**Last Updated:** 2026-04-15  
**Next Step:** Choose a data source from the methods above
