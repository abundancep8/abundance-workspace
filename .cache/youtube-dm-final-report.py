#!/usr/bin/env python3
"""
YouTube DM Monitor - Final Report Generator
Processes all DMs in log and generates comprehensive report.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import re

WORKSPACE_ROOT = Path.home() / '.openclaw' / 'workspace'
CACHE_DIR = WORKSPACE_ROOT / '.cache'
LOG_FILE = CACHE_DIR / 'youtube-dms.jsonl'
PARTNERSHIP_FILE = CACHE_DIR / 'youtube-flagged-partnerships.jsonl'
REPORT_FILE = CACHE_DIR / 'youtube-dms-final-report.txt'


class DMAnalyzer:
    """Analyze DM log and generate reports"""
    
    def __init__(self):
        self.dms = []
        self.partnerships = []
        self.product_inquiries = []
        self.stats = {
            'total_dms': 0,
            'setup_help': 0,
            'newsletter': 0,
            'product_inquiry': 0,
            'partnership': 0,
            'other': 0,
            'auto_responses_sent': 0,
            'flagged_for_review': 0,
        }
    
    def load_dms(self) -> bool:
        """Load DMs from log"""
        if not LOG_FILE.exists():
            print(f"❌ Log file not found: {LOG_FILE}")
            return False
        
        print(f"📥 Loading DMs from {LOG_FILE}...")
        
        try:
            with open(LOG_FILE, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip() or line.startswith('#'):
                        continue
                    
                    try:
                        dm = json.loads(line)
                        self.dms.append(dm)
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Skipping line {line_num}: {e}")
            
            print(f"✅ Loaded {len(self.dms)} DM(s)")
            return True
        
        except Exception as e:
            print(f"❌ Error loading DMs: {e}")
            return False
    
    def analyze_dms(self):
        """Analyze DM content and categorize"""
        print(f"⚙️  Analyzing {len(self.dms)} DM(s)...")
        
        for dm in self.dms:
            category = str(dm.get('category', 'Other')).lower()
            self.stats['total_dms'] += 1
            
            if dm.get('response_sent'):
                self.stats['auto_responses_sent'] += 1
            
            if dm.get('manual_review') or dm.get('manual_review_flag'):
                self.stats['flagged_for_review'] += 1
                self.partnerships.append(dm)
            
            # Count by category
            if 'setup' in category:
                self.stats['setup_help'] += 1
            elif 'newsletter' in category:
                self.stats['newsletter'] += 1
            elif 'product' in category:
                self.stats['product_inquiry'] += 1
                self.product_inquiries.append(dm)
            elif 'partnership' in category:
                self.stats['partnership'] += 1
                self.partnerships.append(dm)
            else:
                self.stats['other'] += 1
        
        print(f"✅ Analysis complete")
    
    def check_conversion_potential(self, text: str) -> Tuple[bool, bool]:
        """Check for budget mentions and conversion indicators"""
        text_lower = text.lower()
        
        budget_patterns = [
            r'\$\d+', r'budget', r'pricing', r'cost',
            r'enterprise', r'monthly', r'yearly', r'annual',
            r'investment', r'spend'
        ]
        
        budget_found = any(re.search(p, text_lower) for p in budget_patterns)
        
        high_intent_patterns = [
            r'need', r'looking for', r'interested', r'when',
            r'how soon', r'urgent', r'asap', r'custom'
        ]
        
        high_intent = any(re.search(p, text_lower) for p in high_intent_patterns)
        
        return budget_found, (budget_found or high_intent)
    
    def generate_report(self) -> str:
        """Generate comprehensive report"""
        report = []
        
        report.append("=" * 80)
        report.append("📊 YOUTUBE DM MONITOR - FINAL REPORT")
        report.append("Channel: Concessa Obvius")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        # Summary stats
        report.append("📈 PROCESSING SUMMARY")
        report.append("-" * 80)
        report.append(f"  Total DMs processed:        {self.stats['total_dms']}")
        report.append(f"  Auto-responses sent:        {self.stats['auto_responses_sent']}")
        report.append(f"  Flagged for manual review:  {self.stats['flagged_for_review']}")
        report.append("")
        
        # Breakdown by category
        report.append("📋 CATEGORIZATION BREAKDOWN")
        report.append("-" * 80)
        report.append(f"  Setup Help:     {self.stats['setup_help']:3d} ({self._pct(self.stats['setup_help'])}%)")
        report.append(f"  Newsletter:     {self.stats['newsletter']:3d} ({self._pct(self.stats['newsletter'])}%)")
        report.append(f"  Product Inquiry: {self.stats['product_inquiry']:3d} ({self._pct(self.stats['product_inquiry'])}%)")
        report.append(f"  Partnership:    {self.stats['partnership']:3d} ({self._pct(self.stats['partnership'])}%)")
        report.append(f"  Other:          {self.stats['other']:3d} ({self._pct(self.stats['other'])}%)")
        report.append("")
        
        # Product inquiries with conversion potential
        if self.product_inquiries:
            report.append("💡 PRODUCT INQUIRIES (Conversion Opportunities)")
            report.append("-" * 80)
            for i, inquiry in enumerate(self.product_inquiries[:10], 1):
                sender = inquiry.get('sender', 'Unknown')
                text = inquiry.get('text', '')
                budget_mentioned, conversion = self.check_conversion_potential(text)
                
                report.append(f"\n  [{i}] {sender}")
                report.append(f"      Message: {text[:70]}...")
                if budget_mentioned:
                    report.append(f"      ✓ Budget mentioned")
                if conversion:
                    report.append(f"      🎯 High conversion potential")
            
            if len(self.product_inquiries) > 10:
                report.append(f"\n  ... and {len(self.product_inquiries) - 10} more product inquiries")
            report.append("")
        
        # Partnerships flagged for review
        if self.partnerships:
            report.append("🚩 PARTNERSHIPS - FLAGGED FOR MANUAL REVIEW")
            report.append("-" * 80)
            for i, partnership in enumerate(self.partnerships[:10], 1):
                sender = partnership.get('sender', 'Unknown')
                text = partnership.get('text', '')
                budget_mentioned, conversion = self.check_conversion_potential(text)
                
                report.append(f"\n  [{i}] {sender}")
                report.append(f"      Message: {text[:70]}...")
                report.append(f"      Category: {partnership.get('category', 'Partnership')}")
                if budget_mentioned:
                    report.append(f"      💰 Budget mentioned")
                if conversion:
                    report.append(f"      🎯 High conversion potential")
            
            if len(self.partnerships) > 10:
                report.append(f"\n  ... and {len(self.partnerships) - 10} more partnership opportunities")
            report.append("")
        
        # Template responses used
        report.append("📝 AUTO-RESPONSE TEMPLATES DEPLOYED")
        report.append("-" * 80)
        templates_used = set()
        for dm in self.dms:
            template = str(dm.get('response_template') or dm.get('category', 'Other'))
            template_short = template[:50] + "..." if len(template) > 50 else template
            templates_used.add(template_short)
        
        for i, template in enumerate(sorted(templates_used), 1):
            report.append(f"  {i}. {template}")
        report.append("")
        
        # Final summary
        report.append("=" * 80)
        report.append("✅ MONITOR STATUS: OPERATIONAL")
        report.append("")
        report.append("📊 KEY METRICS")
        report.append(f"  Response rate:           {self._pct(self.stats['auto_responses_sent'])}%")
        report.append(f"  Conversion opportunities: {len(self.product_inquiries)}")
        report.append(f"  Partnership leads:       {len(self.partnerships)}")
        report.append("")
        report.append("🎯 RECOMMENDED NEXT STEPS")
        report.append("  1. Review flagged partnerships for follow-up")
        report.append("  2. Prioritize product inquiries with budget mentions")
        report.append("  3. Schedule follow-up with high-intent leads")
        report.append("  4. Analyze common setup issues for documentation")
        report.append("")
        report.append("=" * 80)
        report.append(f"Log file: {LOG_FILE}")
        report.append(f"Generated by: YouTube DM Monitor v2026")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_partnership_flags(self):
        """Save flagged partnerships to file"""
        if not self.partnerships:
            return
        
        print(f"🚩 Saving {len(self.partnerships)} partnership flag(s)...")
        
        try:
            PARTNERSHIP_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(PARTNERSHIP_FILE, 'w') as f:
                for partnership in self.partnerships:
                    f.write(json.dumps(partnership) + '\n')
            print(f"✅ Partnership flags saved to {PARTNERSHIP_FILE}")
        except Exception as e:
            print(f"❌ Error saving flags: {e}")
    
    def _pct(self, count: int) -> int:
        """Calculate percentage"""
        if self.stats['total_dms'] == 0:
            return 0
        return round(100 * count / self.stats['total_dms'])


def main():
    """Main entry point"""
    analyzer = DMAnalyzer()
    
    # Load DMs
    if not analyzer.load_dms():
        sys.exit(1)
    
    # Analyze
    analyzer.analyze_dms()
    
    # Generate report
    report = analyzer.generate_report()
    
    # Print to console
    print("\n" + report + "\n")
    
    # Save report
    try:
        REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(REPORT_FILE, 'w') as f:
            f.write(report)
        print(f"✅ Report saved to {REPORT_FILE}")
    except Exception as e:
        print(f"❌ Error saving report: {e}")
    
    # Save partnership flags
    analyzer.save_partnership_flags()
    
    print("\n✅ Processing complete!")


if __name__ == '__main__':
    main()
