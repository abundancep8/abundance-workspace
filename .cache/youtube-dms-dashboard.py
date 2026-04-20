#!/usr/bin/env python3
"""
YouTube DM Monitor Dashboard
View real-time stats, logs, and flagged items.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

CACHE_DIR = Path("/Users/abundance/.openclaw/workspace/.cache")
DM_LOG = CACHE_DIR / "youtube-dms.jsonl"
PARTNERSHIPS_LOG = CACHE_DIR / "youtube-flagged-partnerships.jsonl"
REPORT_FILE = CACHE_DIR / "youtube-dms-report.json"
STATE_FILE = CACHE_DIR / "youtube-dms-state.json"


def load_jsonl(filepath):
    """Load JSONL file."""
    lines = []
    if filepath.exists():
        with open(filepath) as f:
            for line in f:
                if line.strip():
                    try:
                        lines.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return lines


def print_header(title):
    """Print formatted header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def show_summary():
    """Show summary dashboard."""
    print_header("YouTube DM Monitor - Dashboard")
    
    # Load state
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            state = json.load(f)
            print(f"📊 Lifetime Stats:")
            print(f"  Total DMs processed: {state.get('total_processed', 0)}")
            print(f"  Total responses sent: {state.get('total_responses', 0)}")
            print(f"  Last run: {state.get('last_run', 'Never')}")
    
    # Load latest report
    if REPORT_FILE.exists():
        with open(REPORT_FILE) as f:
            report = json.load(f)
            metrics = report.get("metrics", {})
            
            print(f"\n📈 Latest Run ({report['timestamp']}):")
            print(f"  DMs processed: {metrics.get('total_dms_processed', 0)}")
            print(f"  Responses sent: {metrics.get('auto_responses_sent', 0)}")
            
            if metrics.get("by_category"):
                print(f"\n  By Category:")
                for cat, count in metrics["by_category"].items():
                    print(f"    • {cat}: {count}")
            
            if metrics.get("partnerships_flagged", 0) > 0:
                print(f"\n  🚩 Partnerships flagged: {metrics['partnerships_flagged']}")


def show_recent_dms(limit=10):
    """Show recent DMs."""
    print_header("Recent DMs")
    
    dms = load_jsonl(DM_LOG)
    dms = dms[-limit:]  # Get last N
    
    if not dms:
        print("  (no DMs logged yet)")
        return
    
    for i, dm in enumerate(dms, 1):
        sender = dm.get("sender", "Unknown")
        category = dm.get("category", "uncategorized")
        text = dm.get("text", "")[:60]
        timestamp = dm.get("timestamp", "").split("T")[0]
        
        print(f"{i}. [{timestamp}] {sender} → {category}")
        print(f"   {text}...")
        print()


def show_flagged_partnerships(limit=20):
    """Show flagged partnerships."""
    print_header("Flagged Partnerships")
    
    partnerships = load_jsonl(PARTNERSHIPS_LOG)
    partnerships = partnerships[-limit:]
    
    if not partnerships:
        print("  ✅ No flagged partnerships")
        return
    
    for i, p in enumerate(partnerships, 1):
        sender = p.get("sender", "Unknown")
        reason = p.get("reason", "")
        text = p.get("text", "")[:60]
        timestamp = p.get("timestamp", "").split("T")[0]
        
        print(f"{i}. [{timestamp}] {sender}")
        print(f"   {reason}")
        print(f"   Text: {text}...")
        print()


def show_category_stats():
    """Show category breakdown."""
    print_header("Category Statistics")
    
    dms = load_jsonl(DM_LOG)
    categories = defaultdict(int)
    
    for dm in dms:
        cat = dm.get("category", "uncategorized")
        categories[cat] += 1
    
    if not categories:
        print("  (no data)")
        return
    
    total = sum(categories.values())
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total) * 100
        bar = "▓" * int(pct / 5)
        print(f"  {cat:20} {count:3}  {bar} {pct:5.1f}%")
    
    print(f"\n  Total: {total}")


def show_help():
    """Show help."""
    print("""
YouTube DM Monitor Dashboard

Usage:
  python3 youtube-dms-dashboard.py [command]

Commands:
  summary       - Show summary stats (default)
  recent        - Show recent DMs
  partnerships  - Show flagged partnerships
  categories    - Show category breakdown
  all           - Show all information
  help          - Show this help
""")


def main():
    """Main."""
    command = sys.argv[1] if len(sys.argv) > 1 else "summary"
    
    if command == "summary":
        show_summary()
    elif command == "recent":
        show_recent_dms()
    elif command == "partnerships":
        show_flagged_partnerships()
    elif command == "categories":
        show_category_stats()
    elif command == "all":
        show_summary()
        show_recent_dms()
        show_category_stats()
        show_flagged_partnerships()
    elif command in ["help", "-h", "--help"]:
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
