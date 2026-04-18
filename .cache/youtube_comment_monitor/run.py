#!/usr/bin/env python3
"""
YouTube Comment Monitor - Main Entry Point
Run every 30 minutes via cron.

Usage:
    python3 run.py [--config CONFIG_PATH] [--credentials CREDENTIALS_PATH] [--max-results N]
"""

import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from monitor import YouTubeCommentMonitor


def setup_logging(log_dir: Path):
    """Setup comprehensive logging."""
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # File handler
    log_file = log_dir / f"youtube-comment-monitor-{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='YouTube Comment Monitor - Fetches and processes comments'
    )
    parser.add_argument(
        '--config',
        default=os.path.expanduser('~/.openclaw/workspace/.cache/youtube-monitor-config.json'),
        help='Path to config file'
    )
    parser.add_argument(
        '--credentials',
        default=os.path.expanduser('~/.openclaw/workspace/.cache/youtube-credentials.json'),
        help='Path to credentials file'
    )
    parser.add_argument(
        '--workspace',
        default=os.path.expanduser('~/.openclaw/workspace'),
        help='Path to workspace'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=100,
        help='Max comments to fetch per run'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output report filename'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    workspace_path = Path(args.workspace)
    log_dir = workspace_path / '.cache' / 'logs'
    logger = setup_logging(log_dir)
    
    logger.info("=" * 60)
    logger.info("YouTube Comment Monitor Started")
    logger.info("=" * 60)
    
    try:
        # Validate config file
        config_path = Path(args.config)
        if not config_path.exists():
            logger.error(f"Config file not found: {config_path}")
            return 1
        
        # Initialize monitor
        logger.info(f"Loading config from {config_path}")
        monitor = YouTubeCommentMonitor(
            config_path=str(config_path),
            credentials_path=args.credentials,
            workspace_path=args.workspace
        )
        
        # Run monitor
        logger.info(f"Fetching new comments (max: {args.max_results})")
        summary = monitor.run(max_results=args.max_results)
        
        # Save report
        report_file = args.output or 'youtube-comments-report.json'
        report_path = Path(args.workspace) / '.cache' / report_file
        
        with open(report_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Report saved to {report_path}")
        
        # Print summary
        logger.info("=" * 60)
        logger.info("SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Status: {summary.get('status', 'unknown')}")
        logger.info(f"Total Processed: {summary.get('total_processed', 0)}")
        logger.info(f"Auto-responses Sent: {summary.get('auto_responses_sent', 0)}")
        logger.info(f"Flagged for Review: {summary.get('flagged_for_review', 0)}")
        
        if 'errors' in summary and summary['errors']:
            logger.warning(f"Errors: {len(summary['errors'])}")
            for error in summary['errors']:
                logger.warning(f"  - {error}")
        
        logger.info("=" * 60)
        
        # Return 0 on success
        return 0 if summary.get('status') == 'success' else 1
        
    except KeyboardInterrupt:
        logger.info("Monitor interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
