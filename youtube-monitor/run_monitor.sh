#!/bin/bash
###############################################################################
# YouTube Comment Monitor - Cron Wrapper
#
# This script is designed to be run from cron every 30 minutes.
# It sets up the environment and executes the monitor.
#
# Usage:
#   chmod +x run_monitor.sh
#   ./run_monitor.sh
#   
# Add to crontab:
#   */30 * * * * /path/to/youtube-monitor/run_monitor.sh
#
# Configuration:
#   Edit the variables below, or set them via environment variables
#
###############################################################################

set -e  # Exit on any error

# ============================================================================
# CONFIGURATION
# ============================================================================

# YouTube API key (required)
# Can also be set via YOUTUBE_API_KEY environment variable
if [ -z "$YOUTUBE_API_KEY" ]; then
    echo "ERROR: YOUTUBE_API_KEY not set. Exiting."
    exit 1
fi

# YouTube Channel ID (optional, defaults to Concessa Obvius)
YOUTUBE_CHANNEL_ID="${YOUTUBE_CHANNEL_ID:-UCXXz-s8LjQGpAK-PEzMXbqg}"

# Python executable (use full path for cron)
PYTHON="${PYTHON:-/usr/bin/python3}"

# Script directory (auto-detected)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Log file
LOG_FILE="$SCRIPT_DIR/.cache/cron.log"

# ============================================================================
# FUNCTIONS
# ============================================================================

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
}

# ============================================================================
# EXECUTION
# ============================================================================

# Ensure cache directory exists
mkdir -p "$SCRIPT_DIR/.cache"

log "YouTube Comment Monitor starting"

# Verify Python exists
if ! command -v "$PYTHON" &> /dev/null; then
    error "Python not found at $PYTHON"
    exit 1
fi

# Verify script exists
if [ ! -f "$SCRIPT_DIR/youtube_comment_monitor.py" ]; then
    error "Script not found at $SCRIPT_DIR/youtube_comment_monitor.py"
    exit 1
fi

# Run the monitor
cd "$SCRIPT_DIR"

if "$PYTHON" youtube_comment_monitor.py 2>&1 | tee -a "$LOG_FILE"; then
    log "Completed successfully"
    exit 0
else
    EXIT_CODE=$?
    error "Failed with exit code $EXIT_CODE"
    
    # Optional: Send email notification on failure
    # Uncomment and edit to enable:
    # {
    #   echo "YouTube Comment Monitor failed on $(hostname)"
    #   echo "Exit code: $EXIT_CODE"
    #   echo ""
    #   echo "Log tail:"
    #   tail -20 "$LOG_FILE"
    # } | mail -s "YouTube Monitor Error" admin@example.com
    
    exit $EXIT_CODE
fi
