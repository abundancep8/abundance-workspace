#!/bin/bash
# YouTube DM Monitor - Hourly Cron Job (Live Version)
# Monitors Concessa Obvius DMs from YouTube Studio, categorizes, logs, and reports

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
CACHE_DIR="${WORKSPACE}/.cache"
MONITOR_SCRIPT="${WORKSPACE}/youtube-dm-monitor-live.py"
LOG_FILE="${CACHE_DIR}/youtube-dms.jsonl"
REPORT_FILE="${CACHE_DIR}/youtube-dm-report.json"
CRON_LOG="${CACHE_DIR}/youtube-dm-monitor.log"

# Ensure cache directory exists
mkdir -p "$CACHE_DIR"

# Log function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$CRON_LOG"
}

log "========================================="
log "YouTube DM Monitor - Hourly Run"
log "========================================="

# Check if monitor script exists
if [ ! -f "$MONITOR_SCRIPT" ]; then
    log "❌ ERROR: Monitor script not found: $MONITOR_SCRIPT"
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    log "❌ ERROR: Python 3 not found"
    exit 1
fi

# Install dependencies if needed
log "Checking dependencies..."
python3 -c "import playwright" 2>/dev/null || {
    log "Installing Playwright..."
    python3 -m pip install playwright -q
    python3 -m playwright install chromium -q
}

# Run the monitor
log "Starting DM monitor..."
python3 "$MONITOR_SCRIPT" --report >> "$CRON_LOG" 2>&1

# Check if monitor ran successfully
if [ $? -eq 0 ]; then
    log "✅ Monitor completed successfully"
else
    log "⚠️  Monitor completed with warnings"
fi

# Generate report JSON for Discord/API consumption
python3 << 'PYTHON_REPORT'
import json
import os
from datetime import datetime
from pathlib import Path

log_file = os.path.expanduser("~/.cache/youtube-dms.jsonl")
report_file = os.path.expanduser("~/.cache/youtube-dm-report.json")

# Parse logs
dms = []
try:
    with open(log_file, "r") as f:
        for line in f:
            if line.strip():
                try:
                    dms.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
except FileNotFoundError:
    dms = []

# Categorize
categories = {}
product_inquiries = []
partnerships_flagged = []

for dm in dms:
    cat = dm.get("category")
    categories[cat] = categories.get(cat, 0) + 1
    
    if cat == "product_inquiry":
        product_inquiries.append(dm)
    
    if dm.get("interesting_partnership"):
        partnerships_flagged.append({
            "sender": dm.get("sender"),
            "timestamp": dm.get("timestamp"),
            "preview": dm.get("text")[:100] + "..."
        })

# Build report
report = {
    "timestamp": datetime.now().isoformat(),
    "status": "completed",
    "total_dms_processed": len(dms),
    "auto_responses_sent": len([d for d in dms if d.get("response_sent")]),
    "by_category": categories,
    "partnerships_flagged": len(partnerships_flagged),
    "interesting_partnerships": partnerships_flagged,
    "product_inquiries": len(product_inquiries),
    "conversion_potential": f"{len(product_inquiries)} product inquiry/inquiries to follow up on"
}

# Save report
with open(report_file, "w") as f:
    json.dump(report, f, indent=2)

# Print summary
print(f"\n📊 REPORT SUMMARY")
print(f"Total DMs: {report['total_dms_processed']}")
print(f"Auto-responses sent: {report['auto_responses_sent']}")
print(f"Categories: {report['by_category']}")
print(f"Partnerships flagged: {report['partnerships_flagged']}")
print(f"Conversion potential: {report['conversion_potential']}")

if partnerships_flagged:
    print(f"\n⭐ {len(partnerships_flagged)} interesting partnerships for manual review:")
    for p in partnerships_flagged:
        print(f"  • {p['sender']} ({p['timestamp']})")
        print(f"    {p['preview']}")

PYTHON_REPORT

# Send report to Discord (optional - requires webhook configured)
if [ -n "$YOUTUBE_MONITOR_WEBHOOK" ]; then
    log "Sending report to Discord..."
    
    REPORT_JSON=$(cat "$REPORT_FILE")
    TOTAL=$(echo "$REPORT_JSON" | jq '.total_dms_processed')
    RESPONSES=$(echo "$REPORT_JSON" | jq '.auto_responses_sent')
    PARTNERSHIPS=$(echo "$REPORT_JSON" | jq '.partnerships_flagged')
    INQUIRIES=$(echo "$REPORT_JSON" | jq -r '.conversion_potential')
    
    MESSAGE="{\"content\": \"📊 **YouTube DM Monitor Report**\n✓ **DMs Processed:** $TOTAL\n✉️ **Auto-Responses:** $RESPONSES\n🤝 **Partnerships Flagged:** $PARTNERSHIPS\n🎯 **Conversion Potential:** $INQUIRIES\"}"
    
    curl -X POST "$YOUTUBE_MONITOR_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "$MESSAGE" \
        2>/dev/null && log "✅ Report sent to Discord" || log "⚠️  Discord webhook failed"
fi

log "✅ Completed at $(date +'%Y-%m-%d %H:%M:%S')"
log ""
