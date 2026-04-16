#!/bin/bash

# CRON RUNNER SCRIPT
# Kimi K2.5 Integration - Task Router
# Execute via cron: */5 * * * * /usr/local/bin/cron-runner.sh

set -e

INTEGRATION_DIR="/Users/abundance/.openclaw/workspace/kimi-integration"
LOG_DIR="${INTEGRATION_DIR}/logs"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

# Export API key
export OPENROUTER_API_KEY="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"

# Log function
log() {
    echo "[${TIMESTAMP}] $1" >> "${LOG_DIR}/cron.log"
}

# Run the router
log "Starting Kimi router job..."

cd "${INTEGRATION_DIR}" || exit 1

# Generate performance report
log "Generating performance report..."
node router.js report > "${LOG_DIR}/latest-report.json" 2>&1 || log "Report generation had issues (non-critical)"

# Check for any pending tasks (placeholder for future integration)
# In production, this would:
# 1. Check for queued tasks in a database/queue
# 2. Route each task to Kimi or Claude
# 3. Log results to performance.jsonl
# 4. Update dashboard

log "Router job completed successfully"
exit 0
