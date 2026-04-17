#!/bin/bash
# YouTube DM Monitor - Status & Quick View

CACHE_DIR="${HOME}/.openclaw/workspace/.cache"
DMS_LOG="${CACHE_DIR}/youtube-dms.jsonl"
REPORT_FILE="${CACHE_DIR}/youtube-dm-report.txt"

echo "📊 YouTube DM Monitor Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Show latest report if it exists
if [ -f "${REPORT_FILE}" ]; then
    echo "📋 Latest Report:"
    echo ""
    cat "${REPORT_FILE}"
else
    echo "⚠️  No reports generated yet. Run the monitor first."
    echo ""
fi

echo ""
echo "📁 Cache Files:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f "${DMS_LOG}" ]; then
    dm_count=$(wc -l < "${DMS_LOG}")
    echo "✅ youtube-dms.jsonl: $dm_count entries"
    
    echo ""
    echo "Recent entries:"
    tail -3 "${DMS_LOG}" | jq '"\(.timestamp) | \(.sender) (\(.category))"' -r
else
    echo "⚠️  youtube-dms.jsonl: Not created yet"
fi

echo ""
echo "🔍 Quick Queries:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "View all partnerships:"
echo "  jq 'select(.category == \"partnership\")' ${DMS_LOG}"
echo ""
echo "Count by category:"
echo "  jq -s 'group_by(.category) | map({category: .[0].category, count: length})' ${DMS_LOG}"
echo ""
echo "View DMs from specific sender:"
echo "  jq 'select(.sender == \"username\")' ${DMS_LOG}"
echo ""
