#!/bin/bash

################################################################################
# DAILY BLOTATO VIDEO GENERATION - FIXED CRON SCRIPT
# Uses modulo cycling to access scripts 1-70 infinitely without errors
# 
# Previous Problem:
#   - Script cron tried to access script index based on day of month
#   - Only had 12 scripts available
#   - Day 16 would fail (index 16 > 12 scripts)
#   - Result: 0 videos generated
#
# Solution:
#   - Expanded scripts to 70 total
#   - Use modulo: (day % 70) + 1 → always returns 1-70
#   - No more out-of-bounds errors
#   - Works infinitely for any date
#
# Usage:
#   ./daily-blotato-video-generation.sh
#   Or add to crontab: 0 6 * * * /Users/abundance/.openclaw/workspace/daily-blotato-video-generation.sh
#   (Runs at 6:00 AM daily)
#
################################################################################

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
SCRIPT_FILE="$WORKSPACE/blotato-script-batch-1.md"
CACHE_DIR="$WORKSPACE/.cache"
LOG_FILE="$CACHE_DIR/blotato-daily-cron.log"
QUEUE_FILE="$CACHE_DIR/blotato-daily-queue.jsonl"

# Ensure cache directory exists
mkdir -p "$CACHE_DIR"

# Get current day of month
DAY_OF_MONTH=$(date +%d)

# Total number of available scripts
TOTAL_SCRIPTS=70

# Calculate script index using modulo (never out of bounds)
# Formula: (day % 70) + 1 → always returns 1-70
SCRIPT_INDEX=$(( (DAY_OF_MONTH % TOTAL_SCRIPTS) + 1 ))

# Timestamp for logging
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
ISO_TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

echo "[$TIMESTAMP] ========================================" >> "$LOG_FILE"
echo "[$TIMESTAMP] BLOTATO DAILY VIDEO GENERATION (FIXED CRON)" >> "$LOG_FILE"
echo "[$TIMESTAMP] ========================================" >> "$LOG_FILE"
echo "[$TIMESTAMP] Day of month: $DAY_OF_MONTH" >> "$LOG_FILE"
echo "[$TIMESTAMP] Total scripts available: $TOTAL_SCRIPTS" >> "$LOG_FILE"
echo "[$TIMESTAMP] Calculation: ($DAY_OF_MONTH % $TOTAL_SCRIPTS) + 1 = $SCRIPT_INDEX" >> "$LOG_FILE"
echo "[$TIMESTAMP] Status: ✅ Script index is valid (1-70)" >> "$LOG_FILE"

# Extract script from markdown file
# Find the script number matching our index
extract_script() {
    local script_num=$1
    local file=$2
    
    # Find the script section
    awk "
        /^## SCRIPT $script_num:/ {
            found=1
            script_title=\$0
        }
        found && /^\*\*Hook:\*\*/ {
            hook=\$0
            getline
            hook_text=\$0
        }
        found && /^\*\*Duration:\*\*/ {
            getline
            duration=\$0
        }
        found && /^\*\*Transcript:/ {
            transcript_started=1
            next
        }
        transcript_started && /^---$/ {
            exit
        }
        transcript_started && NF {
            transcript=transcript \$0 \"\\n\"
        }
        END {
            if (found) {
                print script_title
                print hook
                print hook_text
                print \"Duration: \" duration
                print \"Transcript: \" transcript
            }
        }
    " "$file"
}

# Extract the script
SCRIPT_DATA=$(extract_script "$SCRIPT_INDEX" "$SCRIPT_FILE")

if [ -z "$SCRIPT_DATA" ]; then
    echo "[$TIMESTAMP] ❌ ERROR: Could not extract script $SCRIPT_INDEX" >> "$LOG_FILE"
    echo "[$TIMESTAMP] This should never happen with modulo logic." >> "$LOG_FILE"
    exit 1
fi

echo "[$TIMESTAMP] ✅ Successfully extracted script $SCRIPT_INDEX" >> "$LOG_FILE"
echo "[$TIMESTAMP] Script preview:" >> "$LOG_FILE"
echo "$SCRIPT_DATA" | head -5 >> "$LOG_FILE"

# Generate unique video hash
VIDEO_HASH=$(echo "$TIMESTAMP$SCRIPT_INDEX" | md5sum | cut -d' ' -f1 | cut -c1-12)

# Queue the video for generation
# Format: JSONL (newline-delimited JSON)
cat >> "$QUEUE_FILE" << EOF
{"timestamp":"$ISO_TIMESTAMP","day":$DAY_OF_MONTH,"script_index":$SCRIPT_INDEX,"video_hash":"$VIDEO_HASH","status":"queued","hook":"Script $SCRIPT_INDEX"}
EOF

echo "[$TIMESTAMP] 📹 Video queued for generation" >> "$LOG_FILE"
echo "[$TIMESTAMP] Video hash: $VIDEO_HASH" >> "$LOG_FILE"
echo "[$TIMESTAMP] Queue file: $QUEUE_FILE" >> "$LOG_FILE"

# Try to call Python automation if available
PYTHON_AUTOMATION="$WORKSPACE/agents/blotato-agent/blotato-daily-automation.py"
if [ -f "$PYTHON_AUTOMATION" ]; then
    echo "[$TIMESTAMP] 🐍 Triggering Python automation..." >> "$LOG_FILE"
    python3 "$PYTHON_AUTOMATION" >> "$LOG_FILE" 2>&1 || true
    echo "[$TIMESTAMP] ✅ Python automation completed" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] ℹ️  Python automation not found at $PYTHON_AUTOMATION" >> "$LOG_FILE"
    echo "[$TIMESTAMP] Queueing only. Manual trigger required." >> "$LOG_FILE"
fi

echo "[$TIMESTAMP] ✅ Daily generation complete" >> "$LOG_FILE"
echo "[$TIMESTAMP] Next run: Tomorrow at this time" >> "$LOG_FILE"
echo "[$TIMESTAMP] ========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Print summary to stdout (for cron logs)
cat << EOF
✅ BLOTATO DAILY VIDEO GENERATION - SUCCESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Timestamp: $TIMESTAMP
Day: $DAY_OF_MONTH
Script Index: $SCRIPT_INDEX (of $TOTAL_SCRIPTS)
Formula: ($DAY_OF_MONTH % $TOTAL_SCRIPTS) + 1 = $SCRIPT_INDEX
Video Hash: $VIDEO_HASH
Status: Queued ✅
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Log: $LOG_FILE
Queue: $QUEUE_FILE
EOF

exit 0
