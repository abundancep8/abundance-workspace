# 🎥 YouTube Comment Monitor - Concessa Obvius Channel

A fully automated system to monitor, categorize, and respond to YouTube comments on the Concessa Obvius channel.

**Status:** Ready to configure | **Runs:** Every 30 minutes (cron)

---

## 📋 What It Does

1. **Monitors** the Concessa Obvius YouTube channel for new comments
2. **Categorizes** each comment:
   - 🤔 **Questions** (How do I...? Tools? Cost? Timeline?)
   - 👏 **Praise** (Amazing, inspiring, love this)
   - 🚫 **Spam** (Crypto, MLM, unrelated)
   - 🤝 **Sales** (Partnerships, collaborations)
3. **Auto-responds** to questions and praise with templates
4. **Flags** sales inquiries for your review
5. **Logs everything** to `.cache/youtube-comments.jsonl`
6. **Reports** stats each run

---

## 🚀 Quick Start (5 minutes)

### Step 1: Run Setup Script

```bash
chmod +x .cache/youtube-setup.sh
./.cache/youtube-setup.sh
```

This will:
- Install Python dependencies
- Save your YouTube API credentials
- Set the channel ID environment variable

### Step 2: Test the Monitor

```bash
python3 .cache/youtube-monitor.py
```

You should see output like:
```
🎥 YouTube Comment Monitor - Concessa Obvius
⏰ 2026-04-19 06:30:15

📊 Session Report:
   Total processed: 5
   Auto-responses sent: 3
   Flagged for review: 1
```

### Step 3: View Analytics

```bash
python3 .cache/youtube-analytics.py
```

Full report with trends, top commenters, and flagged items.

---

## 📁 Files

| File | Purpose |
|------|---------|
| `youtube-monitor.py` | Main monitoring script (runs every 30 min) |
| `youtube-analytics.py` | Analytics & reporting tool |
| `youtube-setup.sh` | One-time setup (credentials, channel ID) |
| `youtube-comments.jsonl` | Comment log (JSON Lines format) |
| `youtube-monitor-state.json` | Last processed comment (internal) |
| `YOUTUBE_SETUP.md` | Detailed setup guide |
| `README-YOUTUBE.md` | This file |

---

## 🔧 Configuration

### YouTube API Credentials

Get credentials from Google Cloud Console:

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project
3. Enable **YouTube Data API v3**
4. Create OAuth 2.0 credentials (Desktop app)
5. Download JSON file
6. Run setup script (it will copy it for you) or manually:
   ```bash
   cp /path/to/credentials.json ~/.openclaw/youtube-credentials.json
   ```

### Channel ID

Find the Concessa Obvius channel ID:
1. Go to channel
2. Click "About"
3. Look for Channel ID (format: `UC` + 22 characters)
4. Set environment variable:
   ```bash
   export YOUTUBE_CHANNEL_ID="UCxxxxxxxxxxxxxxxxxxxxxxxx"
   # Add to ~/.zshrc or ~/.bashrc to persist
   ```

### Auto-Response Templates

Edit `youtube-monitor.py` and modify `TEMPLATES`:

```python
TEMPLATES = {
    1: "Thanks for the question! Here's a link: [insert-url]",
    2: "🙏 Your support means everything!",
}
```

---

## 📊 Outputs

### Session Report (printed each run)
```
📊 Session Report:
   Total processed: 5
   Auto-responses sent: 3
   Flagged for review: 1

📈 Cumulative Stats:
   Total comments logged: 42
   By category: Q=12 | Praise=18 | Spam=8 | Sales=4
   Auto-responses sent: 28
   Flagged for review: 4
```

### JSON Log Format
Each comment in `youtube-comments.jsonl`:
```json
{
  "timestamp": "2026-04-19T13:30:15+00:00",
  "comment_id": "Zxxxxxxxxxxxx",
  "commenter": "John Doe",
  "text": "How do I get started?",
  "category": 1,
  "response_status": "auto_response_queued"
}
```

### Analytics Report
```
python3 .cache/youtube-analytics.py
```

Shows:
- Total comments by category
- Response statistics
- 7-day activity timeline
- Top commenters
- Recent flagged items

---

## ⚙️ Cron Integration

The cron job `114e5c6d-ac8b-47ca-a695-79ac31b5c076` runs every 30 minutes:

```
*/30 * * * * python3 ~/.openclaw/workspace/.cache/youtube-monitor.py
```

**Manual run:**
```bash
python3 .cache/youtube-monitor.py
```

**View recent runs:**
```bash
python3 .cache/youtube-analytics.py
```

---

## 🤖 Auto-Response Status

Comments get flagged with one of:

- `none` — No response (spam category)
- `auto_response_queued` — Template response prepared (categories 1-2)
- `flagged_for_review` — Sales inquiry, needs your review (category 4)

**Current behavior:** Responses are queued, not auto-posted. You review and approve before posting.

To enable auto-posting:
1. Authenticate with YouTube OAuth (handled by setup)
2. Uncomment the reply posting code in `youtube-monitor.py`
3. Restart monitor

---

## 📖 Examples

### Example: Question Comment
```
👤 Jane Smith
"How do I get started with [product]? Is there a free trial?"

📂 Category: 1 (Question)
💬 Response: Auto-responded with template
```

### Example: Sales Inquiry
```
👤 acme-partnerships@example.com
"Hey! We'd love to discuss a partnership opportunity."

📂 Category: 4 (Sales)
🚩 Response: Flagged for review
```

### Example: Spam
```
👤 CryptoBot2000
"Get rich quick with Bitcoin! Check my channel! 🚀💰"

📂 Category: 3 (Spam)
💬 Response: None (logged only)
```

---

## 🛠 Troubleshooting

**"YouTube credentials not found"**
```bash
./.cache/youtube-setup.sh
# Or manually copy to: ~/.openclaw/youtube-credentials.json
```

**"YOUTUBE_CHANNEL_ID not set"**
```bash
export YOUTUBE_CHANNEL_ID="UCxxxxxxxx"
# Add to ~/.zshrc for persistence
```

**"No comments found"**
- Channel may have comments disabled
- YouTube API quota exceeded (check Google Cloud Console)
- Check that the correct channel ID is set

**"ModuleNotFoundError: No module named 'google'"**
```bash
pip install google-auth-oauthlib google-api-python-client
```

---

## 📈 Next Steps

1. ✅ Run setup script: `./.cache/youtube-setup.sh`
2. ✅ Test monitor: `python3 .cache/youtube-monitor.py`
3. ✅ Customize templates in `youtube-monitor.py`
4. ✅ Enable auto-posting (optional, requires auth)
5. ✅ Check analytics daily: `python3 .cache/youtube-analytics.py`
6. 🚩 Review flagged sales inquiries manually

---

## 📞 Support

For issues with:
- **YouTube API:** [google.com/youtube/v3/docs](https://google.com/youtube/v3/docs)
- **Setup:** Read `YOUTUBE_SETUP.md`
- **Analytics:** Run with `--help` flag

---

**Last updated:** 2026-04-19  
**Cron job:** 114e5c6d-ac8b-47ca-a695-79ac31b5c076  
**Schedule:** Every 30 minutes
