#!/bin/bash
# YouTube Comments Log Analyzer
# Analyze patterns and generate statistics from youtube-comments.jsonl

LOG_FILE="${1:-.cache/youtube-comments.jsonl}"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file not found: $LOG_FILE"
    exit 1
fi

echo "════════════════════════════════════════════════════════════"
echo "  YouTube Comments Analysis"
echo "════════════════════════════════════════════════════════════"
echo ""

# Total comments
TOTAL=$(grep -c "^{" "$LOG_FILE" 2>/dev/null || wc -l < "$LOG_FILE")
echo "📊 TOTAL COMMENTS PROCESSED: $TOTAL"
echo ""

# By category
echo "📈 BREAKDOWN BY CATEGORY:"
echo "─────────────────────────────────────────────────────────────"
if command -v jq &> /dev/null; then
    QUESTIONS=$(jq '[.[] | select(.category == "questions")] | length' "$LOG_FILE" 2>/dev/null || echo "?")
    PRAISE=$(jq '[.[] | select(.category == "praise")] | length' "$LOG_FILE" 2>/dev/null || echo "?")
    SPAM=$(jq '[.[] | select(.category == "spam")] | length' "$LOG_FILE" 2>/dev/null || echo "?")
    SALES=$(jq '[.[] | select(.category == "sales")] | length' "$LOG_FILE" 2>/dev/null || echo "?")
    
    echo "Questions:         $QUESTIONS"
    echo "Praise:            $PRAISE"
    echo "Spam:              $SPAM"
    echo "Sales/Partners:    $SALES"
else
    echo "Questions:         $(grep -c '"category":"questions"' "$LOG_FILE")"
    echo "Praise:            $(grep -c '"category":"praise"' "$LOG_FILE")"
    echo "Spam:              $(grep -c '"category":"spam"' "$LOG_FILE")"
    echo "Sales:             $(grep -c '"category":"sales"' "$LOG_FILE")"
fi
echo ""

# Response status
echo "📝 RESPONSE STATUS:"
echo "─────────────────────────────────────────────────────────────"
if command -v jq &> /dev/null; then
    AUTO=$(jq '[.[] | select(.response_status == "auto_responded")] | length' "$LOG_FILE" 2>/dev/null || echo "?")
    FLAGGED=$(jq '[.[] | select(.response_status == "flagged")] | length' "$LOG_FILE" 2>/dev/null || echo "?")
    LOGGED=$(jq '[.[] | select(.response_status == "logged")] | length' "$LOG_FILE" 2>/dev/null || echo "?")
    
    echo "Auto-responded:    $AUTO"
    echo "Flagged for review: $FLAGGED"
    echo "Logged only:       $LOGGED"
else
    echo "Auto-responded:    $(grep -c '"response_status":"auto_responded"' "$LOG_FILE")"
    echo "Flagged for review: $(grep -c '"response_status":"flagged"' "$LOG_FILE")"
    echo "Logged only:       $(grep -c '"response_status":"logged"' "$LOG_FILE")"
fi
echo ""

# Top commenters
echo "👥 TOP COMMENTERS:"
echo "─────────────────────────────────────────────────────────────"
if command -v jq &> /dev/null; then
    jq -r '.commenter // .author' "$LOG_FILE" 2>/dev/null | sort | uniq -c | sort -rn | head -5 | awk '{print $2, "(" $1 ")"}'
else
    grep -o '"commenter":"[^"]*"' "$LOG_FILE" | cut -d'"' -f4 | sort | uniq -c | sort -rn | head -5
fi
echo ""

# Flagged items (needs review)
echo "🚩 FLAGGED FOR REVIEW (Needs your attention):"
echo "─────────────────────────────────────────────────────────────"
if command -v jq &> /dev/null; then
    jq -r 'select(.response_status == "flagged") | "\(.commenter // .author): \(.text)"' "$LOG_FILE" 2>/dev/null | head -5
else
    echo "Use jq for detailed flagged item analysis:"
    echo "  jq 'select(.response_status == \"flagged\")' $LOG_FILE"
fi
echo ""

echo "════════════════════════════════════════════════════════════"
echo "For detailed analysis, use:"
echo "  cat $LOG_FILE | jq ."
echo "  jq 'select(.category == \"questions\")' $LOG_FILE"
echo "  jq 'select(.response_status == \"flagged\")' $LOG_FILE"
echo "════════════════════════════════════════════════════════════"
