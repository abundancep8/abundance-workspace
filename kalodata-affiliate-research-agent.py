#!/usr/bin/env python3
"""
KALODATA AFFILIATE RESEARCH AGENT
Find the best affiliate products for TikTok Shop
Research strategy: High rating + High sales + High commission
"""

import json
from datetime import datetime
from pathlib import Path

print("="*70)
print("KALODATA AFFILIATE RESEARCH AGENT")
print("Find Top Affiliate Products for TikTok Shop")
print("="*70 + "\n")

# PRODUCT RESEARCH CRITERIA
RESEARCH_CRITERIA = {
    "minimum_rating": 4.5,
    "minimum_monthly_sales": 100,
    "minimum_commission_rate": 15,
    "preferred_commission_rate": 20,  # 20%+ is ideal
    "category_priority": [
        "beauty_skincare",
        "wellness_health",
        "productivity_tech",
        "fashion_accessories",
        "home_kitchen"
    ]
}

# TOP AFFILIATE PRODUCT TEMPLATES (What Agent Searches For)
AFFILIATE_SEARCH_TEMPLATES = [
    {
        "category": "beauty_skincare",
        "keywords": [
            "Korean skincare serum",
            "anti-aging face mask",
            "acne treatment cream",
            "vitamin C serum",
            "moisturizer with SPF"
        ],
        "pain_point": "Dull skin, acne, wrinkles",
        "hook": "This $12 item changed my skin (dermatologists hate it)",
        "commission_range": "15-40%"
    },
    {
        "category": "wellness_health",
        "keywords": [
            "sleep supplement melatonin",
            "joint support collagen",
            "energy supplement",
            "vitamin B complex",
            "magnesium powder"
        ],
        "pain_point": "Low energy, poor sleep, joint pain",
        "hook": "Doctors recommend this for sleep (this brand is #1)",
        "commission_range": "10-30%"
    },
    {
        "category": "productivity_tech",
        "keywords": [
            "fast phone charger",
            "desk organizer system",
            "noise-canceling earbuds",
            "standing desk",
            "blue light glasses"
        ],
        "pain_point": "Disorganization, low focus, fatigue",
        "hook": "My productivity increased 40% with this simple tool",
        "commission_range": "5-20%"
    },
    {
        "category": "fashion_accessories",
        "keywords": [
            "minimalist jewelry",
            "sustainable handbag",
            "athleisure leggings",
            "luxury scarf",
            "crossbody bag"
        ],
        "pain_point": "Outdated style, poor self-image",
        "hook": "This \$30 piece is from a luxury brand for 1/4 the price",
        "commission_range": "10-25%"
    },
    {
        "category": "home_kitchen",
        "keywords": [
            "air fryer",
            "storage container set",
            "bamboo cutting board",
            "coffee maker",
            "organizer bins"
        ],
        "pain_point": "Inefficiency, clutter, waste",
        "hook": "This simple item saves me 20 minutes every day",
        "commission_range": "8-20%"
    }
]

def generate_research_instructions():
    """Generate instructions for Agent to research products"""
    
    print("""
═══════════════════════════════════════════════════════════════════════════════
KALODATA AFFILIATE PRODUCT RESEARCH PROTOCOL
═══════════════════════════════════════════════════════════════════════════════

AGENT MISSION:
Find top 50 affiliate products suitable for TikTok Shop
Filter by: 4.5+ rating, 100+ monthly sales, 15%+ commission
Rank by: Conversion potential (rating × commission × market size)
Output: Top 10 products for Week 1 launch

RESEARCH PROCESS:

Step 1: Category Prioritization
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Focus on high-conversion categories (in order):
1. Beauty/Skincare (highest ROI, 15-40% commission)
2. Wellness/Health (emotional investment, 10-30% commission)
3. Productivity/Tech (business buyers, 5-20% commission)
4. Fashion/Accessories (visual on TikTok, 10-25% commission)
5. Home/Kitchen (repeat purchase, 8-20% commission)

Step 2: Keyword Research
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each category, search Kalodata (or Amazon affiliate):

Beauty/Skincare searches:
✓ \"Korean skincare serum\" → Find: Rating, Sales/month, Commission
✓ \"Anti-aging face mask\" → Find: Rating, Sales/month, Commission
✓ \"Acne treatment cream\" → Find: Rating, Sales/month, Commission
✓ \"Vitamin C serum\" → Find: Rating, Sales/month, Commission
✓ \"Moisturizer with SPF\" → Find: Rating, Sales/month, Commission

(Repeat for each category)

Step 3: Filter by Criteria
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Keep only products that meet ALL criteria:
✓ Rating: 4.5+ stars (min 4.3 acceptable)
✓ Sales: 100+ per month (min 50 for niche products)
✓ Commission: 15%+ (min 12% for high-volume products)
✓ Review count: 100+ reviews (social proof)
✓ Price range: \$15-150 (sweet spot for conversions)

Step 4: Ranking Algorithm (Conversion Potential Score)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Calculate score for each product:

Score = (Rating/5.0) × (Commission/25) × (Monthly Sales/500) × (Reviews/500)

Example:
Product A: Rating 4.8, Commission 20%, Sales 250/month, Reviews 200
Score = (4.8/5.0) × (20/25) × (250/500) × (200/500)
Score = 0.96 × 0.80 × 0.50 × 0.40 = 0.154

Product B: Rating 4.5, Commission 25%, Sales 1000/month, Reviews 1000
Score = (4.5/5.0) × (25/25) × (1000/500) × (1000/500)
Score = 0.90 × 1.00 × 2.00 × 2.00 = 3.6

(Product B scores higher = better conversion potential)

Step 5: Competitor Pricing Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For top 20 products, research:
✓ Amazon price (baseline)
✓ Walmart price (if listed)
✓ Direct brand price (if available)
✓ Other marketplace prices

TikTok Shop strategy: Price 10-20% below lowest competitor
- Creates urgency (\"best price available\")
- Builds initial sales volume (for reviews)
- Attracts price-conscious TikTok audience

Step 6: Marketing Psychology Mapping
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For each top product, identify:
✓ Primary pain point (what problem does it solve?)
✓ Curiosity hook (title that makes people click)
✓ Social proof angle (what review language appears most?)
✓ Before/after potential (can you show transformation?)
✓ Urgency angle (scarcity, seasonality, trending)

Example:
Product: Vitamin C Serum
- Pain point: Dull, uneven skin tone
- Hook: \"This \$15 serum outperforms \$80 brands (here's why)\"
- Social proof: \"Glowing skin in 2 weeks\"
- Before/after: Yes (skin brightening is visual)
- Urgency: \"Trending in K-beauty\" + inventory scarcity

═══════════════════════════════════════════════════════════════════════════════
EXPECTED OUTPUT FORMAT
═══════════════════════════════════════════════════════════════════════════════

Top 10 Products for Week 1 Launch:

| Rank | Product | Category | Rating | Sales/mo | Commission | Score | TikTok Price |
|------|---------|----------|--------|----------|------------|-------|--------------|
| 1 | [Name] | Beauty | 4.8 | 1000 | 25% | 3.6 | \$19 |
| 2 | [Name] | Wellness | 4.7 | 800 | 20% | 2.8 | \$24 |
| 3 | [Name] | Tech | 4.6 | 600 | 18% | 1.9 | \$49 |
... (10 total)

Top 20 Products for Month 1 Expansion:
(Same format, ranked 11-30)

Top 50 Products for Reference:
(Full research database, ranked 1-50)

═══════════════════════════════════════════════════════════════════════════════
CRITICAL SUCCESS FACTORS
═══════════════════════════════════════════════════════════════════════════════

1. **Rating is #1 Priority** (4.5+ non-negotiable)
   - 4.5+ = 10x more clicks on TikTok Shop
   - 4.0-4.4 = struggling to convert
   - <4.0 = avoid completely

2. **Commission Rate Matters** (15%+ target)
   - 25%+ = high profitability
   - 15-24% = good margin
   - <15% = low profit, not worth listing

3. **Sales Velocity Signals Demand** (100+/month)
   - 1000+/month = proven bestseller
   - 500+/month = strong market
   - 100+/month = minimum viable
   - <100/month = unproven demand

4. **Reviews Are Social Proof** (100+ reviews)
   - 1000+ reviews = trusted, visible
   - 500+ = strong proof
   - 100+ = minimum for credibility
   - Review content matters more than count

5. **Pricing Strategy** (Price 10-20% below competitor)
   - Amazon \$29 → TikTok Shop \$23-26 (best price perception)
   - Creates urgency (\"only on TikTok\")
   - Attracts price-conscious TikTok audience
   - Builds initial sales volume fast

═══════════════════════════════════════════════════════════════════════════════
TIMELINE
═══════════════════════════════════════════════════════════════════════════════

TODAY (2026-04-09):
- [ ] Research top 50 affiliate products (per above protocol)
- [ ] Calculate conversion potential scores
- [ ] Identify top 10 for Week 1 launch

TOMORROW (2026-04-10):
- [ ] List top 10 products on TikTok Shop
- [ ] Optimize titles/descriptions/images per psychology framework
- [ ] Set up supplier relationships (drop-shipping)
- [ ] Launch flash sale (10-30% off for initial reviews)

WEEK 1 (Apr 10-16):
- [ ] Monitor conversion rates
- [ ] Respond to all DMs + comments
- [ ] Feature customer testimonials
- [ ] Expand to top 20 products

WEEK 2-4 (Apr 17-May 7):
- [ ] Scale content marketing (4-8 posts/day)
- [ ] Optimize pricing based on performance
- [ ] Expand to top 30-40 products
- [ ] Target \$700-2,800 revenue

═══════════════════════════════════════════════════════════════════════════════
""")

def log_research_status():
    """Log research status"""
    
    event = {
        "timestamp": datetime.now().isoformat(),
        "task": "kalodata_affiliate_research",
        "status": "research_protocol_defined",
        "criteria": RESEARCH_CRITERIA,
        "categories_to_research": 5,
        "target_products": {
            "week1": 10,
            "month1": 40,
            "reference": 50
        }
    }
    
    with open('.cache/kalodata-research-status.jsonl', 'a') as f:
        f.write(json.dumps(event) + '\n')

if __name__ == "__main__":
    generate_research_instructions()
    log_research_status()
    
    print("\n✅ RESEARCH PROTOCOL READY")
    print("   Next: Agent executes Kalodata research")
    print("   Search: 5 categories × 5 keywords = 25 searches")
    print("   Output: Top 10 products (Week 1), Top 50 (reference)")
    print("   Timeline: Complete by 2026-04-10 morning\n")
