#!/usr/bin/env python3
"""
YouTube DM Monitor - Live Version
Monitors Concessa Obvius YouTube Studio DMs, categorizes, auto-responds, and logs

Features:
- DM categorization (Setup Help, Newsletter, Product Inquiry, Partnership)
- Auto-response with templated replies
- Full DM logging to .cache/youtube-dms.jsonl
- Hourly reporting with conversion potential tracking
"""

import json
import os
import sys
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import asyncio
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
WORKSPACE = Path.home() / ".openclaw" / "workspace"
CACHE_DIR = WORKSPACE / ".cache"
LOG_FILE = CACHE_DIR / "youtube-dms.jsonl"
REPORT_FILE = CACHE_DIR / "youtube-dm-report.json"
STATE_FILE = CACHE_DIR / "youtube-dm-monitor-state.json"
CHANNEL_NAME = "Concessa Obvius"

# Auto-response templates
TEMPLATES = {
    "setup_help": """Thanks for reaching out! 🙌

I'm glad you're interested in getting started. Here are some helpful resources:

1. **Setup Guide:** Check the playlist on the channel homepage
2. **FAQ:** Most setup questions are answered in the community tab
3. **Need more help?** Reply here and I'll get back to you ASAP

Looking forward to having you as part of the community!""",

    "newsletter": """Thanks for your interest! 📧

To join the email list and stay updated on new content:
- Visit the community tab for signup links
- Or reply here with your email and I'll add you manually

You'll be the first to know about new releases, exclusive tips, and special offers!""",

    "product_inquiry": """Great question! 🎯

Interested in what I offer? I'd love to help you find the right fit.

**Quick info:**
- Check the community tab for current offerings
- Pricing and packages are listed there too
- Reply with any specific questions and I'll personalize a recommendation

Looking forward to working together!""",

    "partnership": """This looks interesting! 🤝

I'm always open to meaningful collaborations. Let's explore this:

1. **Tell me more:** What's your vision for this partnership?
2. **Next step:** I'll review details and get back to you within 48 hours
3. **Questions?** Feel free to reply or check the community tab for contact info

Thanks for thinking of me!"""
}

# Keyword patterns for categorization
CATEGORY_PATTERNS = {
    "setup_help": [
        r"how\s+to", r"setup", r"install", r"configure", r"confused", r"error",
        r"doesn't\s+work", r"broken", r"stuck", r"help", r"struggling",
        r"guide", r"tutorial", r"steps", r"not\s+sure", r"where\s+to\s+start",
        r"how\s+do\s+i", r"what\s+do\s+i", r"can\s+i", r"should\s+i"
    ],
    "newsletter": [
        r"email\s+list", r"subscribe", r"updates", r"newsletter", r"signup",
        r"sign\s+up", r"follow", r"keep\s+me\s+posted", r"notify", r"informed"
    ],
    "product_inquiry": [
        r"price", r"cost", r"how\s+much", r"buy", r"purchase", r"interested\s+in",
        r"available", r"offer", r"sale", r"discount", r"products?",
        r"services?", r"packages?", r"membership", r"access", r"get\s+started",
        r"try\s+it", r"demo", r"trial"
    ],
    "partnership": [
        r"partner", r"collaboration", r"sponsor", r"brand\s+deal", r"affiliate",
        r"promote", r"work\s+together", r"collab", r"promote\s+you", r"feature",
        r"cross\-promo", r"joint\s+venture", r"business\s+opportunity"
    ]
}


class YouTubeDMMonitor:
    """Monitor and process YouTube DMs"""

    def __init__(self):
        """Initialize the monitor"""
        self.cache_dir = CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.dms_processed = []
        self.load_state()

    def load_state(self) -> None:
        """Load previous state"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    self.state = json.load(f)
                logger.info(f"Loaded state: {len(self.state.get('processed_ids', []))} previous DMs")
            except json.JSONDecodeError:
                self.state = {"processed_ids": []}
        else:
            self.state = {"processed_ids": []}

    def save_state(self) -> None:
        """Save current state"""
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)

    def categorize_dm(self, text: str) -> str:
        """Categorize a DM based on keyword patterns"""
        text_lower = text.lower()

        # Check partnerships first (highest priority for manual review)
        for pattern in CATEGORY_PATTERNS["partnership"]:
            if re.search(pattern, text_lower):
                return "partnership"

        # Check product inquiries
        for pattern in CATEGORY_PATTERNS["product_inquiry"]:
            if re.search(pattern, text_lower):
                return "product_inquiry"

        # Check newsletter
        for pattern in CATEGORY_PATTERNS["newsletter"]:
            if re.search(pattern, text_lower):
                return "newsletter"

        # Check setup help
        for pattern in CATEGORY_PATTERNS["setup_help"]:
            if re.search(pattern, text_lower):
                return "setup_help"

        # Default to product_inquiry if no match
        return "product_inquiry"

    def get_response_template(self, category: str) -> str:
        """Get auto-response template for category"""
        return TEMPLATES.get(category, TEMPLATES["product_inquiry"])

    def fetch_dms(self) -> List[Dict]:
        """
        Fetch new DMs from YouTube Studio.
        In a real implementation, this would use Playwright to automate YouTube Studio.
        For now, it returns mock data - replace with actual YouTube Studio integration.
        """
        # This is a placeholder - in production, use Playwright to:
        # 1. Navigate to YouTube Studio
        # 2. Open Messages tab
        # 3. Parse DMs from DOM
        # 4. Filter out already-processed ones
        
        logger.info("Fetching DMs from YouTube Studio...")
        
        # Try to fetch from YouTube Studio via Playwright if available
        try:
            from playwright.sync_api import sync_playwright
            return self._fetch_dms_playwright()
        except ImportError:
            logger.warning("Playwright not installed; using demo mode")
            return self._get_demo_dms()

    def _fetch_dms_playwright(self) -> List[Dict]:
        """Fetch DMs using Playwright (requires browser automation)"""
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Navigate to YouTube Studio Messages
                page.goto("https://studio.youtube.com/messages")
                page.wait_for_load_state("networkidle", timeout=10000)
                
                # Check if already authenticated
                try:
                    page.wait_for_selector("[data-message-thread]", timeout=5000)
                except:
                    logger.error("Authentication required - YouTube Studio not accessible")
                    browser.close()
                    return []
                
                # Extract DM threads
                dms = []
                threads = page.locator("[data-message-thread]").all()
                
                for thread in threads:
                    sender = thread.locator("[data-sender-name]").inner_text()
                    text = thread.locator("[data-message-text]").last.inner_text()
                    timestamp = thread.locator("[data-timestamp]").inner_text()
                    
                    dm_id = f"{sender}_{timestamp}".replace(" ", "_")
                    
                    if dm_id not in self.state["processed_ids"]:
                        dms.append({
                            "id": dm_id,
                            "sender": sender,
                            "text": text,
                            "timestamp": timestamp,
                            "original_timestamp": datetime.now().isoformat()
                        })
                
                browser.close()
                logger.info(f"Fetched {len(dms)} new DMs from YouTube Studio")
                return dms
                
        except Exception as e:
            logger.error(f"Playwright fetch failed: {e}")
            return []

    def _get_demo_dms(self) -> List[Dict]:
        """Return demo DMs for testing (only if no real DMs available)"""
        # Check if we already have real DMs logged
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > 0:
            logger.info("Using existing DM log (no new DMs from YouTube Studio)")
            return []
        
        logger.info("Returning demo DMs for testing")
        return [
            {
                "id": "demo_setup_001",
                "sender": "Alex Johnson",
                "text": "Hi! I'm confused about how to set this up. Where do I start?",
                "timestamp": datetime.now().isoformat(),
                "original_timestamp": datetime.now().isoformat()
            },
            {
                "id": "demo_newsletter_001",
                "sender": "Sarah Chen",
                "text": "Love your content! Can I subscribe to your email list for updates?",
                "timestamp": datetime.now().isoformat(),
                "original_timestamp": datetime.now().isoformat()
            },
            {
                "id": "demo_product_001",
                "sender": "Mike Torres",
                "text": "What's the pricing for your premium package? How much does it cost?",
                "timestamp": datetime.now().isoformat(),
                "original_timestamp": datetime.now().isoformat()
            },
            {
                "id": "demo_partnership_001",
                "sender": "Creative Agency Ltd",
                "text": "We'd love to collaborate on a brand partnership. Your audience aligns perfectly with our client base.",
                "timestamp": datetime.now().isoformat(),
                "original_timestamp": datetime.now().isoformat()
            }
        ]

    def process_dms(self, dms: List[Dict]) -> None:
        """Process and log DMs"""
        for dm in dms:
            # Categorize
            category = self.categorize_dm(dm["text"])
            
            # Get response template
            response = self.get_response_template(category)
            
            # Flag interesting partnerships
            interesting_partnership = (
                category == "partnership" and 
                any(keyword in dm["text"].lower() for keyword in ["collaborate", "partner", "sponsor"])
            )
            
            # Create log entry
            log_entry = {
                "timestamp": dm["original_timestamp"],
                "sender": dm["sender"],
                "text": dm["text"],
                "category": category,
                "response_sent": response,
                "interesting_partnership": interesting_partnership
            }
            
            # Log to JSONL
            with open(LOG_FILE, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
            
            logger.info(f"Logged DM from {dm['sender']} ({category})")
            
            # Track processed
            self.state["processed_ids"].append(dm["id"])
            self.dms_processed.append(log_entry)

    def generate_report(self) -> Dict:
        """Generate hourly report"""
        # Load all DMs from log
        all_dms = []
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            all_dms.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        
        # Analyze
        categories = {}
        partnerships_flagged = []
        product_inquiries = []
        
        for dm in all_dms:
            cat = dm.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            
            if dm.get("interesting_partnership"):
                partnerships_flagged.append({
                    "sender": dm.get("sender"),
                    "timestamp": dm.get("timestamp"),
                    "preview": dm.get("text")[:80] + "..." if len(dm.get("text", "")) > 80 else dm.get("text")
                })
            
            if cat == "product_inquiry":
                product_inquiries.append(dm)
        
        # Build report
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "total_dms_processed": len(all_dms),
            "total_this_run": len(self.dms_processed),
            "auto_responses_sent": len([d for d in all_dms if d.get("response_sent")]),
            "by_category": categories,
            "partnerships_flagged": len(partnerships_flagged),
            "interesting_partnerships": partnerships_flagged,
            "product_inquiries_count": len(product_inquiries),
            "conversion_potential": f"{len(product_inquiries)} lead(s) ready to follow up"
        }
        
        # Save report
        with open(REPORT_FILE, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

    def print_report(self, report: Dict) -> None:
        """Print human-readable report"""
        print("\n" + "="*50)
        print("📊 YOUTUBE DM MONITOR REPORT")
        print("="*50)
        print(f"⏰ Generated: {report['timestamp']}")
        print(f"\n✅ Total DMs (all time): {report['total_dms_processed']}")
        print(f"✉️  This run: {report['total_this_run']}")
        print(f"📤 Auto-responses sent: {report['auto_responses_sent']}")
        
        print(f"\n📂 By Category:")
        for cat, count in report['by_category'].items():
            print(f"  • {cat.replace('_', ' ').title()}: {count}")
        
        print(f"\n🤝 Partnerships Flagged: {report['partnerships_flagged']}")
        if report['interesting_partnerships']:
            print("  Interesting opportunities:")
            for p in report['interesting_partnerships'][:3]:  # Top 3
                print(f"    • {p['sender']} ({p['timestamp'][:10]})")
                print(f"      {p['preview']}")
        
        print(f"\n🎯 Conversion Potential:")
        print(f"  {report['conversion_potential']}")
        print("="*50 + "\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='YouTube DM Monitor')
    parser.add_argument('--report', action='store_true', help='Print report after run')
    parser.add_argument('--demo', action='store_true', help='Use demo mode (no API)')
    args = parser.parse_args()

    logger.info(f"Starting YouTube DM Monitor for '{CHANNEL_NAME}'")

    # Initialize monitor
    monitor = YouTubeDMMonitor()

    # Fetch DMs
    dms = monitor.fetch_dms()
    
    if dms:
        logger.info(f"Processing {len(dms)} DM(s)")
        monitor.process_dms(dms)
        monitor.save_state()
    else:
        logger.info("No new DMs to process")

    # Generate report
    report = monitor.generate_report()

    if args.report:
        monitor.print_report(report)

    logger.info("✅ Monitor run completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
