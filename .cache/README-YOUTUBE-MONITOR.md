# 🎬 YouTube Comment Monitor

Automated system to monitor the Concessa Obvius YouTube channel for new comments, categorize them, auto-respond intelligently, and flag outliers for review.

**Status:** Ready to deploy  
**Update Frequency:** Every 30 minutes (configurable)  
**Storage:** JSON Lines log at `.cache/youtube-comments.jsonl`

---

## ✨ Features

✅ **Automated Comment Monitoring** — Fetches new comments from the channel every 30 minutes  
✅ **Smart Categorization** — Classifies comments as: Questions, Praise, Spam, Sales, Other  
✅ **Auto-Responses** — Sends templated replies to Questions and Praise  
✅ **Sales Flagging** — Marks partnership/collaboration requests for manual review  
✅ **Complete Audit Trail** — Logs all comments with category, response status, timestamp  
✅ **Dashboard Viewer** — Real-time stats and recent comment browser  
✅ **Easy Setup** — One-command installation with guided setup

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd ~/.openclaw/workspace
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 2: Get YouTube Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project: **"Concessa Obvius Monitor"**
3. Enable **YouTube Data API v3**
4. Create OAuth 2.0 credentials (Desktop app)
5. Download JSON → Save to `.cache/youtube_credentials.json`

### Step 3: Run Setup Assistant

```bash
python3 ~/.openclaw/workspace/.cache/setup-youtube-cron.py
```

This will:
- ✓ Verify dependencies
- ✓ Check credentials
- ✓ Make scripts executable
- ✓ Set up cron job (every 30 min)
- ✓ Run initial authorization

### Step 4: Verify It's Running

```bash
# Check cron job is installed
crontab -l | grep youtube-monitor

# View monitor logs
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log

# See recent comments
python3 ~/.openclaw/workspace/.cache/youtube-monitor-dashboard.py
```

---

## 📁 Files

| File | Purpose |
|------|---------|
| `youtube-comment-monitor.py` | Main monitoring script |
| `youtube-monitor-cron.sh` | Cron wrapper (runs every 30 min) |
| `setup-youtube-cron.py` | Interactive setup assistant |
| `youtube-monitor-dashboard.py` | Dashboard viewer |
| `youtube-comments.jsonl` | Complete audit log (auto-created) |
| `youtube-monitor.log` | Monitor logs |
| `youtube-token.json` | OAuth token (auto-created, **keep secret**) |
| `YOUTUBE-SETUP.md` | Detailed setup guide |

---

## 🎯 Comment Categories

### 1️⃣ Questions
**Pattern:** How to, tools, pricing, timeline, recommendations  
**Response:** Helpful template with resources  
**Example:** *"How do I start? What tools do you use?"*

### 2️⃣ Praise
**Pattern:** Amazing, inspiring, helpful, life-changing  
**Response:** Thank you message  
**Example:** *"This is life-changing! Thank you so much!"*

### 3️⃣ Spam
**Pattern:** Crypto, MLM, "click here", suspicious links  
**Response:** None (deleted manually)  
**Example:** *"Bitcoin investment opportunity! 🚀💰"*

### 4️⃣ Sales
**Pattern:** Partnership, sponsorship, collaboration, business opportunity  
**Response:** Flagged for manual review  
**Example:** *"Let's collaborate on a partnership!"*

### 5️⃣ Other
**Pattern:** Doesn't fit above categories  
**Response:** None  

---

## 📊 Dashboard

View statistics and recent comments:

```bash
python3 ~/.openclaw/workspace/.cache/youtube-monitor-dashboard.py
```

Shows:
- Total comments processed
- Breakdown by category
- Auto-responses sent
- Flagged for review
- Top commenters
- Recent comments
- Flagged sales inquiries

---

## 📝 Log Format

All comments stored in `.cache/youtube-comments.jsonl` (one JSON per line):

```json
{
  "timestamp": "2026-04-18T19:30:45.123456",
  "videoId": "abc123xyz",
  "commentId": "UgxY...",
  "commenter": "John Doe",
  "authorChannelId": "UCabc123xyz",
  "text": "How do I get started?",
  "publishedAt": "2026-04-18T19:25:00Z",
  "category": "question",
  "response_status": "auto_responded"
}
```

**Query Examples:**

```bash
# View recent comments
tail -20 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | python3 -m json.tool

# Find all flagged comments
jq 'select(.response_status == "flagged_for_review")' ~/.openclaw/workspace/.cache/youtube-comments.jsonl

# Count by category
jq -r '.category' ~/.openclaw/workspace/.cache/youtube-comments.jsonl | sort | uniq -c

# Find comments from specific user
jq 'select(.commenter == "John Doe")' ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

---

## ⚙️ Customization

### Response Templates

Edit `youtube-comment-monitor.py`:

```python
RESPONSE_TEMPLATES = {
    "question": """Thanks for asking! Here's what I recommend...""",
    "praise": """Thank you so much for the kind words! 🙏""",
}
```

### Category Patterns

Adjust regex patterns in `PATTERNS` dict:

```python
PATTERNS = {
    "spam": [r"crypto|bitcoin", r"mlm|pyramid"],
    "sales": [r"partnership|sponsorship", r"brand deal"],
    "question": [r"how do", r"what.*cost", r"\?$"],
    "praise": [r"amazing|awesome", r"thank you"],
}
```

### Check Frequency

Edit crontab:

```bash
crontab -e

# Change from */30 to whatever frequency you want:
# */15 = every 15 minutes
# */60 = every 60 minutes
# 0 * = every hour at :00
```

### Channel ID

Update in `youtube-comment-monitor.py`:

```python
CHANNEL_ID = "UCxxxxxxxxxxxxxx"  # Get from YouTube channel URL
```

---

## 🔍 Monitoring

### Real-Time Logs

```bash
tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log
```

### Cron Execution Logs

```bash
tail -f ~/.openclaw/workspace/.cache/youtube-monitor-cron.log
```

### System Cron Logs (macOS)

```bash
log stream --predicate 'process == "cron"' | grep youtube
```

### Manual Run

```bash
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
```

---

## 🐛 Troubleshooting

### Credentials Error

```
❌ No valid YouTube credentials found
```

**Fix:**
1. Download JSON from Google Cloud Console
2. Save to `.cache/youtube_credentials.json`
3. Run setup assistant again
4. Delete `.cache/youtube_token.json` to force re-auth

### Channel Not Found

```
⚠️ Channel not found
```

**Fix:**
1. Verify correct channel ID in script
2. Check channel has public comments

### Rate Limited

```
Error: quota exceeded
```

**Info:**
- YouTube API has 10,000 quota/day limit
- Each comment fetch = 1 quota
- Each reply = 50 quota
- Check quota in Google Cloud Console

### Cron Not Running

```bash
# Check it's installed
crontab -l | grep youtube

# Test manually
bash ~/.openclaw/workspace/.cache/youtube-monitor-cron.sh

# Check logs
tail -f ~/.openclaw/workspace/.cache/youtube-monitor-cron.log
```

---

## 🔐 Security

⚠️ **Keep these files secret:**
- `youtube_credentials.json` — Never commit to git
- `youtube_token.json` — Contains refresh token

✅ **Best practices:**
- Add to `.gitignore`
- Audit auto-responses regularly
- Review flagged comments manually before approving partnerships

---

## 🤖 Advanced: LLM-Based Categorization

For more sophisticated categorization, use Claude:

```python
def categorize_comment(text: str) -> str:
    """Use Claude to categorize comments."""
    from anthropic import Anthropic
    
    client = Anthropic()
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=50,
        messages=[{
            "role": "user",
            "content": f"Categorize this comment as question/praise/spam/sales/other: {text}"
        }]
    )
    return response.content[0].text.strip().lower()
```

---

## 📊 Metrics & SLA

| Metric | Target |
|--------|--------|
| Check frequency | ✅ Every 30 minutes |
| Response latency | ✅ <2 min (auto) |
| Uptime | ✅ 99.5% (cron) |
| Accuracy | 📈 Improving with patterns |
| API quota | ✅ <500/day (safe limit) |

---

## 🎓 Usage Examples

### Check stats
```bash
python3 ~/.openclaw/workspace/.cache/youtube-monitor-dashboard.py
```

### Find unanswered questions
```bash
jq 'select(.category == "question" and .response_status == "none")' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl
```

### Export for analysis
```bash
jq -r '[.timestamp, .commenter, .category, .text] | @csv' \
  ~/.openclaw/workspace/.cache/youtube-comments.jsonl > comments.csv
```

### Monitor real-time
```bash
watch -n 30 'python3 ~/.openclaw/workspace/.cache/youtube-monitor-dashboard.py'
```

---

## 📞 Support

For issues:
1. Check logs: `tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log`
2. Run setup again: `python3 ~/.openclaw/workspace/.cache/setup-youtube-cron.py`
3. Read detailed guide: `.cache/YOUTUBE-SETUP.md`

---

**Last Updated:** 2026-04-18  
**Maintainer:** OpenClaw Bot  
**License:** MIT
