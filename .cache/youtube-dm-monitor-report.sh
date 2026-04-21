#!/bin/bash
# YouTube DM Monitor - Hourly Report Script
# Triggered by cron: every hour

set -e

WORKSPACE="$HOME/.openclaw/workspace"
LOG_FILE="$WORKSPACE/.cache/youtube-dms.jsonl"
REPORT_FILE="$WORKSPACE/.cache/youtube-dms-report.json"

# Create report directory if needed
mkdir -p "$WORKSPACE/.cache"

# Run Python monitoring script
cd "$WORKSPACE"

# Count stats
TOTAL_DMS=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
RESPONSES_SENT=$(grep -c '"response_sent": true' "$LOG_FILE" 2>/dev/null || echo "0")
SETUP_COUNT=$(grep -c '"category": "setup_help"' "$LOG_FILE" 2>/dev/null || echo "0")
NEWSLETTER_COUNT=$(grep -c '"category": "newsletter"' "$LOG_FILE" 2>/dev/null || echo "0")
PRODUCT_COUNT=$(grep -c '"category": "product_inquiry"' "$LOG_FILE" 2>/dev/null || echo "0")
PARTNERSHIP_COUNT=$(grep -c '"category": "partnership"' "$LOG_FILE" 2>/dev/null || echo "0")

# Generate JSON report
cat > "$REPORT_FILE" <<EOF
{
  "timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "monitoring_channel": "Concessa Obvius",
  "statistics": {
    "total_dms_processed": $TOTAL_DMS,
    "auto_responses_sent": $RESPONSES_SENT,
    "response_rate_percent": $((RESPONSES_SENT * 100 / (TOTAL_DMS > 0 ? TOTAL_DMS : 1)))
  },
  "by_category": {
    "setup_help": $SETUP_COUNT,
    "newsletter": $NEWSLETTER_COUNT,
    "product_inquiry": $PRODUCT_COUNT,
    "partnership": $PARTNERSHIP_COUNT
  },
  "conversion_opportunities": "See partnership_flags below",
  "partnership_flags": $(python3 -c "
import json
from pathlib import Path

log_file = Path('$LOG_FILE')
partnerships = []

if log_file.exists():
    with open(log_file) as f:
        for line in f:
            entry = json.loads(line)
            if entry.get('category') == 'partnership' and entry.get('response_sent'):
                partnerships.append({
                    'timestamp': entry['timestamp'],
                    'sender': entry.get('sender', 'Unknown'),
                    'text_preview': entry['text'][:80] + '...'
                })

print(json.dumps(partnerships, indent=2))
")
}
EOF

# Print summary
echo "📊 YouTube DM Monitor - Hourly Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Timestamp: $(date)"
echo "Total DMs Processed: $TOTAL_DMS"
echo "Auto-Responses Sent: $RESPONSES_SENT"
echo ""
echo "By Category:"
echo "  • Setup Help: $SETUP_COUNT"
echo "  • Newsletter: $NEWSLETTER_COUNT"
echo "  • Product Inquiry: $PRODUCT_COUNT"
echo "  • Partnership: $PARTNERSHIP_COUNT"
echo ""

if [ "$PARTNERSHIP_COUNT" -gt 0 ]; then
    echo "🤝 Partnership Opportunities (flagged for manual review):"
    grep '"category": "partnership"' "$LOG_FILE" 2>/dev/null | tail -3 | while read line; do
        SENDER=$(echo "$line" | python3 -c "import sys, json; print(json.load(sys.stdin).get('sender', 'Unknown'))")
        TEXT=$(echo "$line" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('text', 'N/A')[:100])")
        echo "  - $SENDER: $TEXT"
    done
    echo ""
fi

echo "✅ Report saved to: $REPORT_FILE"
