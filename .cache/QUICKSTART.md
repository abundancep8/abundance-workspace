# 🚀 YouTube Comment Monitor - Quick Start

**Estimated setup time:** 10 minutes  
**Status:** Production-ready  
**Channel:** Concessa Obvius

---

## 📋 Pre-Setup Checklist

Before you begin, make sure you have:

- [ ] Access to Google Cloud Console
- [ ] Ability to create a new project
- [ ] YouTube channel (Concessa Obvius)
- [ ] macOS/Linux machine with Python 3.8+

---

## ⚡ TL;DR - Fast Track

```bash
# 1. Install dependencies (1 min)
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# 2. Get credentials from Google Cloud Console (3 min)
#    → Create project
#    → Enable YouTube Data API v3
#    → Create OAuth 2.0 credentials (Desktop)
#    → Download JSON to ~/.openclaw/workspace/.cache/youtube_credentials.json

# 3. Run setup wizard (5 min)
python3 ~/.openclaw/workspace/.cache/setup-youtube-cron.py

# 4. Done! Monitor runs automatically every 30 minutes
```

---

## 🎯 Step-by-Step Setup

### Step 1: Install Python Dependencies (2 min)

```bash
cd ~/.openclaw/workspace
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

**What it does:** Installs YouTube API client libraries.

---

### Step 2: Create Google Cloud Project (5 min)

1. **Go to Google Cloud Console:**
   → https://console.cloud.google.com

2. **Create a new project:**
   - Click "Select a Project" (top)
   - Click "NEW PROJECT"
   - Name it: `Concessa Obvius Monitor`
   - Click "CREATE"

3. **Enable YouTube API:**
   - Search for "YouTube Data API v3"
   - Click on it
   - Click "ENABLE"
   - Wait for it to activate

4. **Create OAuth Credentials:**
   - Go to "Credentials" (left sidebar)
   - Click "CREATE CREDENTIALS" → "OAuth client ID"
   - If prompted, configure OAuth consent screen first:
     - User Type: External
     - App name: Concessa Monitor
     - Scopes: Add `https://www.googleapis.com/auth/youtube.force-ssl`
   - Application type: **Desktop application**
   - Name: `Concessa Monitor`
   - Click "CREATE"

5. **Download JSON:**
   - Click the download icon on your new credentials
   - Save file to: **`~/.openclaw/workspace/.cache/youtube_credentials.json`**

---

### Step 3: Update Channel ID (1 min)

Find your actual channel ID:

1. **Go to your YouTube channel:** https://www.youtube.com/@concessaobvius
2. **Get the channel ID:**
   - Right-click → "View page source"
   - Search for `"channelId":"UC`
   - Copy the full ID
   - Or check the URL for `/c/...` or `/@...`

3. **Update the script:**
   ```bash
   nano ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
   
   # Find this line:
   CHANNEL_ID = "UCa_mZVVqV5Aq48a0MnIjS-w"
   
   # Replace with your actual channel ID:
   CHANNEL_ID = "UC_your_actual_id_here_"
   
   # Save: Ctrl+O, Enter, Ctrl+X
   ```

---

### Step 4: Run Setup Wizard (3 min)

```bash
python3 ~/.openclaw/workspace/.cache/setup-youtube-cron.py
```

The wizard will:
- ✓ Verify dependencies
- ✓ Check credentials exist
- ✓ Make scripts executable
- ✓ Set up cron job (every 30 min)
- ✓ Guide you through first-time authorization

**When prompted:** Authorize in your browser.

---

### Step 5: Verify Setup (1 min)

```bash
# Check cron job is installed
crontab -l | grep youtube

# Should show something like:
# */30 * * * * /bin/bash /Users/abundance/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

---

## ✅ You're Done!

Your YouTube comment monitor is now running. Here's what happens:

1. **Every 30 minutes:**
   - Fetches new comments from Concessa Obvius channel
   - Categorizes them (Questions, Praise, Spam, Sales, Other)
   - Auto-responds to Questions & Praise
   - Flags Sales inquiries for manual review

2. **Logs everything:**
   - All comments saved to `.cache/youtube-comments.jsonl`
   - Execution logs in `.cache/youtube-monitor.log`

---

## 🎛️ First-Run Commands

### View Dashboard
```bash
python3 ~/.openclaw/workspace/.cache/youtube-monitor-dashboard.py
```

Shows:
- Total comments processed
- Breakdown by category
- Auto-responses sent
- Flagged for review
- Recent comments

### View Live Logs
```bash
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log
```

### Manual Test Run
```bash
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

### View All Comments
```bash
cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | python3 -m json.tool | less
```

---

## 📊 What Gets Logged

Each comment is logged with:
```json
{
  "timestamp": "2026-04-18T19:30:45",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": "question",
  "response_status": "auto_responded"
}
```

---

## 🎯 Comment Categories

| Category | Pattern | Response | Example |
|----------|---------|----------|---------|
| **Question** | How, tools, price, timeline | Auto-reply with resources | "How do I get started?" |
| **Praise** | Amazing, inspiring, thank you | Auto-reply with thanks | "This is life-changing!" |
| **Spam** | Crypto, MLM, click here | None (manual delete) | "Bitcoin opportunity! 🚀" |
| **Sales** | Partnership, sponsorship | 🚩 Flagged for review | "Let's collaborate!" |
| **Other** | Doesn't fit above | None | Random comment |

---

## 🔧 Customization

### Change Response Templates

Edit in `.cache/youtube-comment-monitor.py`:

```python
RESPONSE_TEMPLATES = {
    "question": "Your custom response for questions...",
    "praise": "Your custom response for praise...",
}
```

### Change Check Frequency

Edit your crontab:
```bash
crontab -e

# Change from:
*/30 * * * * ...     # every 30 minutes

# To:
*/15 * * * * ...     # every 15 minutes
0 * * * * ...        # every hour
0 9 * * * ...        # daily at 9 AM
```

### Add Custom Category

Edit `PATTERNS` dict in the script:
```python
PATTERNS = {
    "your_category": [r"pattern1", r"pattern2"],
}
```

---

## 🆘 Troubleshooting

### "No valid YouTube credentials found"
```bash
# Fix: Download JSON from Google Cloud Console again
# Save to: ~/.openclaw/workspace/.cache/youtube_credentials.json
# Then restart the script
```

### "Channel not found"
```bash
# Fix: Verify CHANNEL_ID in the script is correct
nano ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
# Update CHANNEL_ID with your actual channel ID
```

### Cron job not running
```bash
# Check it's installed
crontab -l | grep youtube

# If not there, run setup again
python3 ~/.openclaw/workspace/.cache/setup-youtube-cron.py

# Test manually
bash ~/.openclaw/workspace/.cache/youtube-monitor-cron.sh
```

### Not seeing comments
```bash
# Make sure channel has comments enabled
# Check logs for errors
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log

# Try manual run
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

---

## 📚 Learn More

| Topic | File |
|-------|------|
| Full setup guide | `YOUTUBE-SETUP.md` |
| Command reference | `YOUTUBE-CHEATSHEET.md` |
| Complete documentation | `README-YOUTUBE-MONITOR.md` |
| Verification test | `test-youtube-setup.py` |

---

## 🚨 Quick Diagnostics

Run the test suite:
```bash
python3 ~/.openclaw/workspace/.cache/test-youtube-setup.py
```

Shows exactly what's working and what needs fixing.

---

## 📞 Stuck?

1. **Check logs:** `tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log`
2. **Run diagnostics:** `python3 ~/.openclaw/workspace/.cache/test-youtube-setup.py`
3. **Read full guide:** `~/.openclaw/workspace/.cache/YOUTUBE-SETUP.md`

---

## ✨ You're Ready!

Your monitor is now:
- ✓ Installed
- ✓ Configured  
- ✓ Running (every 30 min via cron)
- ✓ Logging all comments
- ✓ Auto-responding to questions & praise
- ✓ Flagging sales inquiries

**Enjoy automated YouTube comment management!** 🎬

---

**Last Updated:** April 18, 2026  
**Time Estimate:** 10 minutes total  
**Difficulty:** ⭐ Easy (guided setup)
