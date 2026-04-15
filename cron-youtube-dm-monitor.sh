#!/bin/bash
# YouTube DM Monitor - Hourly Cron Job
# Monitors Concessa Obvius DMs, categorizes, auto-responds, and logs

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
CACHE_DIR="/Users/abundance/.cache"
MONITOR_SCRIPT="$WORKSPACE/youtube-dm-monitor.py"
LOG_FILE="$CACHE_DIR/youtube-dms.jsonl"
REPORT_FILE="$CACHE_DIR/youtube-dm-report.json"

# Ensure cache directory exists
mkdir -p "$CACHE_DIR"

# Function to send report to Discord (if configured)
send_report() {
    local report_json="$1"
    
    # Parse stats from report
    total=$(jq '.total_dms' "$report_json" 2>/dev/null || echo "0")
    responses=$(jq '.auto_responses_sent' "$report_json" 2>/dev/null || echo "0")
    inquiries=$(jq '.conversion_potential' "$report_json" 2>/dev/null || echo "unknown")
    
    # Format message (would be sent to Discord via webhook or CLI)
    message="📊 **YouTube DM Monitor Report** ($(date +'%Y-%m-%d %H:%M'))\n\n"
    message="$message✓ **DMs Processed:** $total\n"
    message="$message✉️ **Auto-Responses Sent:** $responses\n"
    message="$message🎯 **Conversion Potential:** $inquiries"
    
    echo "$message"
}

# Main monitoring function
monitor_dms() {
    # This is a placeholder - actual DM data would come from:
    # 1. YouTube Data API (if DM endpoint available)
    # 2. Browser automation (Playwright/Selenium)
    # 3. Google Cloud Pub/Sub webhook from YouTube
    # 4. YouTube Studio integration
    
    echo "🔍 YouTube DM Monitor - $(date)"
    echo "Current status: Awaiting YouTube integration"
    echo ""
    echo "To enable live monitoring, configure:"
    echo "  1. YouTube Data API credentials → .env"
    echo "  2. Or: Connect browser session for manual DM polling"
    echo "  3. Or: Setup Google Cloud Pub/Sub webhook"
    
    # For now, show the test data
    python3 "$MONITOR_SCRIPT" > /tmp/dm-monitor-output.txt 2>&1
    
    # Generate report
    python3 << 'PYTHON_EOF'
import json
import sys

log_file = "/Users/abundance/.cache/youtube-dms.jsonl"
report_file = "/Users/abundance/.cache/youtube-dm-report.json"

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

categories = {}
product_inquiries = 0
partnerships_flagged = 0
flagged_partnerships = []

for dm in dms:
    cat = dm.get("category")
    categories[cat] = categories.get(cat, 0) + 1
    
    if cat == "product_inquiry":
        product_inquiries += 1
    if dm.get("interesting_partnership"):
        partnerships_flagged += 1
        flagged_partnerships.append({
            "sender": dm.get("sender"),
            "timestamp": dm.get("timestamp"),
            "preview": dm.get("text")[:100] + "..."
        })

report = {
    "timestamp": pd.Timestamp.now().isoformat() if 'pd' in dir() else str(__import__('datetime').datetime.now().isoformat()),
    "total_dms": len(dms),
    "auto_responses_sent": len([d for d in dms if d.get("response_sent")]),
    "by_category": categories,
    "partnerships_flagged": partnerships_flagged,
    "flagged_partnerships": flagged_partnerships,
    "conversion_potential": f"{product_inquiries} product inquiries to follow up on"
}

with open(report_file, "w") as f:
    json.dump(report, f, indent=2)

print(f"✅ Report generated: {report_file}")
print(f"📊 Total DMs: {report['total_dms']}")
print(f"✉️  Auto-responses: {report['auto_responses_sent']}")
print(f"🎯 Product inquiries: {product_inquiries}")
print(f"🚩 Partnerships flagged: {partnerships_flagged}")

if flagged_partnerships:
    print("\n⭐ Interesting partnerships for manual review:")
    for p in flagged_partnerships:
        print(f"  • {p['sender']} ({p['timestamp']})")
        print(f"    {p['preview']}")
PYTHON_EOF
}

# Run monitor
monitor_dms

# Print summary
echo ""
echo "✅ YouTube DM Monitor completed at $(date)"
