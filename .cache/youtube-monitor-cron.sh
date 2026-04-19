#!/bin/bash
# Cron wrapper for YouTube comment monitor
# Runs every 30 minutes

set -e

WORKSPACE="/Users/abundance/.openclaw/workspace"
LOG_DIR="${WORKSPACE}/.cache"
SCRIPT="${LOG_DIR}/youtube-monitor.py"
CRON_LOG="${LOG_DIR}/youtube-monitor-cron.log"

# Ensure directories exist
mkdir -p "${LOG_DIR}"

# Run with timestamp
{
    echo "=========================================="
    echo "Run: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=========================================="
    cd "${WORKSPACE}"
    python3 "${SCRIPT}" 2>&1 || echo "ERROR: Monitor script failed with exit code $?"
    echo ""
} >> "${CRON_LOG}"

# Keep log rotation - last 50 runs
if [ -f "${CRON_LOG}" ]; then
    tail -n 2000 "${CRON_LOG}" > "${CRON_LOG}.tmp"
    mv "${CRON_LOG}.tmp" "${CRON_LOG}"
fi
