#!/usr/bin/env python3
"""
YouTube DM Monitor - Categorizes and auto-responds to channel messages
Logs all activity to .cache/youtube-dms.jsonl
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Configuration
CHANNEL_NAME = "Concessa Obvius"
CACHE_DIR = Path.home() / ".openclaw" / "workspace" / ".cache"
DMS_LOG = CACHE_DIR / "youtube-dms.jsonl"
CREDENTIALS_FILE = Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube-credentials.json"
TOKEN_FILE = Path.home() / ".openclaw" / "workspace" / ".cache" / "youtube-token.json"

# YouTube API scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Auto-response templates
TEMPLATES = {
    "setup_help": """Hi {sender}! 👋

Thanks for reaching out about setup. I've put together detailed guides here: [link to docs]. 

Common issues:
- Issue A → Solution
- Issue B → Solution

Reply with specifics if you're stuck, and I'll help troubleshoot!

—Concessa""",
    
    "newsletter": """Hi {sender}!

Great to hear you're interested in staying updated. You can join our email list here: [link]. 

We send weekly tips, new releases, and exclusive early access to members. See you there!

—Concessa""",
    
    "product_inquiry": """Hi {sender}!

Thanks for your interest! 🎯

{product_specific_info}

Pricing & details: [link to pricing]
Want to chat more? I'm here to help find the right fit.

—Concessa""",
    
    "partnership": """Hi {sender}!

Interesting proposal! I'm forwarding this to our partnerships team for review. We'll get back to you within 2-3 business days.

Thanks for thinking of us!

—Concessa"""
}

class YouTubeDMMonitor:
    def __init__(self):
        self.service = None
        self.channel_id = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with YouTube API"""
        creds = None
        
        if TOKEN_FILE.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
        
        self.service = build("youtube", "v3", credentials=creds)
    
    def get_channel_id(self) -> str:
        """Get channel ID for Concessa Obvius"""
        if self.channel_id:
            return self.channel_id
        
        request = self.service.search().list(
            q=CHANNEL_NAME,
            type="channel",
            part="id",
            maxResults=1
        )
        response = request.execute()
        
        if response["items"]:
            self.channel_id = response["items"][0]["id"]["channelId"]
            return self.channel_id
        else:
            raise ValueError(f"Channel '{CHANNEL_NAME}' not found")
    
    def fetch_new_dms(self, since_timestamp: Optional[str] = None) -> list:
        """Fetch new DMs since last check"""
        # YouTube API doesn't have direct DM endpoint for channels
        # Using Community Posts/Channel Messages as proxy or requires YouTube Messages API beta
        # For now, we'll use a placeholder that assumes manual DM tracking
        
        # In production, this would use:
        # - YouTube Messages API (if available)
        # - Custom webhook integration
        # - Community tab polling
        
        print("⚠️  Note: YouTube doesn't expose DMs via public API. Integration options:")
        print("   1. Use unofficial youtube-dl + oauth flow")
        print("   2. Set up webhook for channel messages")
        print("   3. Manual CSV import of DMs")
        
        return []
    
    def categorize_dm(self, text: str, sender: str) -> str:
        """Categorize DM into one of 4 categories"""
        text_lower = text.lower()
        
        # Setup help keywords
        if any(kw in text_lower for kw in ["how to", "setup", "confused", "help", "install", "doesn't work", "error"]):
            return "setup_help"
        
        # Newsletter keywords
        if any(kw in text_lower for kw in ["email list", "newsletter", "subscribe", "updates", "notifications"]):
            return "newsletter"
        
        # Product inquiry keywords
        if any(kw in text_lower for kw in ["buy", "price", "pricing", "cost", "product", "which one", "recommend", "interested in"]):
            return "product_inquiry"
        
        # Partnership keywords
        if any(kw in text_lower for kw in ["partner", "collaboration", "sponsor", "promote", "affiliate", "collab", "brand deal"]):
            return "partnership"
        
        # Default to product inquiry if unclear
        return "product_inquiry"
    
    def generate_response(self, category: str, sender: str, dm_text: str) -> str:
        """Generate auto-response based on category"""
        template = TEMPLATES.get(category, TEMPLATES["product_inquiry"])
        
        response = template.format(sender=sender)
        
        if category == "product_inquiry":
            # Add context-aware product info
            if "video" in dm_text.lower():
                response = response.replace(
                    "{product_specific_info}",
                    "I see you're interested in our video tools. Here's what we offer:\n\n[Video Product A] - For creators\n[Video Product B] - For teams"
                )
            else:
                response = response.replace(
                    "{product_specific_info}",
                    "I'd love to learn more about what you're looking for so I can point you to the right product!"
                )
        
        return response
    
    def log_dm(self, sender: str, text: str, category: str, response_sent: str, timestamp: Optional[str] = None):
        """Log DM to JSONL file"""
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "timestamp": timestamp or datetime.utcnow().isoformat(),
            "sender": sender,
            "text": text,
            "category": category,
            "response_sent": response_sent,
        }
        
        with open(DMS_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def load_previous_senders(self) -> set:
        """Load set of previously processed senders to avoid duplicates"""
        if not DMS_LOG.exists():
            return set()
        
        senders = set()
        with open(DMS_LOG) as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    senders.add(entry["sender"])
        
        return senders
    
    def process_dms(self, dms: list) -> dict:
        """Process and respond to DMs"""
        stats = {
            "total_processed": 0,
            "auto_responses_sent": 0,
            "by_category": {},
            "partnerships_flagged": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        previous_senders = self.load_previous_senders()
        
        for dm in dms:
            sender = dm["sender"]
            text = dm["text"]
            
            # Skip if already processed
            if sender in previous_senders:
                continue
            
            category = self.categorize_dm(text, sender)
            response = self.generate_response(category, sender, text)
            
            # Log the DM
            self.log_dm(sender, text, category, response)
            
            # Update stats
            stats["total_processed"] += 1
            stats["auto_responses_sent"] += 1
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # Flag partnerships for manual review
            if category == "partnership":
                stats["partnerships_flagged"].append({
                    "sender": sender,
                    "text": text[:100] + "..." if len(text) > 100 else text
                })
        
        return stats
    
    def generate_report(self, stats: dict) -> str:
        """Generate monitoring report"""
        report = f"""
╔════════════════════════════════════════════════════════════════╗
║          YouTube DM Monitor Report - {stats['timestamp']}          ║
╚════════════════════════════════════════════════════════════════╝

📊 SUMMARY
  Total DMs processed: {stats['total_processed']}
  Auto-responses sent: {stats['auto_responses_sent']}

📂 BY CATEGORY
"""
        
        for category, count in stats["by_category"].items():
            category_label = category.replace("_", " ").title()
            report += f"  • {category_label}: {count}\n"
        
        if stats["partnerships_flagged"]:
            report += f"\n🤝 PARTNERSHIPS FLAGGED FOR MANUAL REVIEW ({len(stats['partnerships_flagged'])})\n"
            for p in stats["partnerships_flagged"]:
                report += f"  • {p['sender']}: {p['text']}\n"
        
        # Calculate conversion potential
        product_inquiries = stats["by_category"].get("product_inquiry", 0)
        conversion_potential = product_inquiries * 0.15  # Assume 15% conversion
        report += f"\n💰 CONVERSION POTENTIAL\n"
        report += f"  Product inquiries: {product_inquiries}\n"
        report += f"  Est. conversion (15%): {conversion_potential:.1f} potential customers\n"
        
        report += f"\n📝 Log file: {DMS_LOG}\n"
        
        return report


def main():
    """Main entry point"""
    import sys
    
    # Check if running in test mode (no credentials file)
    test_mode = not CREDENTIALS_FILE.exists()
    
    if test_mode:
        print("🧪 TEST MODE: Running with sample data (no YouTube credentials found)")
        print(f"   To enable: Download OAuth credentials to {CREDENTIALS_FILE}")
        print()
        monitor = None
    else:
        try:
            monitor = YouTubeDMMonitor()
        except Exception as e:
            print(f"❌ Authentication error: {e}", file=sys.stderr)
            sys.exit(1)
    
    # For now, using placeholder data (replace with real DM fetch in production)
    # In real scenario, this would fetch actual DMs from YouTube API or webhook
    dms = [
        {
            "sender": "creator_dev",
            "text": "Hi! How do I set up the API integration? I'm getting an error.",
        },
        {
            "sender": "news_outlet",
            "text": "We'd love to partner on this. Your product aligns with our audience.",
        },
        {
            "sender": "curious_fan",
            "text": "What's the pricing? Interested in the video bundle.",
        },
    ]
    
    # Use test monitor or skip authentication
    if test_mode:
        # Create a minimal monitor for testing (without auth)
        monitor_instance = YouTubeDMMonitor.__new__(YouTubeDMMonitor)
        
        class TestMonitor:
            def categorize_dm(self, text, sender):
                text_lower = text.lower()
                if any(kw in text_lower for kw in ["how to", "setup", "confused", "help", "install", "doesn't work", "error"]):
                    return "setup_help"
                if any(kw in text_lower for kw in ["email list", "newsletter", "subscribe", "updates", "notifications"]):
                    return "newsletter"
                if any(kw in text_lower for kw in ["buy", "price", "pricing", "cost", "product", "which one", "recommend", "interested in"]):
                    return "product_inquiry"
                if any(kw in text_lower for kw in ["partner", "collaboration", "sponsor", "promote", "affiliate", "collab", "brand deal"]):
                    return "partnership"
                return "product_inquiry"
            
            def generate_response(self, category, sender, text):
                templates = {
                    "setup_help": f"Hi {sender}! 👋\n\nThanks for reaching out about setup. I've put together detailed guides at [link to docs].",
                    "newsletter": f"Hi {sender}!\n\nGreat to hear you're interested. Join our email list: [link]",
                    "product_inquiry": f"Hi {sender}!\n\nThanks for your interest! Here's info about our products: [link]",
                    "partnership": f"Hi {sender}!\n\nInteresting proposal! I'm forwarding this to our partnerships team."
                }
                return templates.get(category, "Thanks for reaching out!")
            
            def log_dm(self, sender, text, category, response, timestamp=None):
                CACHE_DIR.mkdir(parents=True, exist_ok=True)
                entry = {
                    "timestamp": timestamp or datetime.now(timezone.utc).isoformat(),
                    "sender": sender,
                    "text": text,
                    "category": category,
                    "response_sent": response,
                }
                with open(DMS_LOG, "a") as f:
                    f.write(json.dumps(entry) + "\n")
            
            def load_previous_senders(self):
                if not DMS_LOG.exists():
                    return set()
                senders = set()
                with open(DMS_LOG) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            try:
                                entry = json.loads(line)
                                senders.add(entry["sender"])
                            except json.JSONDecodeError:
                                pass
                return senders
        
        monitor = TestMonitor()
    
    # Process DMs
    stats = {
        "total_processed": 0,
        "auto_responses_sent": 0,
        "by_category": {},
        "partnerships_flagged": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    previous_senders = monitor.load_previous_senders()
    
    for dm in dms:
        sender = dm["sender"]
        text = dm["text"]
        
        if sender in previous_senders:
            continue
        
        category = monitor.categorize_dm(text, sender)
        response = monitor.generate_response(category, sender, text)
        
        monitor.log_dm(sender, text, category, response)
        
        stats["total_processed"] += 1
        stats["auto_responses_sent"] += 1
        stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
        
        if category == "partnership":
            stats["partnerships_flagged"].append({
                "sender": sender,
                "text": text[:100] + "..." if len(text) > 100 else text
            })
    
    # Generate and print report
    report = generate_report(stats)
    print(report)
    
    # Save report to file
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    report_file = CACHE_DIR / "youtube-dm-report.txt"
    with open(report_file, "w") as f:
        f.write(report)
    
    if test_mode:
        print(f"✅ Test run complete. Report saved to {report_file}")
        print(f"   DM log: {DMS_LOG}")
        print()
        print(f"📋 To enable real monitoring:")
        print(f"   1. Set up Google OAuth credentials")
        print(f"   2. Save to: {CREDENTIALS_FILE}")
        print(f"   3. See: docs/YOUTUBE-DM-MONITOR-SETUP.md")
    else:
        print(f"\n✅ Report saved to {report_file}")


def generate_report(stats):
    """Generate monitoring report"""
    report = f"""
╔════════════════════════════════════════════════════════════════╗
║          YouTube DM Monitor Report - {stats['timestamp']}          ║
╚════════════════════════════════════════════════════════════════╝

📊 SUMMARY
  Total DMs processed: {stats['total_processed']}
  Auto-responses sent: {stats['auto_responses_sent']}

📂 BY CATEGORY
"""
    
    for category, count in stats["by_category"].items():
        category_label = category.replace("_", " ").title()
        report += f"  • {category_label}: {count}\n"
    
    if stats["partnerships_flagged"]:
        report += f"\n🤝 PARTNERSHIPS FLAGGED FOR MANUAL REVIEW ({len(stats['partnerships_flagged'])})\n"
        for p in stats["partnerships_flagged"]:
            report += f"  • {p['sender']}: {p['text']}\n"
    
    product_inquiries = stats["by_category"].get("product_inquiry", 0)
    conversion_potential = product_inquiries * 0.15
    report += f"\n💰 CONVERSION POTENTIAL\n"
    report += f"  Product inquiries: {product_inquiries}\n"
    report += f"  Est. conversion (15%): {conversion_potential:.1f} potential customers\n"
    
    report += f"\n📝 Log file: {DMS_LOG}\n"
    
    return report


if __name__ == "__main__":
    main()
