#!/bin/bash
#
# YouTube DM Monitor - Cron Wrapper
# Executes the Python monitor in a controlled environment with proper error handling
#

set -euo pipefail

# Configuration
WORKSPACE_DIR="/Users/abundance/.openclaw/workspace"
SCRIPT_DIR="$WORKSPACE_DIR"
SCRIPT_NAME="youtube-dm-monitor-cron.py"
SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_NAME"

# Ensure workspace exists
if [ ! -d "$WORKSPACE_DIR" ]; then
    echo "[ERROR] Workspace not found: $WORKSPACE_DIR"
    exit 1
fi

# Ensure Python script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "[ERROR] Script not found: $SCRIPT_PATH"
    exit 1
fi

# Change to workspace directory
cd "$WORKSPACE_DIR"

# Execute Python script
python3 "$SCRIPT_PATH"
exit_code=$?

# Return exit code to cron
exit $exit_code
