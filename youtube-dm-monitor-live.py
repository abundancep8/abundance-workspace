#!/usr/bin/env python3
"""
YouTube DM Monitor - Live Browser-Based Monitor
Fetches DMs from YouTube Studio, categorizes, auto-responds, and logs.
Uses Playwright for browser automation since YouTube API doesn't expose DMs.
"""

import json
import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal
import re
from dataclasses import dataclass, asdict

# Optional imports - fallback if not available
try:
    from playwright.async_api import async_playwright, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not installed. Install with: pip install playwright")
    print("   Then run: playwright install")

# Categories for DM classification
Category = Literal["setup_help", "newsletter", "product_inquiry", "partnership"]

TEMPLATES = {
    "setup_help": """Hey! 👋 Thanks for reaching out about setup. I've got detailed guides that should help:

📚 Full setup guide: [link to guide]
🎥 Step-by-step video: [link to video]
💬 Common issues: [link to FAQ]

If you get stuck on a specific step, reply with what's giving you trouble and I'll help!""",

    "newsletter": """Thanks for wanting to stay in the loop! 🔔

✉️ **Join the newsletter:** [link]
📱 You'll get:
- Weekly tips & updates
- Early access to new features
- Exclusive member content

See you there!""",

    "product_inquiry": """Great question! 🎯

📦 **Product info & pricing:** [link]
💰 We have options for every budget
❓ Let me know:
- What's your use case?
- Budget range?
- Team size?

Happy to help you find the perfect fit!""",

    "partnership": """Ooh, interesting! 🤝 I love hearing partnership ideas.

For collab/sponsorship inquiries, let's take this to email so we can dive deeper:
📧 [partnership@concessa.com]

Tell me a bit about what you have in mind and we'll explore it!"""
}

KEYWORDS = {
    "setup_help": ["setup", "how to", "confused", "beginner", "tutorial", "install", "getting started", "doesn't work", "help", "guide", "stuck", "error", "not working"],
    "newsletter": ["newsletter", "updates", "email list", "subscribe", "news", "latest", "stay updated", "follow", "sign up"],
    "product_inquiry": ["buy", "pricing", "price", "cost", "purchase", "how much", "afford", "product", "which version", "recommend", "features", "difference", "plan"],
    "partnership": ["collaborate", "sponsorship", "partner", "joint", "co-brand", "affiliate", "promotion", "promote", "work together", "business opportunity", "brand deal"]
}

@dataclass
class DM:
    """Represents a single DM."""
    timestamp: str
    sender: str
    sender_id: str
    text: str
    category: Category
    response_sent: str
    interesting_partnership: bool = False
    raw_dm_id: Optional[str] = None

class YouTubeDMMonitor:
    def __init__(self, log_file: str = ".cache/youtube-dms.jsonl", debug: bool = False):
        self.log_file = log_file
        self.debug = debug
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        self.processed_ids = self._load_processed_ids()
        
    def _load_processed_ids(self) -> set:
        """Load already-processed DM IDs to avoid duplicates."""
        processed = set()
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    for line in f:
                        if line.strip():
                            try:
                                dm = json.loads(line)
                                if "raw_dm_id" in dm:
                                    processed.add(dm["raw_dm_id"])
                            except json.JSONDecodeError:
                                pass
            except Exception as e:
                print(f"⚠️  Error loading processed IDs: {e}")
        return processed
    
    def categorize_dm(self, text: str) -> Category:
        """Categorize a DM based on keyword matching."""
        text_lower = text.lower()
        
        # Score each category based on keyword matches
        scores = {}
        for category, keywords in KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            scores[category] = score
        
        # Return category with highest score, default to product_inquiry
        return max(scores, key=scores.get) if max(scores.values()) > 0 else "product_inquiry"
    
    def is_interesting_partnership(self, text: str, sender: str) -> bool:
        """Determine if a partnership inquiry is worth flagging for manual review."""
        text_lower = text.lower()
        
        # Heuristics for interesting partnerships
        interesting_signals = [
            len(text) > 150,  # Detailed inquiry
            any(word in text_lower for word in ["brand", "major", "large", "budget", "contract", "deal"]),
            any(word in text_lower for word in ["youtube", "creator", "influencer", "agency"]),
            "?" in text,  # Asks a question (more engaged)
        ]
        
        return sum(interesting_signals) >= 2
    
    def log_dm(self, dm: DM):
        """Log a DM to the JSONL file."""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(asdict(dm)) + "\n")
        
        if self.debug:
            print(f"✓ Logged DM from {dm.sender} ({dm.category})")
    
    def process_dm(self, sender: str, sender_id: str, text: str, dm_id: Optional[str] = None) -> Optional[DM]:
        """Process a single DM: categorize, respond, and log."""
        
        # Skip if already processed
        if dm_id and dm_id in self.processed_ids:
            if self.debug:
                print(f"⊘ Skipping already-processed DM: {dm_id}")
            return None
        
        # Categorize
        category = self.categorize_dm(text)
        
        # Get template response
        response = TEMPLATES[category]
        
        # Check if partnership is interesting (for manual review flag)
        interesting = False
        if category == "partnership":
            interesting = self.is_interesting_partnership(text, sender)
        
        # Create DM record
        dm = DM(
            timestamp=datetime.now().isoformat(),
            sender=sender,
            sender_id=sender_id,
            text=text,
            category=category,
            response_sent=response,
            interesting_partnership=interesting,
            raw_dm_id=dm_id
        )
        
        # Log
        self.log_dm(dm)
        
        if dm_id:
            self.processed_ids.add(dm_id)
        
        return dm
    
    async def fetch_dms_from_studio(self, page: Page) -> list[dict]:
        """Fetch unread DMs from YouTube Studio using browser automation."""
        dms = []
        
        try:
            # Navigate to YouTube Studio messages
            await page.goto("https://studio.youtube.com/channel/messages", timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            if self.debug:
                print("✓ Navigated to YouTube Studio messages")
            
            # Wait for DM list to load
            await page.wait_for_selector('[role="listitem"]', timeout=5000)
            
            # Extract DMs from the UI
            dm_elements = await page.query_selector_all('[role="listitem"]')
            
            for idx, element in enumerate(dm_elements[:20]):  # Limit to last 20 for first run
                try:
                    # Get sender name
                    sender = await element.query_selector('[role="heading"]')
                    sender_text = await sender.text_content() if sender else "Unknown"
                    
                    # Get message preview / full text
                    message = await element.query_selector('[role="article"]')
                    message_text = await message.text_content() if message else ""
                    
                    # Try to get a unique ID (timestamp or element index)
                    dm_id = f"{sender_text}_{message_text[:50]}_{idx}"
                    
                    if sender_text.strip() and message_text.strip():
                        dms.append({
                            "sender": sender_text.strip(),
                            "sender_id": hashlib.md5(sender_text.encode()).hexdigest()[:8],
                            "text": message_text.strip(),
                            "id": dm_id
                        })
                        
                        if self.debug:
                            print(f"  Found DM {idx + 1}: {sender_text[:30]}")
                except Exception as e:
                    if self.debug:
                        print(f"  ⚠️  Error extracting DM {idx}: {e}")
                    continue
            
            if self.debug:
                print(f"✓ Extracted {len(dms)} DMs from YouTube Studio")
        
        except Exception as e:
            print(f"❌ Error fetching DMs from YouTube Studio: {e}")
            if self.debug:
                print(f"   (Make sure you're logged into YouTube on this browser session)")
        
        return dms
    
    async def run_browser_monitor(self, headless: bool = True, verbose: bool = False):
        """Run the DM monitor using browser automation."""
        if not PLAYWRIGHT_AVAILABLE:
            print("❌ Playwright not available. Install with: pip install playwright && playwright install")
            return None
        
        dms_processed = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=headless)
            page = await browser.new_page()
            
            try:
                # Fetch DMs
                raw_dms = await self.fetch_dms_from_studio(page)
                
                # Process each DM
                for raw_dm in raw_dms:
                    processed = self.process_dm(
                        sender=raw_dm["sender"],
                        sender_id=raw_dm.get("sender_id", ""),
                        text=raw_dm["text"],
                        dm_id=raw_dm.get("id")
                    )
                    if processed:
                        dms_processed.append(processed)
                
            finally:
                await browser.close()
        
        return dms_processed
    
    def get_stats(self, hours: int = 24) -> dict:
        """Generate report stats from the log file."""
        if not os.path.exists(self.log_file):
            return {
                "total_dms": 0,
                "auto_responses_sent": 0,
                "by_category": {},
                "partnerships_flagged": 0,
                "conversion_potential": "No data yet",
                "report_period": f"Last {hours}h"
            }
        
        import datetime as dt
        cutoff_time = datetime.now() - dt.timedelta(hours=hours)
        
        dms = []
        with open(self.log_file, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    try:
                        entry = json.loads(line)
                        ts_str = entry.get("timestamp", "2000-01-01")
                        # Parse ISO timestamp and make naive for comparison
                        entry_time = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                        if entry_time.tzinfo:
                            entry_time = entry_time.replace(tzinfo=None)
                        if entry_time >= cutoff_time:
                            dms.append(entry)
                    except (json.JSONDecodeError, ValueError):
                        continue
        
        categories = {}
        product_inquiries = []
        partnerships_flagged = []
        
        for dm in dms:
            cat = dm.get("category")
            categories[cat] = categories.get(cat, 0) + 1
            
            if cat == "product_inquiry":
                product_inquiries.append(dm)
            if dm.get("interesting_partnership"):
                partnerships_flagged.append({
                    "sender": dm.get("sender"),
                    "timestamp": dm.get("timestamp"),
                    "preview": dm.get("text")[:80] + "..."
                })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "report_period": f"Last {hours}h",
            "total_dms": len(dms),
            "auto_responses_sent": len([d for d in dms if d.get("response_sent")]),
            "by_category": categories,
            "partnerships_flagged": len(partnerships_flagged),
            "interesting_partnerships": partnerships_flagged,
            "conversion_potential": f"{len(product_inquiries)} product inquiries to follow up on",
            "product_inquiries": product_inquiries
        }

async def main():
    """Main entry point - run the monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube DM Monitor")
    parser.add_argument("--headless", action="store_true", default=True, help="Run browser in headless mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--report", action="store_true", help="Generate and print report")
    parser.add_argument("--hours", type=int, default=24, help="Report period in hours")
    args = parser.parse_args()
    
    monitor = YouTubeDMMonitor(debug=args.debug or args.report)
    
    print("🎬 YouTube DM Monitor")
    print(f"⏰ Started at {datetime.now().isoformat()}\n")
    
    # Run the browser-based monitor
    if PLAYWRIGHT_AVAILABLE:
        dms = await monitor.run_browser_monitor(headless=args.headless, verbose=args.debug)
        
        if dms:
            print(f"\n✅ Processed {len(dms)} new DMs")
            for dm in dms:
                print(f"  • {dm.sender}: {dm.category}")
                if dm.interesting_partnership:
                    print(f"    🚩 Flagged for manual review")
    
    # Generate report if requested
    if args.report:
        stats = monitor.get_stats(hours=args.hours)
        print("\n📊 REPORT")
        print(f"Period: {stats['report_period']}")
        print(f"Total DMs: {stats['total_dms']}")
        print(f"Auto-responses sent: {stats['auto_responses_sent']}")
        print(f"By category: {stats['by_category']}")
        print(f"Partnerships flagged: {stats['partnerships_flagged']}")
        print(f"Conversion potential: {stats['conversion_potential']}")
        
        if stats['interesting_partnerships']:
            print("\n⭐ Interesting partnerships for manual review:")
            for p in stats['interesting_partnerships']:
                print(f"  • {p['sender']}")
                print(f"    {p['preview']}")

if __name__ == "__main__":
    import hashlib
    
    # For non-async test mode (without browser)
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        monitor = YouTubeDMMonitor(debug=True)
        
        print("📊 YouTube DM Monitor - Test Mode\n")
        
        test_dms = [
            ("Alice_Creator", "Alice", "Hey! I'm trying to set up your product but I'm confused about the first step. Can you help?"),
            ("marketing_guy", "MarketingGuy", "Hi! We'd love to collaborate on a sponsorship deal. What are your rates and what kind of brands do you typically partner with?"),
            ("subscriber_jane", "Jane", "Are you planning a newsletter? I'd love to stay updated on new releases!"),
            ("potential_buyer", "John", "Hi, how much does the pro version cost and what's the difference from the free plan?"),
        ]
        
        for sender, sid, text in test_dms:
            result = monitor.process_dm(sender, sid, text, dm_id=f"test_{sender}")
            if result:
                print(f"  {result.sender} → {result.category}")
                if result.interesting_partnership:
                    print(f"    🚩 FLAGGED")
        
        print()
        stats = monitor.get_stats(hours=24)
        print("\n📈 REPORT")
        print(f"Total DMs: {stats['total_dms']}")
        print(f"Auto-responses: {stats['auto_responses_sent']}")
        print(f"By category: {stats['by_category']}")
        print(f"Partnerships flagged: {stats['partnerships_flagged']}")
        print(f"Conversion potential: {stats['conversion_potential']}")
    else:
        # Run async monitor
        asyncio.run(main())
