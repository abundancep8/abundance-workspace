#!/bin/bash
# Claude API Usage Monitor - Cron Wrapper
# Run this via cron to fetch and monitor Anthropic API usage
# Usage: ./claude-usage-monitor-cron.sh
# Or add to crontab: 0 * * * * /path/to/claude-usage-monitor-cron.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$SCRIPT_DIR/claude-usage-monitor.log"
PYTHON_SCRIPT="$SCRIPT_DIR/fetch-claude-usage-complete.py"

# Color codes for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log_stdout() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    log "$1"
}

# Ensure Python is available
if ! command -v python3 &> /dev/null; then
    log "ERROR: python3 not found"
    exit 1
fi

log_stdout "Starting Claude API usage monitor..."

# Run the Python script
if python3 "$PYTHON_SCRIPT"; then
    log_stdout "✓ Usage fetch completed successfully"
    
    # Parse the result
    if [ -f "$SCRIPT_DIR/claude-usage.json" ]; then
        status=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/claude-usage.json')).get('status', 'unknown'))")
        cost_today=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/claude-usage.json')).get('cost_today', 'N/A'))")
        cost_month=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/claude-usage.json')).get('cost_month', 'N/A'))")
        
        log_stdout "  Status: $status"
        log_stdout "  Cost Today: \$$cost_today"
        log_stdout "  Cost Month: \$$cost_month"
        
        # Check if alert was triggered
        alert=$(python3 -c "import json; print(json.load(open('$SCRIPT_DIR/claude-usage.json')).get('alert', False))")
        if [ "$alert" = "True" ]; then
            log_stdout "⚠️  ALERT: Usage threshold exceeded!"
        fi
    fi
else
    log "ERROR: Python script failed"
    exit 1
fi

log_stdout "Monitor completed at $(date '+%Y-%m-%d %H:%M:%S')"
