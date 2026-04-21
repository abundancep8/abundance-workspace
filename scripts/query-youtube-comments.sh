#!/bin/bash
# Query and analyze YouTube comments log

LOGFILE=".cache/youtube-comments.jsonl"

if [ ! -f "$LOGFILE" ]; then
    echo "Log file not found: $LOGFILE"
    exit 1
fi

case "${1:-stats}" in
    stats)
        echo "=== OVERALL STATISTICS ==="
        echo "Total comments: $(wc -l < $LOGFILE)"
        echo ""
        echo "By category:"
        cat "$LOGFILE" | jq -r '.category' | sort | uniq -c | sort -rn
        echo ""
        echo "By response status:"
        cat "$LOGFILE" | jq -r '.response_status' | sort | uniq -c | sort -rn
        ;;
    
    recent)
        COUNT=${2:-10}
        echo "=== LAST $COUNT COMMENTS ==="
        tail -$COUNT "$LOGFILE" | jq '{commenter, category, response_status, text: (.text | .[0:60])}'
        ;;
    
    questions)
        echo "=== UNANSWERED QUESTIONS ==="
        cat "$LOGFILE" | jq -s 'map(select(.category=="questions" and .response_status!="auto_responded"))' | jq -r '.[] | "\(.commenter): \(.text)"'
        ;;
    
    flagged)
        echo "=== FLAGGED FOR REVIEW ==="
        cat "$LOGFILE" | jq -s 'map(select(.response_status=="flagged"))' | jq -r '.[] | "\(.commenter): \(.text)"'
        ;;
    
    spam)
        echo "=== SPAM COMMENTS ==="
        cat "$LOGFILE" | jq -s 'map(select(.category=="spam"))' | jq '.[] | {commenter, text: (.text | .[0:80])}'
        ;;
    
    authors)
        echo "=== TOP COMMENTERS ==="
        cat "$LOGFILE" | jq -r '.commenter' | sort | uniq -c | sort -rn | head -20
        ;;
    
    search)
        QUERY="${2:-}"
        if [ -z "$QUERY" ]; then
            echo "Usage: $0 search <query>"
            exit 1
        fi
        echo "=== COMMENTS MATCHING: $QUERY ==="
        cat "$LOGFILE" | jq "select(.text | test(\"$QUERY\"; \"i\")) | {commenter, category, text}"
        ;;
    
    export)
        FORMAT=${2:-csv}
        case "$FORMAT" in
            csv)
                echo "timestamp,commenter,category,response_status,text"
                cat "$LOGFILE" | jq -r '[.timestamp, .commenter, .category, .response_status, .text] | @csv'
                ;;
            json)
                cat "$LOGFILE" | jq -s '.'
                ;;
            *)
                echo "Unknown format: $FORMAT"
                exit 1
                ;;
        esac
        ;;
    
    *)
        echo "Usage: $0 {stats|recent [N]|questions|flagged|spam|authors|search <query>|export [csv|json]}"
        echo ""
        echo "Examples:"
        echo "  $0 stats           # Show overall statistics"
        echo "  $0 recent 20       # Show last 20 comments"
        echo "  $0 flagged         # Show all flagged comments"
        echo "  $0 search 'how'    # Search for comments containing 'how'"
        echo "  $0 export csv      # Export as CSV"
        ;;
esac
