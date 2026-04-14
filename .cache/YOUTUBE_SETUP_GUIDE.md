# YouTube Comment Monitor — Setup Guide

## ✋ Current Status

The monitor script is ready, but **YouTube API authentication is not configured**. The monitor will run every 30 minutes but won't fetch comments until you complete setup.

## 🔧 Setup Steps

### 1. Install Python Dependencies
```bash
pip install google-auth google-auth-httplib2 google-api-python-client
```

### 2. Create YouTube API Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **YouTube Data API v3**:
   - Search for "YouTube Data API v3"
   - Click "Enable"

### 3. Create Service Account (Recommended for Cron)
1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → Service Account**
3. Fill in service account details (name: `youtube-monitor`)
4. Click **Create and Continue**
5. Grant role: **Viewer** (basic read-only access)
6. Skip "Grant users access"
7. Click **Done**

### 4. Create and Download Key
1. Go back to **Credentials**
2. Under **Service Accounts**, click the account you just created
3. Go to **Keys** tab
4. Click **Add Key → Create new key**
5. Choose **JSON**
6. This downloads a JSON file
7. Rename it to `youtube-credentials.json`
8. Move it to: `.cache/youtube-credentials.json` in your workspace

### 5. Update Channel Handle
Edit `.cache/youtube-comment-monitor.py` line ~21:
```python
CHANNEL_HANDLE = "ConcessaObvius"  # Update with actual handle
```

Replace with the actual YouTube channel name or handle.

### 6. Test the Monitor
```bash
python3 .cache/youtube-comment-monitor.py
```

Should show:
```
⚙️  STATUS
  API availability: ✓ OK
  Credentials: ✓ Found
```

## 📋 Monitoring Features (Once Configured)

- ✅ Fetches new comments every 30 minutes (via cron)
- ✅ Auto-categorizes: Questions, Praise, Spam, Sales
- ✅ Auto-responds to Questions & Praise
- ✅ Flags Sales inquiries for manual review
- ✅ Logs everything to `.cache/youtube-comments.jsonl`
- ✅ Generates summary report with stats

## 🚨 Troubleshooting

**"API not available"**
→ Run: `pip install google-auth google-auth-httplib2 google-api-python-client`

**"Credentials: Missing"**
→ Download service account JSON key and place in `.cache/youtube-credentials.json`

**"Channel not found"**
→ Verify `CHANNEL_HANDLE` matches the actual YouTube channel name

**"403 Forbidden"**
→ Service account may need channel access. Check YouTube API permissions.

## 🔄 Cron Integration

Once configured, the monitor runs automatically every 30 minutes and:
- Processes new comments
- Logs them with timestamp, commenter, text, category, response status
- Reports total processed, auto-responses sent, flagged for review

---

Questions? Check the script comments or YouTube API docs: https://developers.google.com/youtube/v3
