#!/bin/bash
# YouTube Comment Monitor - Status Report

WORKSPACE="/Users/abundance/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"

cd "$WORKSPACE"

echo "════════════════════════════════════════════════════════════"
echo "  YouTube Comment Monitor - Status Report"
echo "════════════════════════════════════════════════════════════"
echo ""

# Check if .cache directory exists
if [ ! -d "$CACHE_DIR" ]; then
    echo "⚠️  No .cache directory found. Monitor hasn't run yet."
    echo ""
    echo "Next steps:"
    echo "1. Set YOUTUBE_API_KEY and YOUTUBE_CHANNEL_ID env vars"
    echo "2. Run: python scripts/youtube-comment-monitor.py"
    echo ""
    exit 0
fi

# Check log file
if [ -f "$CACHE_DIR/youtube-comments.jsonl" ]; then
    TOTAL_COMMENTS=$(wc -l < "$CACHE_DIR/youtube-comments.jsonl")
    echo "📊 Total Comments Logged: $TOTAL_COMMENTS"
    
    # Count by category
    echo ""
    echo "Comments by Category:"
    echo "  Questions:      $(jq -r 'select(.category==1)' "$CACHE_DIR/youtube-comments.jsonl" 2>/dev/null | wc -l)"
    echo "  Praise:         $(jq -r 'select(.category==2)' "$CACHE_DIR/youtube-comments.jsonl" 2>/dev/null | wc -l)"
    echo "  Spam:           $(jq -r 'select(.category==3)' "$CACHE_DIR/youtube-comments.jsonl" 2>/dev/null | wc -l)"
    echo "  Sales/Partners: $(jq -r 'select(.category==4)' "$CACHE_DIR/youtube-comments.jsonl" 2>/dev/null | wc -l)"
    echo "  Uncategorized:  $(jq -r 'select(.category==0)' "$CACHE_DIR/youtube-comments.jsonl" 2>/dev/null | wc -l)"
    
    # Count auto-responses
    AUTO_RESPONSES=$(jq -r 'select(.response_sent==true)' "$CACHE_DIR/youtube-comments.jsonl" 2>/dev/null | wc -l)
    echo ""
    echo "💬 Auto-Responses Sent: $AUTO_RESPONSES"
else
    echo "⚠️  No comments logged yet."
fi

# Check review file
if [ -f "$CACHE_DIR/youtube-review.txt" ]; then
    REVIEW_COUNT=$(grep -c "^--- " "$CACHE_DIR/youtube-review.txt" 2>/dev/null || echo 0)
    echo "🚩 Flagged for Review: $REVIEW_COUNT"
    
    if [ "$REVIEW_COUNT" -gt 0 ]; then
        echo ""
        echo "Recent Flagged Comments:"
        echo "─────────────────────────────────────────────────────────"
        tail -30 "$CACHE_DIR/youtube-review.txt"
    fi
else
    echo "🚩 Flagged for Review: 0 (none yet)"
fi

# Check state
echo ""
echo "📅 Last Check:"
if [ -f "$CACHE_DIR/youtube-monitor.json" ]; then
    LAST_CHECKED=$(jq -r '.last_checked' "$CACHE_DIR/youtube-monitor.json" 2>/dev/null)
    echo "    $LAST_CHECKED"
    PROCESSED=$(jq '.processed_comments | length' "$CACHE_DIR/youtube-monitor.json" 2>/dev/null)
    echo "    ($PROCESSED total processed)"
else
    echo "    Never (script not run yet)"
fi

# Check cron status
echo ""
echo "⏰ Cron Status:"
if crontab -l 2>/dev/null | grep -q "youtube-monitor-cron.sh"; then
    echo "    ✅ Cron job is installed"
    echo ""
    echo "Cron Schedule:"
    crontab -l | grep "youtube-monitor-cron.sh"
else
    echo "    ❌ Cron job is NOT installed"
    echo ""
    echo "To install:"
    echo "    crontab -e"
    echo "    Add: */30 * * * * $WORKSPACE/scripts/youtube-monitor-cron.sh"
fi

# Check environment
echo ""
echo "🔐 Environment:"
if [ -n "$YOUTUBE_API_KEY" ]; then
    echo "    ✅ YOUTUBE_API_KEY is set"
else
    echo "    ❌ YOUTUBE_API_KEY is NOT set"
fi

if [ -n "$YOUTUBE_CHANNEL_ID" ]; then
    echo "    ✅ YOUTUBE_CHANNEL_ID is set"
else
    echo "    ❌ YOUTUBE_CHANNEL_ID is NOT set"
fi

# Check log file
echo ""
echo "📝 Logs:"
if [ -f "$CACHE_DIR/monitor.log" ]; then
    LAST_LOG_TIME=$(tail -1 "$CACHE_DIR/monitor.log" | grep -oP '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}' | tail -1)
    if [ -n "$LAST_LOG_TIME" ]; then
        echo "    Last run: $LAST_LOG_TIME"
    else
        echo "    Monitor has run"
    fi
    echo "    Location: $CACHE_DIR/monitor.log"
else
    echo "    No logs yet"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Files:"
echo "  • Comments:  $CACHE_DIR/youtube-comments.jsonl"
echo "  • Review:    $CACHE_DIR/youtube-review.txt"
echo "  • State:     $CACHE_DIR/youtube-monitor.json"
echo "  • Logs:      $CACHE_DIR/monitor.log"
echo ""
echo "View recent comments:"
echo "  tail -5 .cache/youtube-comments.jsonl | jq ."
echo ""
echo "View flagged for review:"
echo "  cat .cache/youtube-review.txt"
echo ""
