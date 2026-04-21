#!/usr/bin/env python3
"""
YouTube Comment Ingester — Queue comments for processing
Allows manual comment submission for testing and batch processing.

Usage:
  youtube-comment-ingester.py \
    --commenter "John Doe" \
    --text "How do I get started?" \
    [--timestamp "2026-04-20T09:30:00Z"] \
    [--inbox-file /path/to/queue]
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

def ingest_comment(commenter, text, timestamp=None, inbox_file=None):
    """Queue a comment for processing"""
    
    if not inbox_file:
        workspace = Path.home() / ".openclaw/workspace"
        inbox_file = workspace / ".cache" / "youtube-comments-inbox.jsonl"
    else:
        inbox_file = Path(inbox_file)
    
    # Create cache dir if needed
    inbox_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Use current time if not specified
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()
    
    comment = {
        "commenter": commenter,
        "text": text,
        "timestamp": timestamp
    }
    
    # Append to inbox
    with open(inbox_file, 'a') as f:
        f.write(json.dumps(comment) + '\n')
    
    print(f"✅ Comment queued from {commenter}")
    print(f"   Text: {text[:60]}..." if len(text) > 60 else f"   Text: {text}")
    print(f"   Inbox: {inbox_file}")
    
    return 0

def main():
    parser = argparse.ArgumentParser(
        description="Queue YouTube comments for processing"
    )
    parser.add_argument(
        '--commenter',
        required=True,
        help='Name of the commenter'
    )
    parser.add_argument(
        '--text',
        required=True,
        help='Comment text'
    )
    parser.add_argument(
        '--timestamp',
        default=None,
        help='ISO 8601 timestamp (default: now)'
    )
    parser.add_argument(
        '--inbox-file',
        default=None,
        help='Custom inbox file path'
    )
    
    args = parser.parse_args()
    
    return ingest_comment(
        commenter=args.commenter,
        text=args.text,
        timestamp=args.timestamp,
        inbox_file=args.inbox_file
    )

if __name__ == "__main__":
    sys.exit(main())
