# YouTube Comment Monitor - OpenClaw Integration Guide

## Quick Start

1. **Run setup:**
   ```bash
   bash ~/.openclaw/workspace/.cache/youtube-monitor-setup.sh
   ```

2. **Add credentials:**
   - Go to Google Cloud Console → Create OAuth2 credentials
   - Save to `~/.openclaw/secrets/youtube.json`

3. **Test it:**
   ```bash
   python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py --dry-run
   ```

---

## Integration Methods

### Option 1: Heartbeat Monitoring (Recommended)

Add to your `HEARTBEAT.md`:

```yaml
## YouTube Comment Monitor

Run every 6 hours to check for new comments.

Command:
  python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py

Check:
  - View log: tail -f ~/.openclaw/workspace/.cache/youtube-monitor.log
  - JSON: cat ~/.openclaw/workspace/.cache/youtube-comments.jsonl | tail -5 | jq .
  - Summary: grep "total_processed" ~/.openclaw/workspace/.cache/youtube-monitor.log

Expected:
  - total_processed > 0 (new comments found)
  - flagged_sales gets review attention
  - auto_responses_sent logged

Alert if:
  - Errors > 0
  - Credentials expired
  - API quota exceeded
```

### Option 2: Cron Scheduling

**Every 3 hours:**
```bash
0 */3 * * * cd ~/.openclaw/workspace && python3 .cache/youtube-comment-monitor.py >> .cache/youtube-monitor-cron.log 2>&1
```

**Twice daily (6 AM & 6 PM):**
```bash
0 6,18 * * * cd ~/.openclaw/workspace && python3 .cache/youtube-comment-monitor.py >> .cache/youtube-monitor-cron.log 2>&1
```

**Once daily (9 AM):**
```bash
0 9 * * * cd ~/.openclaw/workspace && python3 .cache/youtube-comment-monitor.py >> .cache/youtube-monitor-cron.log 2>&1
```

### Option 3: Workflow Automation (Advanced)

If using `agentic-workflow-automation` skill, create `.cache/youtube-monitor-workflow.yaml`:

```yaml
name: YouTube Comment Monitoring
description: Periodic monitoring with review alerts

trigger:
  type: cron
  schedule: "0 */6 * * *"  # Every 6 hours
  timezone: America/Los_Angeles

context:
  script_path: ~/.openclaw/workspace/.cache/youtube-comment-monitor.py
  log_file: ~/.openclaw/workspace/.cache/youtube-comments.jsonl
  max_comments: 20

steps:
  - name: fetch_and_process
    action: execute
    command: "python3 {{ script_path }} --max-comments {{ max_comments }}"
    timeout: 30s
    on_error: log_and_continue

  - name: parse_report
    action: evaluate
    script: |
      import json
      with open('/tmp/youtube-monitor-report.json') as f:
        report = json.load(f)
      return report

  - name: check_sales_inquiries
    action: conditional
    condition: "{{ parse_report.flagged_sales > 0 }}"
    then:
      - notify_user:
          channel: discord
          message: |
            🔔 **YouTube Comment Alert**
            Sales inquiries flagged for review: {{ parse_report.flagged_sales }}
            Auto-responses sent: {{ parse_report.auto_responses_sent }}
          color: orange

  - name: check_errors
    action: conditional
    condition: "{{ parse_report.errors > 0 }}"
    then:
      - notify_user:
          channel: discord
          message: |
            ⚠️ **YouTube Monitor Error**
            Errors encountered: {{ parse_report.errors }}
            Check: ~/.openclaw/workspace/.cache/youtube-monitor.log
          color: red

  - name: archive_comments
    action: execute
    command: |
      cp ~/.openclaw/workspace/.cache/youtube-comments.jsonl \
         ~/.openclaw/workspace/.cache/youtube-comments-$(date +%Y%m%d-%H%M%S).jsonl
    on_error: log_only

exit_criteria:
  - success: report.status == "success"
  - degraded: report.status == "completed_with_errors"
  - failed: report.status == "failed"
```

Run with:
```bash
openclaw workflow run .cache/youtube-monitor-workflow.yaml
```

---

## Discord Integration

Send alerts to Discord when comments arrive:

```bash
# After running monitor, check for sales inquiries
if grep -q '"category": "sales"' ~/.openclaw/workspace/.cache/youtube-comments.jsonl; then
    python3 << 'EOF'
import json
import subprocess
from pathlib import Path

# Read last comment
log_file = Path.home() / '.openclaw' / 'workspace' / '.cache' / 'youtube-comments.jsonl'
with open(log_file) as f:
    last_line = f.readlines()[-1]
    comment = json.loads(last_line)

# Send to Discord
message = f"""
🎬 **New YouTube Comment**
From: {comment['commenter']}
Category: {comment['category'].upper()}
Text: {comment['text'][:100]}...
"""

subprocess.run([
    'openclaw', 'message', 'send',
    '--channel', 'youtube-monitoring',
    '--message', message
])
EOF
fi
```

---

## Monitoring Dashboard

Create a simple HTML dashboard to visualize comments:

```html
<!-- ~/.openclaw/workspace/.cache/youtube-dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Comments Monitor</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .stat { display: inline-block; margin: 20px; padding: 10px; border: 1px solid #ddd; }
        .comment { margin: 10px 0; padding: 10px; border-left: 4px solid #007bff; }
        .question { border-left-color: #17a2b8; }
        .praise { border-left-color: #28a745; }
        .sales { border-left-color: #ffc107; }
        .spam { border-left-color: #dc3545; }
    </style>
</head>
<body>
    <h1>📺 YouTube Comment Monitor</h1>
    <div id="stats"></div>
    <div id="comments"></div>
    <script>
        async function loadComments() {
            try {
                const response = await fetch('.cache/youtube-comments.jsonl');
                const text = await response.text();
                const lines = text.trim().split('\n');
                
                // Stats
                const stats = {};
                lines.forEach(line => {
                    const comment = JSON.parse(line);
                    stats[comment.category] = (stats[comment.category] || 0) + 1;
                });
                
                // Render stats
                let html = '<div id="stats">';
                for (const [cat, count] of Object.entries(stats)) {
                    html += `<div class="stat">${cat}: ${count}</div>`;
                }
                html += '</div>';
                document.body.innerHTML += html;
                
                // Render recent comments
                html = '<h2>Recent Comments</h2>';
                lines.slice(-10).reverse().forEach(line => {
                    const comment = JSON.parse(line);
                    html += `
                        <div class="comment ${comment.category}">
                            <strong>${comment.commenter}</strong> (${comment.category})
                            <p>${comment.text.substring(0, 200)}</p>
                            <small>${comment.timestamp}</small>
                        </div>
                    `;
                });
                document.body.innerHTML += html;
            } catch (e) {
                console.error('Error loading comments:', e);
            }
        }
        loadComments();
        setInterval(loadComments, 30000); // Refresh every 30s
    </script>
</body>
</html>
```

Open in browser: `file://$HOME/.openclaw/workspace/.cache/youtube-dashboard.html`

---

## Troubleshooting

### "Credentials file not found"
```bash
# Ensure credentials are saved
ls -la ~/.openclaw/secrets/youtube.json

# Create directory if missing
mkdir -p ~/.openclaw/secrets
```

### "No comments found"
```bash
# Check channel has public videos with comments enabled
python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py --dry-run -v

# Verify channel ID
echo "Checking channel UC32674..."
```

### "Rate limit exceeded"
```bash
# Reduce frequency or check quota
# Google Cloud Console → YouTube Data API → Quotas

# For now, increase interval to 12 hours
crontab -e
# Change: 0 */3 → 0 */12
```

### Check logs
```bash
# Main log
tail -50 ~/.openclaw/workspace/.cache/youtube-monitor.log

# JSON comments
tail -5 ~/.openclaw/workspace/.cache/youtube-comments.jsonl | jq .

# Cron log (if using cron)
tail -50 ~/.openclaw/workspace/.cache/youtube-monitor-cron.log
```

---

## Next Steps

1. ✅ Run setup: `bash ~/.openclaw/workspace/.cache/youtube-monitor-setup.sh`
2. ✅ Add credentials to `~/.openclaw/secrets/youtube.json`
3. ✅ Test: `python3 ~/.openclaw/workspace/.cache/youtube-comment-monitor.py --dry-run`
4. ✅ Add to HEARTBEAT.md or cron
5. ✅ (Optional) Set up Discord alerts
6. ✅ (Optional) Create dashboard

**Questions?** Check the main README:
```bash
cat ~/.openclaw/workspace/.cache/YOUTUBE-MONITOR-README.md
```
