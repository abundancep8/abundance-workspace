"""
Comment Categorizer
Categorizes YouTube comments into 4 categories with keyword matching and templates.
"""

import logging
import re
from typing import Dict, List


class CommentCategorizer:
    """
    Categorizes comments into:
    1. Questions (how-to, tools, cost, timeline)
    2. Praise (amazing, inspiring, positive feedback)
    3. Spam (crypto, MLM, off-topic promotions)
    4. Sales (partnership, collaboration requests)
    """
    
    CATEGORIES = {
        '1_questions': {
            'name': 'Questions',
            'keywords': [
                # Exact question patterns (high weight)
                'how do i', 'how to', 'how can', 'how does',
                'what is', 'what\'s', 'where can',
                'when', 'why', 'which', 'who',
                # Specific question topics
                'cost', 'price', 'timeline', 'tools', 'setup',
                'start', 'getting started', 'tutorial',
                'can i', '?', 'help me',
            ],
            'weight': 1.0,
        },
        '2_praise': {
            'name': 'Praise',
            'keywords': [
                'amazing', 'awesome', 'incredible', 'love this',
                'great', 'brilliant', 'inspiring', 'fantastic',
                'excellent', 'genius', 'mind-blowing', 'game-changer',
                'thanks', 'thank you', 'grateful', 'best',
                'love', 'well done', 'perfect', 'awesome sauce',
                '❤️', '👏', '🔥', '⭐'
            ],
            'weight': 1.0,
        },
        '3_spam': {
            'name': 'Spam',
            'keywords': [
                'crypto', 'bitcoin', 'ethereum', 'nft', 'coin',
                'mlm', 'multi-level', 'pyramid',
                'join now', 'click here', 'limited time', 'act fast',
                'earn money fast', 'work from home', 'get rich',
                'forex', 'casino', 'betting', 'slots',
                'dm me', 'check my profile', 'follow my link',
                'pump', 'moon', 'lambo', 'guaranteed profits'
            ],
            'weight': 1.0,
        },
        '4_sales': {
            'name': 'Sales/Partnership',
            'keywords': [
                'partnership', 'collaborate', 'collaboration',
                'sponsor', 'sponsorship', 'advertisement', 'advertise',
                'promote', 'promotion', 'business opportunity',
                'affiliate', 'brand deal', 'deal',
                'looking to work', 'interested in working',
                'can we partner', 'white label', 'reseller',
                'wholesale', 'agency', 'pitch', 'proposal'
            ],
            'weight': 1.0,
        },
    }
    
    def __init__(self, config: Dict = None):
        """Initialize with optional config override."""
        self.config = config or {}
        self.log = logging.getLogger('categorizer')
        
        # Override keywords from config if provided
        if self.config and 'categories' in self.config:
            for cat_id, cat_config in config['categories'].items():
                if cat_id in self.CATEGORIES:
                    self.CATEGORIES[cat_id]['keywords'] = cat_config.get(
                        'keywords',
                        self.CATEGORIES[cat_id]['keywords']
                    )
    
    
    def categorize(self, text: str) -> str:
        """
        Categorize a comment.
        
        Uses keyword matching with weights.
        Falls back to neutral category if no keywords match.
        
        Args:
            text: Comment text
            
        Returns:
            Category ID (1_questions, 2_praise, 3_spam, 4_sales)
        """
        text_lower = text.lower()
        text_clean = re.sub(r'[^\w\s]', '', text_lower)
        text_words = set(text_clean.split())
        
        scores = {}
        
        # Score each category
        for cat_id, cat_data in self.CATEGORIES.items():
            score = 0
            keywords_found = []
            
            for keyword in cat_data['keywords']:
                keyword_clean = re.sub(r'[^\w\s]', '', keyword).lower()
                
                # Multi-word phrase match (highest weight)
                if ' ' in keyword_clean:
                    if keyword_clean in text_clean:
                        score += 3 * cat_data['weight']
                        keywords_found.append(keyword)
                # Single word with boundaries (medium-high weight)
                else:
                    if keyword_clean in text_words:
                        score += 2 * cat_data['weight']
                        keywords_found.append(keyword)
                    elif keyword_clean in text_clean and len(keyword_clean) > 3:
                        # Partial match for longer keywords
                        score += 1 * cat_data['weight']
                        keywords_found.append(keyword)
            
            if score > 0:
                scores[cat_id] = {
                    'score': score,
                    'keywords_found': keywords_found
                }
        
        # Return category with highest score
        if not scores:
            # Default neutral categorization
            if '?' in text:
                return '1_questions'
            if len(text) < 20:
                return '2_praise'  # Short comments usually positive
            return '2_praise'  # Default to praise if unsure
        
        best_category = max(scores.items(), key=lambda x: x[1]['score'])[0]
        return best_category
    
    
    def get_response_template(self, category: str) -> str:
        """Get response template for a category."""
        templates = {
            '1_questions': (
                "Thanks for asking! 👋\n\n"
                "Great question! Check our documentation for more details, "
                "or feel free to ask follow-up questions. We're here to help! 🚀"
            ),
            '2_praise': (
                "Thank you so much! 🙏\n\n"
                "Glad this is helpful. Keep building amazing things! 💪"
            ),
            '3_spam': None,  # No response
            '4_sales': None,  # Flagged for manual review
        }
        
        # Check config for custom templates
        if 'auto_response_templates' in self.config:
            if category == '1_questions' and 'question_template' in self.config['auto_response_templates']:
                return self.config['auto_response_templates']['question_template']
            if category == '2_praise' and 'praise_template' in self.config['auto_response_templates']:
                return self.config['auto_response_templates']['praise_template']
        
        return templates.get(category, '')
    
    
    def get_category_name(self, category_id: str) -> str:
        """Get human-readable category name."""
        return self.CATEGORIES.get(category_id, {}).get('name', 'Unknown')
