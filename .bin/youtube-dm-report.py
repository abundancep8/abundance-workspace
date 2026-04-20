#!/usr/bin/env python3
"""Quick report across all YouTube DMs"""

import json
from datetime import datetime
from pathlib import Path

workspace = Path.home() / ".openclaw/workspace"
cache_file = workspace / ".cache/youtube-dms.jsonl"

stats = {
    "total": 0,
    "setup_help": 0,
    "newsletter": 0,
    "product_inquiry": 0,
    "partnership": 0,
    "partnerships_flagged": [],
    "product_inquiries": [],
}

if cache_file.exists():
    with open(cache_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                dm = json.loads(line)
                stats["total"] += 1
                
                category = dm.get('category', 'unknown')
                if category in stats:
                    stats[category] += 1
                
                if category == 'partnership':
                    stats["partnerships_flagged"].append({
                        "sender": dm.get('sender_name') or dm.get('sender', 'Unknown'),
                        "text": dm.get('text', '')[:80],
                        "timestamp": dm.get('timestamp', '')
                    })
                
                if category == 'product_inquiry':
                    stats["product_inquiries"].append({
                        "sender": dm.get('sender_name') or dm.get('sender', 'Unknown'),
                        "text": dm.get('text', '')[:80],
                        "timestamp": dm.get('timestamp', '')
                    })
            except:
                pass

print(f"""
╔════════════════════════════════════════════╗
║   YOUTUBE DM MONITOR - CONCESSA OBVIUS     ║
║   Comprehensive Report (All Time)          ║
╚════════════════════════════════════════════╝

Generated: {datetime.now().isoformat()}

📊 TOTAL STATS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total DMs Processed:         {stats['total']}
Auto-Responses Sent:         {stats['total']}
Conversion Potential (leads): {stats['product_inquiry']} ⭐

📋 BREAKDOWN BY CATEGORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Setup Help.................. {stats['setup_help']}
📧 Newsletter.................. {stats['newsletter']}
⭐ Product Inquiry............. {stats['product_inquiry']}
🚩 Partnership................. {stats['partnership']}

""")

if stats['partnerships_flagged']:
    print(f"🚩 PARTNERSHIPS FOR MANUAL REVIEW ({len(stats['partnerships_flagged'])})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    for pf in stats['partnerships_flagged']:
        print(f"  • {pf['sender']}: {pf['text']}...")
        print(f"    [{pf['timestamp']}]\n")

if stats['product_inquiries']:
    print(f"\n💡 PRODUCT INQUIRY LEADS ({len(stats['product_inquiries'])})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    for pi in stats['product_inquiries']:
        print(f"  • {pi['sender']}: {pi['text']}...")

print("\n✅ Monitor Status: ACTIVE | 📍 Next check: Hourly")
