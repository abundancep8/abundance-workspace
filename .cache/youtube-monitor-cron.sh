#!/bin/bash
# YouTube Comment Monitor - Cron job runner
# Runs every 30 minutes to monitor Concessa Obvius channel

set -e

WORKSPACE="$HOME/.openclaw/workspace"
CACHE_DIR="$WORKSPACE/.cache"
MONITOR_SCRIPT="$CACHE_DIR/youtube-monitor.py"
LOG_FILE="$CACHE_DIR/youtube-monitor-cron.log"
REPORT_FILE="$CACHE_DIR/youtube-comments-report.txt"

# Ensure cache directory exists
mkdir -p "$CACHE_DIR"

# Run timestamp
RUN_TIME=$(date '+%Y-%m-%d %H:%M:%S UTC')
echo "=== YouTube Comment Monitor Run ===" >> "$LOG_FILE"
echo "Timestamp: $RUN_TIME" >> "$LOG_FILE"

# Run monitor
cd "$CACHE_DIR"
if [ -f "$MONITOR_SCRIPT" ]; then
    python3 "$MONITOR_SCRIPT" >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?
    echo "Exit Code: $EXIT_CODE" >> "$LOG_FILE"
else
    echo "ERROR: Monitor script not found at $MONITOR_SCRIPT" >> "$LOG_FILE"
    exit 1
fi

# Generate report
generate_report() {
    local total_new=0
    local auto_responses=0
    local flagged=0
    local questions=0
    local praise=0
    local spam=0
    local sales=0
    
    # Parse last run stats from log
    if [ -f "$CACHE_DIR/youtube-comments.jsonl" ]; then
        total_new=$(grep -c '"response_status"' "$CACHE_DIR/youtube-comments.jsonl" || echo "0")
        auto_responses=$(grep -c '"auto_replied": true' "$CACHE_DIR/youtube-comments.jsonl" || echo "0")
        flagged=$(grep -c '"sales"' "$CACHE_DIR/youtube-comments.jsonl" || echo "0")
        questions=$(grep -c '"questions"' "$CACHE_DIR/youtube-comments.jsonl" || echo "0")
        praise=$(grep -c '"praise"' "$CACHE_DIR/youtube-comments.jsonl" || echo "0")
        spam=$(grep -c '"spam"' "$CACHE_DIR/youtube-comments.jsonl" || echo "0")
        sales=$(grep -c '"sales"' "$CACHE_DIR/youtube-comments.jsonl" || echo "0")
    fi
    
    cat > "$REPORT_FILE" << EOF
📊 YouTube Comment Monitor Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Timestamp: $RUN_TIME
Channel: Concessa Obvius

📈 Statistics:
  Total comments in log: $total_new
  Auto-responses sent: $auto_responses
  Flagged for review: $flagged

📂 Categories:
  Questions: $questions
  Praise: $praise
  Spam: $spam
  Sales: $sales

✅ Status: Monitor running every 30 minutes
EOF
    echo "Report updated: $REPORT_FILE" >> "$LOG_FILE"
}

generate_report

echo "Run completed successfully" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
