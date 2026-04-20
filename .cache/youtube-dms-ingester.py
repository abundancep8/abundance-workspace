#!/usr/bin/env python3
"""
YouTube DM Ingester
Accepts DMs from various sources and queues them for processing.
Can accept: manual JSON, environment variables, webhook payloads, etc.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

CACHE_DIR = Path("/Users/abundance/.openclaw/workspace/.cache")
QUEUE_FILE = CACHE_DIR / "youtube-dm-inbox.jsonl"


def normalize_dm(dm):
    """Normalize DM data to standard format."""
    if isinstance(dm, str):
        # If it's a string, assume it's the DM text
        dm = {"text": dm}
    
    # Ensure required fields
    normalized = {
        "sender": dm.get("sender") or dm.get("author") or "Unknown",
        "sender_id": dm.get("sender_id") or dm.get("user_id") or "",
        "text": dm.get("text") or dm.get("content") or dm.get("message") or "",
        "timestamp": dm.get("timestamp") or dm.get("created_at") or datetime.utcnow().isoformat(),
        "channel_id": dm.get("channel_id") or "",
        "dm_url": dm.get("dm_url") or "",
    }
    
    return normalized


def queue_dms(dms):
    """Queue DMs for processing."""
    if not isinstance(dms, list):
        dms = [dms]
    
    queued = []
    for dm in dms:
        try:
            normalized = normalize_dm(dm)
            with open(QUEUE_FILE, "a") as f:
                f.write(json.dumps(normalized) + "\n")
            queued.append(normalized)
        except Exception as e:
            print(f"❌ Error queueing DM: {e}", file=sys.stderr)
    
    return queued


def main():
    """Main ingester."""
    # Accept DMs from stdin
    try:
        input_data = sys.stdin.read()
        if not input_data.strip():
            print("ℹ️  No input provided", file=sys.stderr)
            return 1
        
        # Try to parse as JSON
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError:
            # Assume it's plain text
            data = {"text": input_data}
        
        queued = queue_dms(data)
        print(f"✅ Queued {len(queued)} DM(s)")
        print(json.dumps({"queued": len(queued), "dms": queued}, indent=2))
        return 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
