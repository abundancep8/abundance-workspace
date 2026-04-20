#!/usr/bin/env python3
"""
YouTube DM Ingester
Accepts DMs from various sources (email, webhooks, manual queue) and queues them for processing.

Usage:
  # Via command line:
  python3 youtube-dm-ingester.py --sender "John Doe" --text "I have a question" --id "sender123"
  
  # Via JSON file:
  echo '{"sender_name":"Jane","text":"interested in pricing","sender_id":"jane123","dm_id":"dm_123"}' >> .cache/youtube-dm-inbox.jsonl
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

workspace = Path.home() / ".openclaw/workspace"
inbox_file = workspace / ".cache/youtube-dm-inbox.jsonl"
inbox_file.parent.mkdir(parents=True, exist_ok=True)

def ingest_dm(sender_name: str, text: str, sender_id: str, dm_id: str = None):
    """Add a DM to the inbox for processing"""
    if not sender_name or not text:
        print("❌ Error: sender_name and text are required", file=sys.stderr)
        return False
    
    dm_record = {
        "sender_name": sender_name,
        "text": text,
        "sender_id": sender_id or f"user_{sender_name.lower().replace(' ', '_')}",
        "dm_id": dm_id or f"dm_{int(datetime.utcnow().timestamp())}",
        "queued_at": datetime.utcnow().isoformat() + "Z"
    }
    
    try:
        with open(inbox_file, 'a') as f:
            f.write(json.dumps(dm_record) + '\n')
        print(f"✅ DM queued from {sender_name}")
        return True
    except Exception as e:
        print(f"❌ Error queuing DM: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Queue a YouTube DM for processing by the hourly monitor"
    )
    parser.add_argument("--sender", required=True, help="Sender name")
    parser.add_argument("--text", required=True, help="DM text content")
    parser.add_argument("--id", default=None, help="Sender ID (optional)")
    parser.add_argument("--dm-id", default=None, help="DM ID (optional)")
    
    args = parser.parse_args()
    
    success = ingest_dm(args.sender, args.text, args.id, args.dm_id)
    sys.exit(0 if success else 1)
