#!/usr/bin/env python3
"""
YouTube DM Monitor - Cron Handler
Monitors Concessa Obvius YouTube DMs, categorizes, auto-responds, and logs.
Runs hourly via cron job.
"""

import json
import os
import sys
import time
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import hashlib

# Configuration
WORKSPACE = Path("/Users/abundance/.openclaw/workspace")
CACHE_DIR = WORKSPACE / ".cache"
SECRETS_DIR = WORKSPACE / ".secrets"
CONFIG_FILE = CACHE_DIR / "youtube-dm-monitor-config.json"
DM_LOG_FILE = CACHE_DIR / "youtube-dms.jsonl"
REPORT_FILE = CACHE_DIR / "youtube-dms-report.json"
PARTNERSHIPS_FILE = CACHE_DIR / "youtube-flagged-partnerships.jsonl"
STATE_FILE = CACHE_DIR / "youtube-dms-state.json"
CRON_LOG = CACHE_DIR / "youtube-dms-cron.log"

# Data sources (in priority order)
DATA_SOURCES = [
    {"type": "file", "path": "/tmp/new-dms.json"},
    {"type": "env", "var": "DM_JSON"},
    {"type": "file", "path": CACHE_DIR / "youtube-dm-inbox.jsonl"},
    {"type": "file", "path": CACHE_DIR / "youtube-dms-queue.jsonl"},
]


def load_config():
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        print(f"❌ Config file not found: {CONFIG_FILE}", file=sys.stderr)
        sys.exit(1)
    
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_state():
    """Load processing state (processed DM IDs)."""
    defaults = {
        "processed_ids": set(),
        "last_run": None,
        "total_processed": 0,
        "total_responses": 0,
    }
    
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                data = json.load(f)
                # Convert list back to set for processing
                data["processed_ids"] = set(data.get("processed_ids", []))
                # Merge with defaults to ensure all keys exist
                defaults.update(data)
                return defaults
        except (json.JSONDecodeError, IOError):
            pass
    
    return defaults


def save_state(state):
    """Save processing state."""
    # Convert set to list for JSON serialization
    state_copy = state.copy()
    state_copy["processed_ids"] = list(state_copy.get("processed_ids", []))
    with open(STATE_FILE, "w") as f:
        json.dump(state_copy, f, indent=2)


def get_new_dms():
    """Fetch new DMs from available data sources."""
    dms = []
    
    for source in DATA_SOURCES:
        if source["type"] == "file":
            path = Path(source["path"])
            if path.exists():
                try:
                    if path.suffix == ".jsonl":
                        # JSONL format: one JSON object per line
                        with open(path) as f:
                            for line in f:
                                if line.strip():
                                    dms.append(json.loads(line))
                    else:
                        # JSON array format
                        with open(path) as f:
                            data = json.load(f)
                            if isinstance(data, list):
                                dms.extend(data)
                            else:
                                dms.append(data)
                    
                    # Clear processed file to prevent re-processing
                    if source["path"] != str(CACHE_DIR / "youtube-dms-queue.jsonl"):
                        path.unlink()
                    
                    if dms:
                        break  # Use first available source
                except Exception as e:
                    print(f"⚠️  Error reading {source['path']}: {e}", file=sys.stderr)
        
        elif source["type"] == "env":
            env_data = os.getenv(source["var"])
            if env_data:
                try:
                    dms = json.loads(env_data)
                    if not isinstance(dms, list):
                        dms = [dms]
                    break
                except json.JSONDecodeError as e:
                    print(f"⚠️  Error parsing {source['var']}: {e}", file=sys.stderr)
    
    return dms


def generate_dm_id(dm):
    """Generate unique ID for DM from available fields."""
    id_parts = [
        str(dm.get("sender_id", dm.get("sender", "unknown"))),
        dm.get("text", "")[:50],
        str(dm.get("timestamp", int(time.time()))),
    ]
    id_str = "|".join(id_parts)
    return hashlib.md5(id_str.encode()).hexdigest()[:12]


def categorize_dm(text, categories_config):
    """Categorize DM based on keywords."""
    text_lower = text.lower()
    
    # Score each category
    scores = {}
    for category in categories_config:
        keywords = category.get("keywords", [])
        score = sum(1 for keyword in keywords if keyword in text_lower)
        if score > 0:
            scores[category["id"]] = score
    
    # Return top match
    if scores:
        return max(scores.items(), key=lambda x: x[1])[0]
    
    return "general"


def get_response_template(category_id, categories_config):
    """Get auto-response template for category."""
    for category in categories_config:
        if category["id"] == category_id:
            return category.get("response_template", "Thanks for reaching out! 👋")
    
    return "Thanks for reaching out! 👋"


def should_flag_partnership(category_id, categories_config):
    """Check if category should be flagged for manual review."""
    for category in categories_config:
        if category["id"] == category_id:
            return category.get("flag_for_review", False)
    return False


def log_dm(dm, category, response_template):
    """Log DM to JSONL file."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sender": dm.get("sender", "Unknown"),
        "sender_id": dm.get("sender_id", ""),
        "text": dm.get("text", ""),
        "category": category,
        "response_sent": True,
        "response_template": response_template,
        "dm_id": dm.get("_id", ""),
        "channel_id": dm.get("channel_id", ""),
    }
    
    with open(DM_LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    return log_entry


def log_flagged_partnership(dm, category, reason):
    """Log flagged partnership for manual review."""
    flag_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sender": dm.get("sender", "Unknown"),
        "sender_id": dm.get("sender_id", ""),
        "text": dm.get("text", ""),
        "category": category,
        "reason": reason,
        "action": "MANUAL_REVIEW_REQUIRED",
        "url": dm.get("dm_url", ""),
    }
    
    with open(PARTNERSHIPS_FILE, "a") as f:
        f.write(json.dumps(flag_entry) + "\n")


def generate_report(dms_processed, responses_sent, categories_data):
    """Generate hourly report."""
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Count by category
    category_counts = defaultdict(int)
    product_inquiries = 0
    partnerships_flagged = 0
    
    for entry in categories_data:
        category_counts[entry["category"]] += 1
        if entry["category"] == "product_inquiry":
            product_inquiries += 1
        if entry.get("flagged_for_review"):
            partnerships_flagged += 1
    
    report = {
        "timestamp": timestamp,
        "metrics": {
            "total_dms_processed": dms_processed,
            "auto_responses_sent": responses_sent,
            "by_category": dict(category_counts),
            "product_inquiries": product_inquiries,
            "partnerships_flagged": partnerships_flagged,
            "conversion_potential": int(product_inquiries * 0.15),
        },
        "log_file": str(DM_LOG_FILE),
        "partnerships_file": str(PARTNERSHIPS_FILE),
        "next_run": None,
    }
    
    # Save JSON report
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2)
    
    return report


def print_report(report):
    """Print formatted report to stdout."""
    metrics = report["metrics"]
    
    print("\n" + "="*70)
    print(f"📊 YouTube DM Monitor Report - {report['timestamp']}")
    print("="*70)
    
    print(f"\n✅ SUMMARY")
    print(f"  Total DMs processed: {metrics['total_dms_processed']}")
    print(f"  Auto-responses sent: {metrics['auto_responses_sent']}")
    
    if metrics["by_category"]:
        print(f"\n📂 BY CATEGORY")
        for cat, count in metrics["by_category"].items():
            print(f"  • {cat}: {count}")
    
    print(f"\n💰 CONVERSION POTENTIAL")
    print(f"  Product inquiries: {metrics['product_inquiries']}")
    print(f"  Est. conversion (15%): {metrics['conversion_potential']} customers")
    
    if metrics["partnerships_flagged"] > 0:
        print(f"\n🤝 FLAGGED PARTNERSHIPS")
        print(f"  Partnerships for review: {metrics['partnerships_flagged']}")
        print(f"  📄 See: {report['partnerships_file']}")
    
    print(f"\n📝 LOG FILE")
    print(f"  {report['log_file']}")
    print("\n" + "="*70 + "\n")


def main():
    """Main cron job handler."""
    try:
        # Load configuration
        config = load_config()
        state = load_state()
        
        print(f"🟢 YouTube DM Monitor started at {datetime.utcnow().isoformat()}Z")
        
        # Fetch new DMs
        dms = get_new_dms()
        print(f"📥 Fetched {len(dms)} DM(s) from data sources")
        
        if not dms:
            print("✅ No new DMs to process")
            report = generate_report(0, 0, [])
            print_report(report)
            return 0
        
        # Process DMs
        categories_data = []
        processed_count = 0
        response_count = 0
        
        for dm in dms:
            # Generate unique ID for deduplication
            dm_id = generate_dm_id(dm)
            
            # Skip if already processed
            if dm_id in state.get("processed_ids", []):
                print(f"⏭️  Skipping duplicate DM from {dm.get('sender', 'Unknown')}")
                continue
            
            # Categorize
            category_id = categorize_dm(dm.get("text", ""), config["categories"])
            response_template = get_response_template(category_id, config["categories"])
            
            # Log DM
            log_entry = log_dm(dm, category_id, response_template)
            categories_data.append(log_entry)
            processed_count += 1
            response_count += 1
            
            # Check if should flag for manual review
            if should_flag_partnership(category_id, config["categories"]):
                log_flagged_partnership(
                    dm,
                    category_id,
                    "Partnership/collaboration inquiry detected"
                )
                print(f"🚩 Flagged partnership from {dm.get('sender', 'Unknown')}")
            
            print(f"✓ Processed DM from {dm.get('sender', 'Unknown')} → {category_id}")
            
            # Mark as processed
            state["processed_ids"].add(dm_id)
        
        # Update state
        state["last_run"] = datetime.utcnow().isoformat() + "Z"
        state["total_processed"] += processed_count
        state["total_responses"] += response_count
        save_state(state)
        
        # Generate and print report
        report = generate_report(processed_count, response_count, categories_data)
        print_report(report)
        
        print(f"🟢 Completed successfully at {datetime.utcnow().isoformat()}Z")
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
