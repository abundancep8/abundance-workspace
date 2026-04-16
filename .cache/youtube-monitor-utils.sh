#!/bin/bash
# YouTube Monitor Utilities - Query and manage logs

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
LOG_FILE="$WORKSPACE/.cache/youtube-comments.jsonl"
STATE_FILE="$WORKSPACE/.cache/youtube-monitor-state.json"

# Color codes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

show_help() {
    cat << EOF
${BLUE}YouTube Monitor Utilities${NC}

Usage: $0 [command] [options]

Commands:
  ${GREEN}status${NC}              Show monitor status and stats
  ${GREEN}recent${NC} [n=10]       Show last n comments
  ${GREEN}category${NC} [type]    Show comments by category (questions|praise|spam|sales|other)
  ${GREEN}flagged${NC}             Show all flagged for review items
  ${GREEN}auto-responses${NC}      Show queued auto-response comments
  ${GREEN}spam${NC}                Show spam comments
  ${GREEN}by-user${NC} [name]      Show comments from specific user
  ${GREEN}search${NC} [text]      Search comment text
  ${GREEN}export${NC} [format]    Export logs (json|csv)
  ${GREEN}stats${NC}               Show detailed statistics
  ${GREEN}reset${NC}               Reset state (caution!)
  ${GREEN}help${NC}                Show this message

Examples:
  $0 status
  $0 recent 20
  $0 category questions
  $0 flagged
  $0 search "partnership"
  $0 export csv
  $0 stats

EOF
}

check_files() {
    if [ ! -f "$LOG_FILE" ]; then
        echo -e "${YELLOW}No log file found. Run monitor first.${NC}"
        exit 1
    fi
}

show_status() {
    echo -e "${BLUE}=== YouTube Monitor Status ===${NC}\n"
    
    if [ -f "$STATE_FILE" ]; then
        echo -e "${GREEN}State:${NC}"
        jq . "$STATE_FILE" | sed 's/^/  /'
        echo
    fi
    
    echo -e "${GREEN}Log File:${NC}"
    if [ -f "$LOG_FILE" ]; then
        TOTAL_LINES=$(wc -l < "$LOG_FILE")
        echo "  Total comments logged: $TOTAL_LINES"
        echo "  File size: $(du -h "$LOG_FILE" | cut -f1)"
    else
        echo "  No log file yet"
    fi
    echo
    
    echo -e "${GREEN}Run Log:${NC}"
    if [ -f "$WORKSPACE/.cache/youtube-monitor.log" ]; then
        echo "  Latest entries:"
        tail -3 "$WORKSPACE/.cache/youtube-monitor.log" | sed 's/^/    /'
    else
        echo "  No run log yet"
    fi
}

show_recent() {
    local n=${1:-10}
    check_files
    
    echo -e "${BLUE}=== Last $n Comments ===${NC}\n"
    
    tail -n $n "$LOG_FILE" | jq '
        {
            time: .timestamp,
            author: .commenter,
            category: .category,
            status: .response_status,
            text: .text,
            likes: .likes
        }
    ' | column -t
}

show_category() {
    local category=$1
    
    if [ -z "$category" ]; then
        echo -e "${RED}Error: Specify category (questions|praise|spam|sales|other)${NC}"
        exit 1
    fi
    
    check_files
    
    echo -e "${BLUE}=== $category Comments ===${NC}\n"
    
    grep "\"category\":\"$category\"" "$LOG_FILE" 2>/dev/null | \
        jq '{author: .commenter, text: .text, likes: .likes, time: .timestamp}' | \
        jq -r '"\(.author): \(.text) (❤️ \(.likes))"'
    
    echo
    local count=$(grep -c "\"category\":\"$category\"" "$LOG_FILE" 2>/dev/null || echo 0)
    echo -e "${GREEN}Total: $count${NC}"
}

show_flagged() {
    check_files
    
    echo -e "${BLUE}=== Flagged for Review (Sales Inquiries) ===${NC}\n"
    
    grep "\"response_status\":\"flagged_for_review\"" "$LOG_FILE" 2>/dev/null | \
        jq '{
            author: .commenter,
            text: .text,
            time: .timestamp,
            id: .comment_id
        }' | \
        jq -r '"[\(.time | .[0:10])] \(.author):\n  \(.text)\n  ID: \(.id)\n"' || echo "No flagged items"
}

show_auto_responses() {
    check_files
    
    echo -e "${BLUE}=== Queued Auto-Responses ===${NC}\n"
    
    grep "\"response_status\":\"auto_response_queued\"" "$LOG_FILE" 2>/dev/null | \
        jq '{
            category: .category,
            author: .commenter,
            text: .text,
            time: .timestamp
        }' | \
        jq -r '"[\(.category | ascii_upcase)] \(.author): \(.text)"' || echo "No queued responses"
}

show_spam() {
    check_files
    
    echo -e "${BLUE}=== Spam Comments ===${NC}\n"
    
    grep "\"category\":\"spam\"" "$LOG_FILE" 2>/dev/null | \
        jq '{author: .commenter, text: .text}' | \
        jq -r '"\(.author): \(.text)"' || echo "No spam detected"
    
    echo
    local count=$(grep -c "\"category\":\"spam\"" "$LOG_FILE" 2>/dev/null || echo 0)
    echo -e "${GREEN}Total: $count${NC}"
}

show_by_user() {
    local user=$1
    
    if [ -z "$user" ]; then
        echo -e "${RED}Error: Specify username${NC}"
        exit 1
    fi
    
    check_files
    
    echo -e "${BLUE}=== Comments from \"$user\" ===${NC}\n"
    
    grep "\"commenter\":\"$user\"" "$LOG_FILE" 2>/dev/null | \
        jq '{category: .category, text: .text, time: .timestamp}' | \
        jq -r '"[\(.category | ascii_upcase)] \(.time | .[0:10]): \(.text)"' || \
        echo "No comments from that user"
}

search_comments() {
    local query=$1
    
    if [ -z "$query" ]; then
        echo -e "${RED}Error: Specify search text${NC}"
        exit 1
    fi
    
    check_files
    
    echo -e "${BLUE}=== Search Results for \"$query\" ===${NC}\n"
    
    grep -i "$query" "$LOG_FILE" 2>/dev/null | \
        jq '{author: .commenter, category: .category, text: .text}' | \
        jq -r '"\(.author) [\(.category)]: \(.text)"' || \
        echo "No matches found"
}

export_logs() {
    local format=$1
    check_files
    
    if [ -z "$format" ]; then
        format="json"
    fi
    
    local outfile="youtube-comments-export.${format}"
    
    case "$format" in
        json)
            jq -s '.' "$LOG_FILE" > "$outfile"
            ;;
        csv)
            echo "timestamp,author,category,response_status,text,likes" > "$outfile"
            jq -r '[.timestamp, .commenter, .category, .response_status, .text, .likes] | @csv' "$LOG_FILE" >> "$outfile"
            ;;
        *)
            echo -e "${RED}Unsupported format: $format${NC}"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}✓ Exported to $outfile${NC}"
}

show_stats() {
    check_files
    
    echo -e "${BLUE}=== Detailed Statistics ===${NC}\n"
    
    echo -e "${GREEN}By Category:${NC}"
    jq '[.category] | group_by(.) | map({category: .[0], count: length})' \
        <(grep '.' "$LOG_FILE") | jq '.[] | "\(.category): \(.count)"'
    
    echo
    echo -e "${GREEN}By Response Status:${NC}"
    jq '[.response_status] | group_by(.) | map({status: .[0], count: length})' \
        <(grep '.' "$LOG_FILE") | jq '.[] | "\(.status): \(.count)"'
    
    echo
    echo -e "${GREEN}Top Commenters:${NC}"
    jq '[.commenter] | group_by(.) | map({author: .[0], comments: length}) | sort_by(-.comments) | .[0:5]' \
        <(grep '.' "$LOG_FILE") | jq '.[] | "\(.author): \(.comments)"'
}

reset_state() {
    echo -e "${YELLOW}⚠ This will reset monitoring state${NC}"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$STATE_FILE"
        echo -e "${GREEN}✓ State reset${NC}"
    else
        echo "Cancelled"
    fi
}

# Main
case "${1:-help}" in
    status)
        show_status
        ;;
    recent)
        show_recent "$2"
        ;;
    category)
        show_category "$2"
        ;;
    flagged)
        show_flagged
        ;;
    auto-responses)
        show_auto_responses
        ;;
    spam)
        show_spam
        ;;
    by-user)
        show_by_user "$2"
        ;;
    search)
        search_comments "$2"
        ;;
    export)
        export_logs "$2"
        ;;
    stats)
        show_stats
        ;;
    reset)
        reset_state
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        show_help
        exit 1
        ;;
esac
