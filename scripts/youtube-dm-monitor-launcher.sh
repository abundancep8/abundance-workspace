#!/bin/bash
# YouTube DM Monitor - Cron launcher wrapper
# This script sets up environment and runs the Python monitor

set -e

WORKSPACE="${HOME}/.openclaw/workspace"
SCRIPT="${WORKSPACE}/scripts/youtube-dm-monitor.py"
CACHE_DIR="${WORKSPACE}/.cache"
LOG_FILE="${CACHE_DIR}/youtube-dm-monitor.log"

# Create cache directory
mkdir -p "${CACHE_DIR}"

# Log execution
{
    echo "=== YouTube DM Monitor Run ==="
    echo "Time: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
    echo ""
    
    # Run the Python script
    python3 "${SCRIPT}"
    
    echo ""
    echo "Status: Success"
} >> "${LOG_FILE}" 2>&1

exit 0
