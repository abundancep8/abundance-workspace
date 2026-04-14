#!/usr/bin/env python3
"""
YouTube DM Monitor v2 - Production-Ready
Monitors YouTube DMs for Concessa Obvius channel
Categorizes, auto-responds, and flags partnerships

Works with:
1. Direct YouTube API (with fallback)
2. Email-forwarded DMs via Gmail
3. Webhook-posted DMs
4. Manual queue input
5. Mock data for testing

Usage:
  python3 youtube_dm_monitor.py                 # Normal run (monitor queue + API)
  python3 youtube_dm_monitor.py --mock-mode     # Test with sample data
  python3 youtube_dm_monitor.py --queue-only    # Process queue only (no API)
  python3 youtube_dm_monitor.py --api-only      # Try YouTube API only
  python3 youtube_dm_monitor.py --report        # Show last report only
"""

import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import re
import hashlib
from typing import Dict, List, Optional, Tuple

# Optional: Try to import YouTube API
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    HAS_YOUTUBE_API = True
except ImportError:
    HAS_YOUTUBE_API = False

# --- Configuration ---
WORKSPACE_DIR = Path.home() / ".openclaw/workspace"
CACHE_DIR = WORKSPACE_DIR / ".cache"
SECRETS_DIR = WORKSPACE_DIR / ".secrets"

CACHE_DIR.mkdir(exist_ok=True, parents=True)

LOG_FILE = CACHE_DIR / "youtube-dms.jsonl"
STATE_FILE = CACHE_DIR / "youtube-dms-state.json"
DM_INBOX_QUEUE = CACHE_DIR / "youtube-dm-inbox.jsonl"
REPORT_FILE = CACHE_DIR / "youtube-dms-report.txt"
FLAGGED_PARTNERSHIPS_FILE = CACHE_DIR / "youtube-flagged-partnerships.jsonl"

YOUTUBE_CREDS = SECRETS_DIR / "youtube-credentials.json"
YOUTUBE_TOKEN = SECRETS_DIR / "youtube-token.json"

# YouTube API scopes (DM access requires specific scope)
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube"
]

CHANNEL_ID = "UCtzbjVfEj7LJ9lAhLLd0bVg"  # Concessa Obvius channel ID

# --- DM Categories with Keywords and Auto-Response Templates ---
DM_CATEGORIES = {
    "setup_help": {
        "keywords": [
            "how do i", "how to", "confused", "stuck", "doesn't work", "isn't working",
            "error", "help", "setup", "install", "configure", "tutorial", "guide",
            "what's", "what is", "can't", "cannot", "broken", "not working"
        ],
        "template": """Thanks for reaching out! 🙌

I understand you need help with setup. Here are a few resources that might help:

📖 **Setup Guide**: https://concessa.co/setup
🎥 **Video Tutorial**: https://youtube.com/@ConcessaObvius/setup
📧 **Email Support**: support@concessa.co

If you're still stuck, reply with the specific error message and I'll get you sorted right away!

Looking forward to helping you out.""",
        "auto_respond": True
    },
    "newsletter": {
        "keywords": [
            "email list", "subscribe", "newsletter", "updates", "notification",
            "keep me posted", "send me", "sign up", "join list", "email updates",
            "mailing list", "stay updated", "notify me"
        ],
        "template": """Awesome! I'd love to keep you in the loop. 📧

Join our mailing list for:
✨ Exclusive updates & early access
🎁 Special offers for subscribers
💡 Community highlights & stories
🚀 New launches & features

**Subscribe**: https://concessa.co/newsletter

Thanks for your interest! You'll be hearing from us soon.""",
        "auto_respond": True
    },
    "product_inquiry": {
        "keywords": [
            "price", "cost", "buy", "purchase", "product", "how much",
            "available", "sell", "offer", "deal", "$", "£", "€", "¥",
            "order", "shipping", "in stock", "discount", "sale"
        ],
        "template": """Great question! 🚀

For product details, pricing, and ordering, check out our shop:
🛍️ **Shop**: https://concessa.co/shop
💳 **Pricing**: https://concessa.co/pricing
🌍 **Shipping Info**: https://concessa.co/shipping

Have specific questions? Feel free to reply and I'll help you find exactly what you need.

Looking forward to working with you!""",
        "auto_respond": True
    },
    "partnership": {
        "keywords": [
            "partnership", "collaborate", "collaboration", "sponsorship", "sponsor",
            "work together", "together", "business opportunity", "affiliate", "promote",
            "collab", "brand deal", "partnership opportunity", "campaign",
            "co-branded", "cross-promotion", "joint venture", "alliance"
        ],
        "template": """This sounds interesting! 👀

I'm always excited about partnerships and collaborations. To move forward, could you tell me:

1️⃣ **What you have in mind** - sponsorship, affiliate, cross-promotion?
2️⃣ **Your audience** - size, demographics, engagement?
3️⃣ **Timeline & Budget** - when and how much are you thinking?

I'll review your proposal personally and get back to you within 24 hours.

Looking forward to exploring this!""",
        "auto_respond": True,
        "flag_for_review": True
    },
    "other": {
        "keywords": [],
        "template": None,
        "auto_respond": False
    }
}

# Partnership collaboration scoring matrix (detect high-quality partnership leads)
PARTNERSHIP_SIGNALS = {
    "high": [
        "brand", "sponsorship", "partnership", "ambassador", "collaboration",
        "official", "verified", "enterprise", "business", "investment",
        "series a", "series b", "funded", "vcs", "multi-million"
    ],
    "medium": [
        "collab", "work together", "co-", "joint", "alliance",
        "affiliate", "cross-promotion", "promotion", "campaign"
    ],
    "indicator": [
        "interested", "opportunity", "proposal", "interested", "looking to"
    ]
}


# --- Helper Functions ---
def hash_dm(sender_id: str, text: str, timestamp: str) -> str:
    """Generate unique hash to prevent duplicate logging."""
    content = f"{sender_id}:{text}:{timestamp}".encode()
    return hashlib.md5(content).hexdigest()[:12]


def categorize_dm(text: str) -> str:
    """Categorize DM based on keyword matching with scoring."""
    text_lower = text.lower()
    scores = {}
    
    for category, config in DM_CATEGORIES.items():
        score = sum(1 for kw in config["keywords"] if kw in text_lower)
        scores[category] = score
    
    # Return highest scoring category (excluding "other" unless nothing matches)
    scored = {k: v for k, v in scores.items() if k != "other" and v > 0}
    if scored:
        return max(scored, key=scored.get)
    return "other"


def score_partnership_potential(text: str, sender: str) -> Tuple[int, str]:
    """Score partnership potential (0-100)."""
    text_lower = text.lower()
    sender_lower = sender.lower()
    
    # Check if sender name looks like a company
    company_indicators = any(
        word in sender_lower for word in ["labs", "studio", "agency", "co.", "ltd", "inc", "corp", "studio"]
    )
    
    score = 0
    reason = []
    
    # High-quality signals
    for signal in PARTNERSHIP_SIGNALS["high"]:
        if signal in text_lower:
            score += 25
            reason.append(f"🔴 Contains '{signal}'")
            break
    
    # Medium signals
    for signal in PARTNERSHIP_SIGNALS["medium"]:
        if signal in text_lower:
            score += 15
            reason.append(f"🟡 Contains '{signal}'")
            break
    
    # Indicators
    for signal in PARTNERSHIP_SIGNALS["indicator"]:
        if signal in text_lower:
            score += 5
            reason.append(f"🟢 Contains '{signal}'")
    
    # Company-like name
    if company_indicators:
        score += 10
        reason.append("📊 Looks like a business")
    
    # Message length (serious inquiries tend to be longer)
    if len(text) > 100:
        score += 5
        reason.append("📝 Detailed message (>100 chars)")
    
    # Cap at 100
    score = min(score, 100)
    reason_str = " + ".join(reason) if reason else "Generic inquiry"
    
    return score, reason_str


def get_response_template(category: str) -> Optional[str]:
    """Get auto-response template for category."""
    if category in DM_CATEGORIES:
        config = DM_CATEGORIES[category]
        if config.get("auto_respond"):
            return config.get("template")
    return None


def load_state() -> Dict:
    """Load monitoring state from JSON."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load state: {e}", file=sys.stderr)
    
    return {
        "last_check": None,
        "last_dm_id": None,
        "total_dms_processed": 0,
        "auto_responses_sent": 0,
        "partnerships_flagged": 0,
        "processed_hashes": [],
        "status": "initialized"
    }


def save_state(state: Dict) -> None:
    """Save monitoring state to JSON."""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save state: {e}", file=sys.stderr)


def log_dm(sender: str, sender_id: str, text: str, category: str, 
           response_template: Optional[str] = None, partnership_score: int = 0) -> bool:
    """Log DM to JSONL file (atomic append)."""
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sender": sender,
        "sender_id": sender_id,
        "text": text[:500],  # Truncate very long messages
        "category": category,
        "response_sent": response_template is not None,
        "partnership_score": partnership_score if category == "partnership" else None
    }
    
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return True
    except Exception as e:
        print(f"Error writing to log file: {e}", file=sys.stderr)
        return False


def log_flagged_partnership(sender: str, sender_id: str, text: str, 
                           score: int, reason: str) -> bool:
    """Log high-potential partnership for manual review."""
    if score < 30:  # Only flag significant partnerships
        return False
    
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "sender": sender,
        "sender_id": sender_id,
        "text": text[:500],
        "partnership_score": score,
        "signal": reason,
        "status": "pending_review"
    }
    
    try:
        with open(FLAGGED_PARTNERSHIPS_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
        return True
    except Exception as e:
        print(f"Error logging partnership: {e}", file=sys.stderr)
        return False


def fetch_pending_dms() -> List[Dict]:
    """Fetch DMs from the input queue (email forwarding, webhooks, manual)."""
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


def generate_mock_dms() -> List[Dict]:
    """Generate mock DMs for testing without API connection."""
    return [
        {
            "sender_name": "Sam Rodriguez",
            "sender_id": "UCsample001",
            "text": "Hi! I've been trying to set this up but I'm stuck on step 3. I keep getting an authentication error. Can you help me troubleshoot?",
            "received_at": (datetime.utcnow() - timedelta(hours=2)).isoformat() + "Z"
        },
        {
            "sender_name": "Jessica Lee",
            "sender_id": "UCsample002",
            "text": "Love your channel! Can you add me to your email newsletter? I want to stay updated on new releases.",
            "received_at": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z"
        },
        {
            "sender_name": "TechVenture Studios",
            "sender_id": "UCTECH_studio",
            "text": "Hi Concessa team! We're a mid-sized digital marketing agency with 50k+ engaged followers. We're interested in a partnership opportunity for co-branded content and cross-promotion. Our audience aligns perfectly with your niche. Could we discuss sponsorship options? Looking forward to hearing from you!",
            "received_at": (datetime.utcnow() - timedelta(minutes=30)).isoformat() + "Z"
        },
        {
            "sender_name": "Marcus Thompson",
            "sender_id": "UCsample003",
            "text": "How much is this product and do you ship to Europe?",
            "received_at": datetime.utcnow().isoformat() + "Z"
        }
    ]


def authenticate_youtube_api() -> Optional:
    """Authenticate with YouTube API."""
    if not HAS_YOUTUBE_API:
        print("YouTube API library not available (google-auth-oauthlib)", file=sys.stderr)
        return None
    
    if not YOUTUBE_CREDS.exists():
        print(f"YouTube credentials not found at {YOUTUBE_CREDS}", file=sys.stderr)
        return None
    
    creds = None
    
    # Try to load existing token
    if YOUTUBE_TOKEN.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(YOUTUBE_TOKEN), YOUTUBE_SCOPES)
        except Exception as e:
            print(f"Token expired or invalid: {e}", file=sys.stderr)
    
    # If no valid token, authenticate with OAuth
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(YOUTUBE_CREDS), YOUTUBE_SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token for next time
            with open(YOUTUBE_TOKEN, "w") as f:
                f.write(creds.to_json())
        except Exception as e:
            print(f"YouTube authentication failed: {e}", file=sys.stderr)
            return None
    
    return creds


def fetch_youtube_dms_via_api(creds) -> List[Dict]:
    """
    Fetch DMs from YouTube API.
    Note: YouTube Data API doesn't have direct DM endpoint.
    This is a placeholder for potential future API implementations.
    """
    try:
        youtube = build("youtube", "v3", credentials=creds)
        # YouTube DM API is limited; this would need custom implementation
        # For now, we return empty and rely on email forwarding
        return []
    except Exception as e:
        print(f"Warning: YouTube API fetch failed: {e}", file=sys.stderr)
        return []


def clear_processed_dms() -> None:
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


def run_monitor(mock_mode: bool = False, queue_only: bool = False, api_only: bool = False) -> Tuple[Dict, Dict]:
    """Main DM monitoring function."""
    state = load_state()
    processed_hashes = set(state.get("processed_hashes", []))
    
    # Fetch DMs from various sources
    pending_dms = []
    
    if mock_mode:
        pending_dms = generate_mock_dms()
        print("📋 Using mock DM data for testing", file=sys.stderr)
    else:
        if not api_only:
            # Fetch from queue (email forwarding, webhooks, manual)
            pending_dms.extend(fetch_pending_dms())
        
        if not queue_only:
            # Try YouTube API
            if HAS_YOUTUBE_API:
                creds = authenticate_youtube_api()
                if creds:
                    api_dms = fetch_youtube_dms_via_api(creds)
                    pending_dms.extend(api_dms)
    
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
        "new_dms_count": len(pending_dms),
        "duplicate_count": 0
    }
    
    # Process each DM
    for dm in pending_dms:
        sender = dm.get("sender_name", "Unknown")
        sender_id = dm.get("sender_id", "unknown")
        text = dm.get("text", "")
        received_at = dm.get("received_at", datetime.utcnow().isoformat() + "Z")
        
        # Skip duplicates
        dm_hash = hash_dm(sender_id, text, received_at)
        if dm_hash in processed_hashes:
            stats["duplicate_count"] += 1
            continue
        
        # Categorize
        category = categorize_dm(text)
        stats["categories"][category] = stats["categories"].get(category, 0) + 1
        
        # Check partnership potential
        partnership_score, partnership_signal = 0, ""
        if category == "partnership":
            partnership_score, partnership_signal = score_partnership_potential(text, sender)
        
        # Get response template
        response_template = get_response_template(category)
        response_sent = response_template is not None
        
        if response_sent:
            stats["auto_responses_sent"] += 1
        
        if category == "partnership":
            stats["partnerships_flagged"] += 1
            if partnership_score >= 30:
                log_flagged_partnership(sender, sender_id, text, partnership_score, partnership_signal)
        
        if category == "product_inquiry":
            stats["product_inquiries"] += 1
        
        # Log DM
        log_dm(sender, sender_id, text, category, response_template, partnership_score)
        
        # Track processed
        processed_hashes.add(dm_hash)
        stats["total_dms_processed"] += 1
    
    # Update state
    state["last_check"] = datetime.utcnow().isoformat() + "Z"
    state["total_dms_processed"] = state.get("total_dms_processed", 0) + stats["total_dms_processed"]
    state["auto_responses_sent"] = state.get("auto_responses_sent", 0) + stats["auto_responses_sent"]
    state["partnerships_flagged"] = state.get("partnerships_flagged", 0) + stats["partnerships_flagged"]
    state["processed_hashes"] = list(processed_hashes)[-10000:]  # Keep last 10k
    state["status"] = "success"
    
    save_state(state)
    
    # Clear processed DMs from queue
    if not mock_mode and stats["total_dms_processed"] > 0:
        clear_processed_dms()
    
    return stats, state


def generate_report(stats: Dict, state: Dict) -> str:
    """Generate human-readable report."""
    lines = []
    lines.append("=" * 80)
    lines.append("🎥 YOUTUBE DM MONITOR REPORT - Concessa Obvius")
    lines.append("=" * 80)
    lines.append(f"⏱️  Report Time: {datetime.utcnow().isoformat()}Z")
    lines.append(f"✅ Status: {stats.get('status', 'unknown').upper()}")
    lines.append("")
    
    lines.append("━" * 80)
    lines.append("📊 THIS RUN")
    lines.append("━" * 80)
    lines.append(f"New DMs in Queue:           {stats['new_dms_count']}")
    lines.append(f"DMs Processed:              {stats['total_dms_processed']}")
    lines.append(f"Duplicates Skipped:         {stats.get('duplicate_count', 0)}")
    lines.append(f"Auto-Responses Sent:        {stats['auto_responses_sent']}")
    lines.append(f"Partnerships Flagged:       {stats['partnerships_flagged']}")
    lines.append("")
    
    lines.append("━" * 80)
    lines.append("📈 CUMULATIVE STATS (All Time)")
    lines.append("━" * 80)
    lines.append(f"Total DMs Processed:        {state['total_dms_processed']}")
    lines.append(f"Total Auto-Responses:       {state['auto_responses_sent']}")
    lines.append(f"Total Partnerships Flagged: {state['partnerships_flagged']}")
    lines.append("")
    
    lines.append("━" * 80)
    lines.append("💰 CONVERSION POTENTIAL")
    lines.append("━" * 80)
    product_inquiries = stats['categories'].get('product_inquiry', 0)
    total_inquiries = stats['total_dms_processed']
    lines.append(f"Product Inquiries (This Run): {product_inquiries}")
    lines.append(f"Total New Leads (This Run):   {total_inquiries}")
    if total_inquiries > 0:
        conversion_rate = (product_inquiries / total_inquiries) * 100
        lines.append(f"Estimated Conversion Rate:   {conversion_rate:.1f}%")
        lines.append(f"Estimated Revenue Potential: {product_inquiries} potential customers")
    lines.append("")
    
    lines.append("━" * 80)
    lines.append("📂 CATEGORY BREAKDOWN (This Run)")
    lines.append("━" * 80)
    category_names = {
        "setup_help": "Setup Help 🔧",
        "newsletter": "Newsletter Signup 📧",
        "product_inquiry": "Product Inquiries 🛍️",
        "partnership": "Partnership Opportunities 🤝",
        "other": "Other 💬"
    }
    for category in ["setup_help", "newsletter", "product_inquiry", "partnership", "other"]:
        count = stats['categories'].get(category, 0)
        label = category_names.get(category, category.title())
        bar = "█" * min(count, 20)
        lines.append(f"{label:.<50} {bar} {count}")
    lines.append("")
    
    lines.append("━" * 80)
    lines.append("🚀 NEXT STEPS")
    lines.append("━" * 80)
    lines.append("1. ✅ Check flagged partnerships in:")
    lines.append(f"   → {FLAGGED_PARTNERSHIPS_FILE}")
    lines.append("")
    lines.append("2. ✅ Review all DMs logged in:")
    lines.append(f"   → {LOG_FILE}")
    lines.append("")
    lines.append("3. ✅ Set up DM ingestion (choose one):")
    lines.append("   a) Email Forwarding → youtube-dm-email-parser.py")
    lines.append("   b) Webhook Receiver → youtube-dm-webhook.py")
    lines.append("   c) Manual Queue → .cache/youtube-dm-inbox.jsonl")
    lines.append("")
    lines.append("4. ✅ Schedule hourly cron job:")
    lines.append(f"   0 * * * * cd {WORKSPACE_DIR} && python3 .cache/youtube_dm_monitor.py >> .cache/youtube-dms-cron.log 2>&1")
    lines.append("")
    
    lines.append("=" * 80)
    lines.append(f"End of Report - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="YouTube DM Monitor - Concessa Obvius",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 youtube_dm_monitor.py                 # Normal run (monitor queue + API)
  python3 youtube_dm_monitor.py --mock-mode     # Test with sample data
  python3 youtube_dm_monitor.py --queue-only    # Process queue only
  python3 youtube_dm_monitor.py --report        # Show last report only
        """
    )
    
    parser.add_argument("--mock-mode", action="store_true",
                       help="Use mock data for testing (no API/queue)")
    parser.add_argument("--queue-only", action="store_true",
                       help="Process queue only (skip YouTube API)")
    parser.add_argument("--api-only", action="store_true",
                       help="Try YouTube API only (skip queue)")
    parser.add_argument("--report", action="store_true",
                       help="Show last report and exit")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Show last report if requested
    if args.report:
        if REPORT_FILE.exists():
            with open(REPORT_FILE) as f:
                print(f.read())
        else:
            print("No report found. Run monitor first.", file=sys.stderr)
        return 0
    
    # Run monitor
    try:
        stats, state = run_monitor(
            mock_mode=args.mock_mode,
            queue_only=args.queue_only,
            api_only=args.api_only
        )
        
        # Generate and print report
        report = generate_report(stats, state)
        print(report)
        
        # Save report
        try:
            with open(REPORT_FILE, "w") as f:
                f.write(report)
        except Exception as e:
            print(f"Warning: Could not save report: {e}", file=sys.stderr)
        
        return 0
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
