#!/bin/bash
#
# YouTube DM Monitor - Setup & Installation Script
# Installs the cron job and configures launchd for periodic execution
#
# Usage:
#   ./setup-youtube-dm-cron.sh install     # Install cron job
#   ./setup-youtube-dm-cron.sh uninstall   # Remove cron job
#   ./setup-youtube-dm-cron.sh status      # Check status
#   ./setup-youtube-dm-cron.sh test        # Run a test execution
#

set -euo pipefail

# Configuration
WORKSPACE_DIR="/Users/abundance/.openclaw/workspace"
SCRIPT_DIR="$WORKSPACE_DIR"
SCRIPT_NAME="youtube-dm-monitor-cron.sh"
SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_NAME"
PLIST_NAME="com.concessa.youtube-dm-monitor"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
LAUNCHD_ENABLED=false
CRON_ENABLED=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found. Please install Python 3."
        exit 1
    fi
    print_success "Python 3 found: $(python3 --version)"
    
    # Check workspace directory
    if [ ! -d "$WORKSPACE_DIR" ]; then
        print_error "Workspace directory not found: $WORKSPACE_DIR"
        exit 1
    fi
    print_success "Workspace directory: $WORKSPACE_DIR"
    
    # Check script file
    if [ ! -f "$SCRIPT_PATH" ]; then
        print_error "Script not found: $SCRIPT_PATH"
        exit 1
    fi
    print_success "Script file: $SCRIPT_PATH"
    
    # Make script executable
    chmod +x "$SCRIPT_PATH"
    print_success "Script is executable"
}

# Create launchd plist
create_launchd_plist() {
    print_header "Creating launchd Configuration"
    
    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "$HOME/Library/LaunchAgents"
    
    # Create plist file
    cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_NAME</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$SCRIPT_PATH</string>
    </array>
    
    <key>StartInterval</key>
    <integer>3600</integer>
    
    <key>StandardOutPath</key>
    <string>$WORKSPACE_DIR/.cache/youtube-dm-monitor.out</string>
    
    <key>StandardErrorPath</key>
    <string>$WORKSPACE_DIR/.cache/youtube-dm-monitor.err</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF
    
    print_success "launchd plist created: $PLIST_PATH"
}

# Install the cron job
install_cron() {
    print_header "Installing Cron Job"
    
    # Check if crontab exists
    if crontab -l &> /dev/null; then
        # Crontab exists, check if our job is already there
        if crontab -l | grep -F "$SCRIPT_PATH" &> /dev/null; then
            print_warning "Cron job already installed"
            return 0
        fi
    fi
    
    # Add new cron job (every hour at :00)
    (
        crontab -l 2>/dev/null || echo ""
        echo "# YouTube DM Monitor - Concessa Obvius"
        echo "0 * * * * $SCRIPT_PATH >> $WORKSPACE_DIR/.cache/youtube-dm-monitor.cron.log 2>&1"
    ) | crontab -
    
    print_success "Cron job installed (every hour)"
}

# Install launchd job
install_launchd() {
    print_header "Installing launchd Job (macOS)"
    
    create_launchd_plist
    
    # Load the plist
    launchctl load "$PLIST_PATH"
    
    print_success "launchd job loaded"
}

# Install all (try both methods)
install_all() {
    print_header "YouTube DM Monitor - Setup & Installation"
    
    check_prerequisites
    
    echo ""
    print_info "Choose installation method:"
    echo ""
    echo "1) launchd (recommended for macOS)"
    echo "2) crontab"
    echo "3) Both"
    echo "4) Cancel"
    echo ""
    read -p "Select option [1-4]: " choice
    
    case $choice in
        1)
            install_launchd
            LAUNCHD_ENABLED=true
            ;;
        2)
            install_cron
            CRON_ENABLED=true
            ;;
        3)
            install_launchd
            LAUNCHD_ENABLED=true
            echo ""
            install_cron
            CRON_ENABLED=true
            ;;
        4)
            print_warning "Installation cancelled"
            exit 0
            ;;
        *)
            print_error "Invalid option"
            exit 1
            ;;
    esac
    
    echo ""
    print_header "Installation Complete ✓"
    
    if [ "$LAUNCHD_ENABLED" = true ]; then
        echo ""
        print_info "launchd Status:"
        launchctl list | grep "$PLIST_NAME" || print_warning "Not yet active (will start next cycle)"
    fi
    
    if [ "$CRON_ENABLED" = true ]; then
        echo ""
        print_info "Cron Job:"
        crontab -l | grep "$SCRIPT_PATH" || print_warning "Job entry not found"
    fi
    
    echo ""
    print_success "Setup complete!"
}

# Uninstall
uninstall_all() {
    print_header "Uninstalling YouTube DM Monitor"
    
    # Unload launchd
    if [ -f "$PLIST_PATH" ]; then
        launchctl unload "$PLIST_PATH" 2>/dev/null || true
        rm "$PLIST_PATH"
        print_success "launchd job removed"
    fi
    
    # Remove from crontab
    if crontab -l 2>/dev/null | grep -F "$SCRIPT_PATH" &> /dev/null; then
        (
            crontab -l | grep -v "$SCRIPT_PATH"
        ) | crontab -
        print_success "Cron job removed"
    fi
    
    echo ""
    print_success "Uninstalled successfully"
}

# Show status
show_status() {
    print_header "Status - YouTube DM Monitor"
    
    echo ""
    print_info "Workspace: $WORKSPACE_DIR"
    print_info "Script: $SCRIPT_PATH"
    
    echo ""
    print_info "launchd Status:"
    if [ -f "$PLIST_PATH" ]; then
        print_success "plist installed at $PLIST_PATH"
        launchctl list | grep "$PLIST_NAME" && echo "  Running: YES" || echo "  Running: NO"
    else
        print_warning "plist not found"
    fi
    
    echo ""
    print_info "Cron Status:"
    if crontab -l 2>/dev/null | grep -F "$SCRIPT_PATH" &> /dev/null; then
        print_success "Cron job installed"
        crontab -l | grep "$SCRIPT_PATH" | sed 's/^/  /'
    else
        print_warning "No cron job found"
    fi
    
    echo ""
    print_info "Recent Logs:"
    if [ -f "$WORKSPACE_DIR/.cache/youtube-dm-monitor.log" ]; then
        tail -n 5 "$WORKSPACE_DIR/.cache/youtube-dm-monitor.log" | sed 's/^/  /'
    else
        print_warning "No logs found yet"
    fi
}

# Test run
test_run() {
    print_header "Running Test Execution"
    
    echo ""
    print_info "Executing: $SCRIPT_PATH"
    echo ""
    
    if bash "$SCRIPT_PATH"; then
        echo ""
        print_success "Test execution completed successfully"
    else
        echo ""
        print_error "Test execution failed"
        exit 1
    fi
}

# Main
main() {
    case "${1:-help}" in
        install)
            install_all
            ;;
        uninstall)
            uninstall_all
            ;;
        status)
            show_status
            ;;
        test)
            test_run
            ;;
        *)
            echo ""
            echo "YouTube DM Monitor - Setup & Installation Script"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  install      Install the cron/launchd job"
            echo "  uninstall    Remove the cron/launchd job"
            echo "  status       Show installation status"
            echo "  test         Run a test execution"
            echo "  help         Show this help message"
            echo ""
            ;;
    esac
}

main "$@"
