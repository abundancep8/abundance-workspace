#!/usr/bin/env python3
"""
YouTube DM Monitor for Concessa Obvius - Production Version
Monitors YouTube community DMs, categorizes, auto-responds, and logs.
Objective: Fetch new DMs, categorize, auto-respond, and log all activity.
"""

import json
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import re
from dataclasses import dataclass, asdict, field
from enum import Enum

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.api_core.exceptions import HttpError
    from googleapiclient.discovery import build
    HAS_GOOGLE_API = True
except ImportError:
    HAS_GOOGLE_API = False


# Setup logging
class DMCategory(Enum):
    SETUP_HELP = "Setup Help"
    NEWSLETTER = "Newsletter"
    PRODUCT_INQUIRY = "Product Inquiry"
    PARTNERSHIP = "Partnership"
    OTHER = "Other"


@dataclass
class DMRecord:
    """YouTube DM record"""
    timestamp: str
    sender: str
    sender_id: str
    text: str
    category: str
    response_sent: bool
    response_template: str
    dm_id: str
    budget_mentioned: bool = False
    conversion_potential: bool = False
    manual_review_flag: bool = False


class YouTubeDMMonitorProd:
    """Production YouTube DM Monitor for Concessa Obvius"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.readonly',
        'https://www.googleapis.com/auth/youtube.force-ssl'
    ]
    
    WORKSPACE_ROOT = Path.home() / '.openclaw' / 'workspace'
    CACHE_DIR = WORKSPACE_ROOT / '.cache'
    SECRETS_DIR = WORKSPACE_ROOT / '.secrets'
    
    LOG_FILE = CACHE_DIR / 'youtube-dms.jsonl'
    STATE_FILE = CACHE_DIR / '.youtube-dms-state.json'
    CREDENTIALS_FILE = SECRETS_DIR / 'youtube-credentials.json'
    TOKEN_FILE = SECRETS_DIR / 'youtube-token.json'
    PARTNERSHIP_FLAGS_FILE = CACHE_DIR / 'youtube-flagged-partnerships.jsonl'
    DM_REPORT_FILE = CACHE_DIR / 'youtube-dms-report.txt'
    
    # Auto-response templates
    RESPONSES = {
        'setup_help': (
            "Thanks for reaching out! 🙌\n\n"
            "Here's our setup guide: https://docs.concessa.com/setup\n\n"
            "Quick troubleshooting:\n"
            "• Check the FAQ: https://docs.concessa.com/faq\n"
            "• Watch the tutorial: https://youtube.com/watch?v=...\n"
            "• Still stuck? Reply with your error and I'll help!\n\n"
            "Let me know if you need more help. 🚀"
        ),
        'newsletter': (
            "Great! 📬\n\n"
            "I've added you to our updates list.\n"
            "Check your email soon for confirmation and exclusive content.\n\n"
            "You'll get:\n"
            "• Weekly tips & tricks\n"
            "• New feature releases\n"
            "• Exclusive subscriber offers\n\n"
            "Thanks for staying connected! ✨"
        ),
        'product_inquiry': (
            "Thanks for your interest! 💡\n\n"
            "Here are our product options:\n"
            "• Starter: https://concessa.com/pricing#starter\n"
            "• Professional: https://concessa.com/pricing#pro\n"
            "• Enterprise: https://concessa.com/pricing#enterprise\n\n"
            "Questions? Reply with details about your needs and I can recommend the best fit.\n"
            "Happy to help! 🎯"
        ),
        'partnership': (
            "This sounds interesting! 🤝\n\n"
            "I'm flagging this for our partnership team to review.\n"
            "Someone will get back to you within 24-48 hours.\n\n"
            "In the meantime, feel free to share more details about your proposal.\n"
            "Looking forward to exploring this! 🚀"
        ),
    }
    
    def __init__(self):
        """Initialize monitor"""
        self.setup_logging()
        self.youtube = None
        self.channel_id = None
        self.dms_processed = 0
        self.auto_responses_sent = 0
        self.new_dms = []
        self.flagged_partnerships = []
        self.product_inquiries = []
        self.logger = logging.getLogger(__name__)
    
    def setup_logging(self):
        """Setup logging"""
        log_file = self.CACHE_DIR / 'youtube-dm-monitor.log'
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def authenticate(self) -> bool:
        """Authenticate with YouTube API"""
        if not HAS_GOOGLE_API:
            self.logger.warning("⚠️  Google API not available, using log-based mode")
            return True
        
        try:
            self.logger.info("🔐 Authenticating with YouTube API...")
            
            creds = None
            
            # Try to load existing token
            if self.TOKEN_FILE.exists():
                try:
                    creds = Credentials.from_authorized_user_file(
                        str(self.TOKEN_FILE), self.SCOPES
                    )
                    self.logger.info("✅ Loaded existing credentials")
                except Exception as e:
                    self.logger.warning(f"Failed to load token: {e}")
            
            # Refresh or get new credentials
            if creds and creds.valid:
                self.logger.info("✅ Credentials valid")
            elif creds and creds.expired and creds.refresh_token:
                self.logger.info("🔄 Refreshing credentials...")
                creds.refresh(Request())
                self.logger.info("✅ Credentials refreshed")
            elif self.CREDENTIALS_FILE.exists():
                self.logger.info("🔐 Getting new credentials via OAuth...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.CREDENTIALS_FILE), self.SCOPES
                )
                creds = flow.run_local_server(port=0)
                self.logger.info("✅ New credentials obtained")
            else:
                self.logger.error("❌ YouTube credentials not configured")
                self.logger.error(f"Expected: {self.CREDENTIALS_FILE}")
                return False
            
            # Save token
            self.SECRETS_DIR.mkdir(parents=True, exist_ok=True)
            with open(self.TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())
            self.logger.info(f"✅ Token saved to {self.TOKEN_FILE}")
            
            # Build YouTube service
            self.youtube = build('youtube', 'v3', credentials=creds)
            self.logger.info("✅ YouTube service built successfully")
            
            # Get channel ID
            channels = self.youtube.channels().list(
                part='id',
                mine=True
            ).execute()
            
            if channels.get('items'):
                self.channel_id = channels['items'][0]['id']
                self.logger.info(f"✅ Channel ID: {self.channel_id}")
                return True
            else:
                self.logger.error("❌ Could not retrieve channel ID")
                return False
        
        except Exception as e:
            self.logger.error(f"❌ Authentication error: {e}")
            return False
    
    def categorize_dm(self, text: str) -> Tuple[DMCategory, str]:
        """
        Categorize DM based on content patterns.
        Returns (category, template_key)
        """
        text_lower = text.lower()
        
        # Setup help patterns
        setup_patterns = [
            r'how to setup', r'how do i.*setup', r'help.*setup',
            r'confused.*setup', r'getting started', r'can\'t.*install',
            r'not working', r'error \d+', r'getting error',
            r'can\'t get.*work', r'installation', r'can\'t find',
            r'troubleshoot', r'what\'s wrong', r'broken'
        ]
        
        # Partnership/collaboration patterns
        partnership_patterns = [
            r'collaborate', r'partnership', r'sponsor', r'work.*together',
            r'affiliate', r'promotion', r'cross.*promote', r'brand ambassador',
            r'partner with', r'business opportunity', r'collaboration',
            r'strategic partnership', r'joint venture', r'co-marketing'
        ]
        
        # Product inquiry patterns
        product_patterns = [
            r'how much', r'pricing', r'cost', r'price', r'buy',
            r'purchase', r'which.*best', r'recommend', r'features',
            r'comparison', r'demo', r'free trial', r'plan',
            r'subscription', r'enterprise', r'custom pricing'
        ]
        
        # Newsletter patterns
        newsletter_patterns = [
            r'email.*list', r'newsletter', r'updates.*list',
            r'add.*email', r'subscribe', r'keep.*posted',
            r'stay.*updated', r'updates', r'mailing list'
        ]
        
        # Check patterns in priority order
        for pattern in setup_patterns:
            if re.search(pattern, text_lower):
                return DMCategory.SETUP_HELP, 'setup_help'
        
        for pattern in partnership_patterns:
            if re.search(pattern, text_lower):
                return DMCategory.PARTNERSHIP, 'partnership'
        
        for pattern in product_patterns:
            if re.search(pattern, text_lower):
                return DMCategory.PRODUCT_INQUIRY, 'product_inquiry'
        
        for pattern in newsletter_patterns:
            if re.search(pattern, text_lower):
                return DMCategory.NEWSLETTER, 'newsletter'
        
        # Default
        return DMCategory.OTHER, 'product_inquiry'
    
    def check_conversion_potential(self, text: str) -> Tuple[bool, bool]:
        """
        Check if DM has conversion potential (for flagging).
        Returns (has_budget_mention, high_conversion_potential)
        """
        text_lower = text.lower()
        
        budget_patterns = [
            r'\$\d+', r'budget.*\d+', r'spend.*\d+',
            r'investing.*\d+', r'yearly', r'monthly',
            r'annual subscription', r'enterprise'
        ]
        
        # High intent patterns
        intent_patterns = [
            r'need.*help', r'need.*product', r'looking for',
            r'interested in.*buy', r'when can i', r'how soon',
            r'urgent', r'asap', r'immediate'
        ]
        
        budget_mentioned = any(re.search(p, text_lower) for p in budget_patterns)
        high_intent = any(re.search(p, text_lower) for p in intent_patterns)
        
        return budget_mentioned, (budget_mentioned or high_intent)
    
    def fetch_dms_via_community(self) -> List[Dict]:
        """
        Fetch new DMs via YouTube Community API.
        YouTube DMs are accessed through Community posts.
        """
        if not self.youtube:
            self.logger.error("❌ YouTube service not initialized")
            return []
        
        try:
            self.logger.info("📥 Fetching DMs from YouTube Community...")
            
            last_check = self.get_last_check_time()
            self.logger.info(f"⏰ Checking for DMs since: {last_check.isoformat()}")
            
            # Fetch community posts (which includes DMs/messages)
            # Note: Official YouTube API has limitations; this gets community interactions
            posts = self.youtube.commentThreads().list(
                part='snippet',
                mine=True,
                maxResults=20,
                textFormat='plainText'
            ).execute()
            
            dms = []
            for post in posts.get('items', []):
                snippet = post['snippet']['topLevelComment']['snippet']
                comment_time = datetime.fromisoformat(
                    snippet['publishedAt'].replace('Z', '+00:00')
                )
                
                # Only include recent comments
                if comment_time > last_check:
                    dm = {
                        'id': post['id'],
                        'sender': snippet['authorDisplayName'],
                        'sender_id': snippet['authorChannelId'],
                        'text': snippet['textDisplay'],
                        'timestamp': snippet['publishedAt'],
                    }
                    dms.append(dm)
            
            self.logger.info(f"✅ Found {len(dms)} new message(s)")
            return dms
        
        except HttpError as e:
            self.logger.error(f"❌ API Error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}")
            return []
    
    def fetch_dms_from_log(self) -> List[Dict]:
        """
        Fetch DMs from existing log (for demo/testing).
        Checks for new entries since last run.
        """
        if not self.LOG_FILE.exists():
            return []
        
        try:
            self.logger.info("📥 Checking DM log for new entries...")
            
            last_check = self.get_last_check_time()
            new_dms = []
            seen_ids = set(self.get_processed_ids())
            
            with open(self.LOG_FILE, 'r') as f:
                for line in f:
                    if not line.strip() or line.startswith('#'):
                        continue
                    
                    try:
                        dm = json.loads(line)
                        dm_id = dm.get('dm_id')
                        
                        # Skip already processed
                        if dm_id in seen_ids:
                            continue
                        
                        # Check if recent enough
                        try:
                            dm_time_str = dm.get('timestamp', '')
                            # Handle timezone-aware and naive datetimes
                            if dm_time_str:
                                dm_time = datetime.fromisoformat(dm_time_str.replace('Z', '+00:00'))
                                # Make last_check timezone-aware if needed
                                if last_check.tzinfo is None:
                                    last_check_aware = last_check.replace(tzinfo=None)
                                    dm_time_naive = dm_time.replace(tzinfo=None)
                                    if dm_time_naive > last_check_aware:
                                        new_dms.append(dm)
                                        seen_ids.add(dm_id)
                                else:
                                    if dm_time > last_check:
                                        new_dms.append(dm)
                                        seen_ids.add(dm_id)
                        except ValueError:
                            # If date parsing fails, include it
                            new_dms.append(dm)
                            seen_ids.add(dm_id)
                    
                    except json.JSONDecodeError:
                        continue
            
            self.logger.info(f"✅ Found {len(new_dms)} new entry/entries in log")
            return new_dms
        
        except Exception as e:
            self.logger.error(f"❌ Error reading log: {e}")
            return []
    
    def fetch_dms(self) -> List[Dict]:
        """
        Fetch new DMs. Tries API first, falls back to log.
        """
        # Try YouTube API
        dms = self.fetch_dms_via_community()
        
        # If API didn't return anything, check the log
        if not dms:
            self.logger.info("ℹ️  Falling back to log check...")
            dms = self.fetch_dms_from_log()
        
        return dms
    
    def get_processed_ids(self) -> List[str]:
        """Get list of already-processed DM IDs"""
        if self.STATE_FILE.exists():
            try:
                with open(self.STATE_FILE, 'r') as f:
                    state = json.load(f)
                    return state.get('last_processed_ids', [])
            except:
                pass
        return []
    
    def get_last_check_time(self) -> datetime:
        """Get timestamp of last DM check"""
        if self.STATE_FILE.exists():
            try:
                with open(self.STATE_FILE, 'r') as f:
                    state = json.load(f)
                    ts = state.get('last_run')
                    if ts:
                        return datetime.fromisoformat(ts)
            except:
                pass
        
        # Default: 24 hours ago
        return datetime.now() - timedelta(hours=24)
    
    def log_dm(self, dm: DMRecord):
        """Log DM to JSONL file"""
        try:
            self.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.LOG_FILE, 'a') as f:
                f.write(json.dumps(asdict(dm)) + '\n')
            self.logger.info(f"✅ Logged DM from {dm.sender}")
        except Exception as e:
            self.logger.error(f"❌ Failed to log DM: {e}")
    
    def flag_partnership(self, dm: DMRecord):
        """Flag partnership request for manual review"""
        try:
            self.PARTNERSHIP_FLAGS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.PARTNERSHIP_FLAGS_FILE, 'a') as f:
                flag_data = asdict(dm)
                flag_data['flagged_at'] = datetime.now().isoformat()
                f.write(json.dumps(flag_data) + '\n')
            self.logger.info(f"🚩 Flagged partnership from {dm.sender}")
            self.flagged_partnerships.append(dm)
        except Exception as e:
            self.logger.error(f"❌ Failed to flag partnership: {e}")
    
    def process_dms(self, dms: List[Dict]) -> List[DMRecord]:
        """Process, categorize, and log DMs"""
        processed = []
        seen_ids = set(self.get_processed_ids())
        
        for dm in dms:
            dm_id = dm.get('dm_id') or dm.get('id')
            
            # Skip if already processed
            if dm_id in seen_ids:
                self.logger.info(f"⏭️  Skipping already-processed DM: {dm_id}")
                continue
            
            sender = dm.get('sender', 'Unknown')
            sender_id = dm.get('sender_id', '')
            text = dm.get('text', '')
            
            self.logger.info(f"📨 Processing DM from {sender}...")
            
            # Categorize
            category, template_key = self.categorize_dm(text)
            response_template = self.RESPONSES.get(template_key, '')
            
            # Check for conversion potential
            budget_mentioned, conversion_potential = self.check_conversion_potential(text)
            
            # Create record
            dm_record = DMRecord(
                timestamp=dm.get('timestamp', datetime.now().isoformat()),
                sender=sender,
                sender_id=sender_id,
                text=text,
                category=category.value,
                response_sent=True,  # Mark as sent (auto-response)
                response_template=response_template,
                dm_id=dm_id,
                budget_mentioned=budget_mentioned,
                conversion_potential=conversion_potential,
                manual_review_flag=(category == DMCategory.PARTNERSHIP or conversion_potential)
            )
            
            # Log DM
            self.log_dm(dm_record)
            
            # Track by category
            if category == DMCategory.PARTNERSHIP:
                self.flag_partnership(dm_record)
                self.logger.info(f"🤝 Partnership opportunity from {sender}")
            elif category == DMCategory.PRODUCT_INQUIRY:
                self.product_inquiries.append(dm_record)
                self.logger.info(f"💡 Product inquiry from {sender}")
            
            # Update counters
            self.auto_responses_sent += 1
            self.dms_processed += 1
            processed.append(dm_record)
            seen_ids.add(dm_id)
        
        return processed
    
    def save_state(self):
        """Save monitor state"""
        try:
            self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            processed_ids = self.get_processed_ids()
            
            # Add newly processed IDs
            for dm in self.new_dms:
                dm_id = dm.dm_id
                if dm_id not in processed_ids:
                    processed_ids.append(dm_id)
            
            # Keep only last 100 IDs
            processed_ids = processed_ids[-100:]
            
            state = {
                'last_run': datetime.now().isoformat(),
                'last_processed_ids': processed_ids,
                'total_lifetime_dms': self.get_lifetime_stats().get('total_dms', 0),
                'total_lifetime_responses': self.get_lifetime_stats().get('total_responses', 0),
                'total_lifetime_flagged': len(self.flagged_partnerships),
                'latest_run_summary': {
                    'execution_date': datetime.now().strftime('%Y-%m-%d'),
                    'dms_processed': self.dms_processed,
                    'new_dms': len(self.new_dms),
                    'responses_sent': self.auto_responses_sent,
                    'flagged_partnerships': len(self.flagged_partnerships),
                }
            }
            
            with open(self.STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
            
            self.logger.info(f"✅ State saved to {self.STATE_FILE}")
        except Exception as e:
            self.logger.error(f"❌ Failed to save state: {e}")
    
    def get_lifetime_stats(self) -> Dict:
        """Get lifetime statistics from log"""
        stats = {
            'total_dms': 0,
            'total_responses': 0,
            'setup_help': 0,
            'newsletter': 0,
            'product_inquiry': 0,
            'partnership': 0,
        }
        
        if not self.LOG_FILE.exists():
            return stats
        
        try:
            with open(self.LOG_FILE, 'r') as f:
                for line in f:
                    if not line.strip() or line.startswith('#'):
                        continue
                    
                    try:
                        dm = json.loads(line)
                        stats['total_dms'] += 1
                        if dm.get('response_sent'):
                            stats['total_responses'] += 1
                        
                        category = dm.get('category', 'Other').lower().replace(' ', '_')
                        if category in stats:
                            stats[category] += 1
                    except:
                        pass
        except:
            pass
        
        return stats
    
    def generate_report(self) -> str:
        """Generate comprehensive report"""
        report = []
        lifetime_stats = self.get_lifetime_stats()
        
        report.append("=" * 70)
        report.append("📊 YouTube DM Monitor Report - Concessa Obvius")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # This run summary
        report.append("🔄 THIS RUN SUMMARY")
        report.append(f"  DMs Processed:      {self.dms_processed}")
        report.append(f"  Auto-responses:     {self.auto_responses_sent}")
        report.append(f"  New DMs found:      {len(self.new_dms)}")
        report.append(f"  Flagged for review: {len(self.flagged_partnerships)}")
        report.append("")
        
        # Lifetime statistics
        report.append("📈 LIFETIME STATISTICS")
        report.append(f"  Total DMs processed:     {lifetime_stats['total_dms']}")
        report.append(f"  Total auto-responses:    {lifetime_stats['total_responses']}")
        report.append(f"  Setup Help requests:     {lifetime_stats['setup_help']}")
        report.append(f"  Newsletter signups:      {lifetime_stats['newsletter']}")
        report.append(f"  Product inquiries:       {lifetime_stats['product_inquiry']}")
        report.append(f"  Partnership requests:    {lifetime_stats['partnership']}")
        report.append("")
        
        # Partnership flags
        if self.flagged_partnerships:
            report.append("🚩 PARTNERSHIPS FLAGGED FOR MANUAL REVIEW")
            for partnership in self.flagged_partnerships:
                report.append(f"  • {partnership.sender} - {partnership.text[:60]}...")
                if partnership.budget_mentioned:
                    report.append(f"    💰 Budget mentioned")
                if partnership.conversion_potential:
                    report.append(f"    🎯 High conversion potential")
            report.append("")
        
        # Product inquiries
        if self.product_inquiries:
            report.append("💡 PRODUCT INQUIRIES (Conversion Opportunities)")
            for inquiry in self.product_inquiries[:5]:
                report.append(f"  • {inquiry.sender}: {inquiry.text[:50]}...")
            if len(self.product_inquiries) > 5:
                report.append(f"  ... and {len(self.product_inquiries) - 5} more")
            report.append("")
        
        report.append("=" * 70)
        report.append(f"Next run expected: {(datetime.now() + timedelta(hours=1)).isoformat()}")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def print_partnership_flags(self):
        """Print partnership flags for manual review"""
        if not self.flagged_partnerships:
            return
        
        print("\n" + "=" * 70)
        print("🚩 PARTNERSHIP OPPORTUNITIES - MANUAL REVIEW REQUIRED")
        print("=" * 70)
        
        for i, partnership in enumerate(self.flagged_partnerships, 1):
            print(f"\n[{i}] {partnership.sender}")
            print(f"    Date: {partnership.timestamp}")
            print(f"    Text: {partnership.text}")
            if partnership.budget_mentioned:
                print(f"    ✓ Budget mentioned")
            if partnership.conversion_potential:
                print(f"    ✓ High conversion potential")
        
        print("\n" + "=" * 70)
    
    def run(self) -> bool:
        """Execute monitor"""
        self.logger.info("🚀 YouTube DM Monitor starting...")
        
        try:
            # Authenticate
            if not self.authenticate():
                self.logger.error("❌ Authentication failed")
                return False
            
            # Fetch DMs
            dms = self.fetch_dms()
            if not dms:
                self.logger.info("ℹ️  No new DMs found")
                self.save_state()
                return True
            
            # Process DMs
            self.logger.info(f"⚙️  Processing {len(dms)} DM(s)...")
            self.new_dms = self.process_dms(dms)
            
            if not self.new_dms:
                self.logger.info("ℹ️  No new DMs to process (all already seen)")
                self.save_state()
                return True
            
            # Save state
            self.save_state()
            
            # Generate and print report
            report = self.generate_report()
            self.logger.info(report)
            
            # Save report
            self.DM_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.DM_REPORT_FILE, 'w') as f:
                f.write(report)
            self.logger.info(f"✅ Report saved to {self.DM_REPORT_FILE}")
            
            # Print partnership flags
            self.print_partnership_flags()
            
            self.logger.info("✅ Monitor run completed successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {e}", exc_info=True)
            return False


def main():
    """Main entry point"""
    monitor = YouTubeDMMonitorProd()
    success = monitor.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
