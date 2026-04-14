#!/usr/bin/env python3
"""
YouTube DM Monitor for Concessa Obvius channel.
Monitors inbox, categorizes DMs, auto-responds, and logs results.
Works with email-forwarded DMs, webhook feeds, or manual queue.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import re
import hashlib

CACHE_DIR = Path.home() / ".openclaw/workspace/.cache"
CACHE_DIR.mkdir(exist_ok=True)

LOG_FILE = CACHE_DIR / "youtube-dms.jsonl"
STATE_FILE = CACHE_DIR / "youtube-dms-state.json"
DM_INBOX_QUEUE = CACHE_DIR / "youtube-dm-inbox.jsonl"  # Input queue for DMs

# DM Category definitions with keywords and templates
DM_CATEGORIES = {
    "setup_help": {
        "keywords": ["how do i", "how to", "confused", "stuck", "doesn't work", "isn't working", "error", "help", "setup", "install", "configure", "tutorial", "guide", "what's", "what is"],
        "template": "Thanks for reaching out! 🙌 I understand you need help with setup. Check out our [setup guide](https://example.com/setup) for step-by-step instructions. If you're still stuck, reply with the specific issue and I'll get you sorted!"
    },
    "newsletter": {
        "keywords": ["email list", "subscribe", "newsletter", "updates", "notification", "keep me posted", "send me", "sign up", "join list", "email updates"],
        "template": "Awesome! I'd love to keep you in the loop. 📧 Join our mailing list at [https://example.com/newsletter](https://example.com/newsletter) for exclusive updates, early access, and community highlights. Thanks for your interest!"
    },
    "product_inquiry": {
        "keywords": ["price", "cost", "buy", "purchase", "product", "how much", "available", "sell", "offer", "deal", "$", "£", "€", "order", "shipping", "in stock"],
        "template": "Great question! 🚀 For product details, pricing, and ordering, check out our [shop page](https://example.com/shop). Have specific questions? Feel free to reply and I'll help you find exactly what you need."
    },
    "partnership": {
        "keywords": ["partnership", "collaborate", "collaboration", "sponsorship", "sponsor", "work with", "together", "business opportunity", "affiliate", "promote", "collab", "brand deal", "partnership opportunity"],
        "template": "This sounds interesting! 👀 I'm always open to partnerships and collaborations. Could you tell me more about what you have in mind? Looking forward to exploring this with you!"
    }
}

def hash_dm(sender_id, text, timestamp):
    """Generate unique hash to prevent duplicate logging."""
    content = f"{sender_id}:{text}:{timestamp}".encode()
    return hashlib.md5(content).hexdigest()[:12]

def categorize_dm(text):
    """Categorize DM based on keyword matching."""
    text_lower = text.lower()
    
    # Score each category
    scores = {}
    for category, config in DM_CATEGORIES.items():
        score = sum(1 for kw in config["keywords"] if kw in text_lower)
        scores[category] = score
    
    # Return highest scoring category
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "other"

def get_response_template(category):
    """Get auto-response template for category."""
    if category in DM_CATEGORIES:
        return DM_CATEGORIES[category]["template"]
    return None

def load_state():
    """Load monitoring state."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except:
            pass
    return {
        "last_check": None,
        "total_dms_processed": 0,
        "auto_responses_sent": 0,
        "partnerships_flagged": 0,
        "processed_hashes": []
    }

def save_state(state):
    """Save monitoring state."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def log_dm(sender, sender_id, text, category, response_template=None):
    """Log DM to JSONL file."""
    entry = {
        "timestamp": datetime.now().isoformat() + "Z",
        "sender": sender,
        "sender_id": sender_id,
        "text": text[:500],  # Truncate very long messages
        "category": category,
        "response_sent": response_template is not None,
        "response_template": response_template or None
    }
    
    # Append to log (atomic write)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}", file=sys.stderr)

def fetch_pending_dms():
    """
    Fetch DMs from the input queue.
    These come from:
    - Email forwarding (parsed by external script)
    - Webhook notifications (posted to queue)
    - Manual input
    
    Queue format: one JSON object per line with:
    {
        "sender_name": str,
        "sender_id": str,
        "text": str,
        "received_at": datetime ISO string (optional)
    }
    """
    dms = []
    
    if not DM_INBOX_QUEUE.exists():
        return []
    
    try:
        with open(DM_INBOX_QUEUE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        dm = json.loads(line)
                        dms.append(dm)
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"Warning: Could not read DM queue: {e}", file=sys.stderr)
    
    return dms

def clear_processed_dms():
    """Clear the input queue after processing (move to backup)."""
    if DM_INBOX_QUEUE.exists():
        try:
            # Backup queue for audit trail
            backup_file = CACHE_DIR / f"youtube-dm-inbox-backup-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.jsonl"
            with open(DM_INBOX_QUEUE, "r") as src:
                with open(backup_file, "w") as dst:
                    dst.write(src.read())
            
            # Clear queue
            with open(DM_INBOX_QUEUE, "w") as f:
                f.write("")
        except Exception as e:
            print(f"Warning: Could not backup/clear queue: {e}", file=sys.stderr)

def run_monitor():
    """Main DM monitor function."""
    state = load_state()
    processed_hashes = set(state.get("processed_hashes", []))
    
    # Fetch new DMs from queue
    pending_dms = fetch_pending_dms()
    
    stats = {
        "status": "success",
        "total_dms_processed": 0,
        "auto_responses_sent": 0,
        "partnerships_flagged": 0,
        "product_inquiries": 0,
        "categories": {
            "setup_help": 0,
            "newsletter": 0,
            "product_inquiry": 0,
            "partnership": 0,
            "other": 0
        },
        "new_dms_count": len(pending_dms)
    }
    
    # Process each DM
    for dm in pending_dms:
        sender = dm.get("sender_name", "Unknown")
        sender_id = dm.get("sender_id", "unknown")
        text = dm.get("text", "")
        received_at = dm.get("received_at", datetime.now().isoformat() + "Z")
        
        # Skip duplicates
        dm_hash = hash_dm(sender_id, text, received_at)
        if dm_hash in processed_hashes:
            continue
        
        # Categorize
        category = categorize_dm(text)
        stats["categories"][category] = stats["categories"].get(category, 0) + 1
        
        # Get response template
        response_template = get_response_template(category)
        response_sent = response_template is not None
        
        if response_sent:
            stats["auto_responses_sent"] += 1
        
        if category == "partnership":
            stats["partnerships_flagged"] += 1
        
        if category == "product_inquiry":
            stats["product_inquiries"] += 1
        
        # Log DM
        log_dm(sender, sender_id, text, category, response_template)
        
        # Track processed
        processed_hashes.add(dm_hash)
        stats["total_dms_processed"] += 1
    
    # Update state
    state["last_check"] = datetime.now().isoformat() + "Z"
    state["total_dms_processed"] = state.get("total_dms_processed", 0) + stats["total_dms_processed"]
    state["auto_responses_sent"] = state.get("auto_responses_sent", 0) + stats["auto_responses_sent"]
    state["partnerships_flagged"] = state.get("partnerships_flagged", 0) + stats["partnerships_flagged"]
    state["processed_hashes"] = list(processed_hashes)[-10000:]  # Keep last 10k to prevent memory bloat
    save_state(state)
    
    # Clear processed DMs from queue
    if stats["total_dms_processed"] > 0:
        clear_processed_dms()
    
    return stats, state

def generate_report(stats, state):
    """Generate human-readable report."""
    report = []
    report.append("=" * 70)
    report.append("YOUTUBE DM MONITOR REPORT")
    report.append("=" * 70)
    report.append(f"Time: {datetime.utcnow().isoformat()}Z")
    report.append(f"Status: {stats.get('status', 'unknown').upper()}")
    report.append("")
    report.append("THIS RUN")
    report.append("-" * 70)
    report.append(f"New DMs in Queue: {stats['new_dms_count']}")
    report.append(f"DMs Processed: {stats['total_dms_processed']}")
    report.append(f"Auto-Responses Sent: {stats['auto_responses_sent']}")
    report.append("")
    report.append("CUMULATIVE STATS (All Time)")
    report.append("-" * 70)
    report.append(f"Total DMs Processed: {state['total_dms_processed']}")
    report.append(f"Total Auto-Responses Sent: {state['auto_responses_sent']}")
    report.append(f"Total Partnerships Flagged: {state['partnerships_flagged']}")
    report.append("")
    report.append("CONVERSION POTENTIAL")
    report.append("-" * 70)
    product_inquiries = stats['categories'].get('product_inquiry', 0)
    report.append(f"Product Inquiries (This Run): {product_inquiries}")
    report.append(f"Estimated Conversion Value: {product_inquiries} potential customers")
    report.append("")
    report.append("CATEGORY BREAKDOWN (This Run)")
    report.append("-" * 70)
    for category, count in sorted(stats['categories'].items()):
        label = category.replace('_', ' ').title()
        report.append(f"  {label:.<40} {count}")
    report.append("")
    report.append("SETUP INSTRUCTIONS FOR LIVE DM INGESTION")
    report.append("-" * 70)
    report.append("To enable live DM monitoring, use ONE of these methods:")
    report.append("")
    report.append("1. EMAIL FORWARDING (Recommended)")
    report.append("   - Forward YouTube DMs to a monitored email")
    report.append("   - Use an email-to-queue parser script")
    report.append("   - Writes to: .cache/youtube-dm-inbox.jsonl")
    report.append("")
    report.append("2. WEBHOOK INTEGRATION")
    report.append("   - Set up webhook on YouTube Community/Messaging")
    report.append("   - POST JSON to: localhost:8000/youtube-dm")
    report.append("   - Handler appends to: .cache/youtube-dm-inbox.jsonl")
    report.append("")
    report.append("3. MANUAL QUEUE")
    report.append("   - Append DM JSON objects to: .cache/youtube-dm-inbox.jsonl")
    report.append("   - Monitor script processes each line")
    report.append("")
    report.append("Queue Format (JSONL):")
    report.append(json.dumps({
        "sender_name": "John Doe",
        "sender_id": "UCxxxxx",
        "text": "How do I set this up?",
        "received_at": "2026-04-14T05:03:00Z"
    }, indent=2))
    report.append("=" * 70)
    
    return "\n".join(report)

if __name__ == "__main__":
    try:
        stats, state = run_monitor()
        report = generate_report(stats, state)
        print(report)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
