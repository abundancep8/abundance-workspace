#!/usr/bin/env node

/**
 * YouTube DM Monitor
 * Monitors Concessa Obvius channel DMs and auto-responds with categorized templates
 * 
 * Categories:
 * 1. Setup help - How to set up, confused about features
 * 2. Newsletter - Email list, updates, subscriptions
 * 3. Product inquiry - Buy, pricing, product selection
 * 4. Partnership - Collaborate, sponsorship, business inquiry
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const CACHE_FILE = path.join(process.env.HOME, '.openclaw/.cache/youtube-dms.jsonl');
const TIMESTAMP = new Date().toISOString();

// Auto-response templates by category
const TEMPLATES = {
  'Setup help': {
    subject: 'Help with Setup',
    body: `Hi! Thanks for reaching out about setup. We're here to help! 

Here are some resources that might help:
- Video tutorials: [Link to setup guide]
- Documentation: [Link to docs]
- FAQ: [Link to FAQ]

If you need more specific help, please reply with details about what you're trying to do and where you're stuck.

Best regards,
Concessa`
  },
  'Newsletter': {
    subject: 'Newsletter Signup',
    body: `Hi! Thanks for your interest in staying updated!

You can subscribe to our newsletter here: [Newsletter signup link]

I send updates about:
- New videos and tutorials
- Product announcements
- Exclusive tips and behind-the-scenes content

Looking forward to connecting with you!

Best regards,
Concessa`
  },
  'Product inquiry': {
    subject: 'Product Information',
    body: `Hi! Thanks for your interest!

Here's what I offer:
- [Product 1]: [Brief description + price]
- [Product 2]: [Brief description + price]
- [Product 3]: [Brief description + price]

I'd be happy to answer any specific questions or help you find what works best for your needs.

What are you looking for?

Best regards,
Concessa`
  },
  'Partnership': {
    subject: 'Partnership Inquiry',
    body: `Hi! Thanks for reaching out about potential collaboration!

I'm interested in discussing this further. To help me evaluate if this is a good fit, could you tell me a bit more about:
- What type of partnership you're proposing
- Your audience/reach
- Timeline and goals

I'll review and get back to you within 48 hours.

Best regards,
Concessa`
  }
};

// Categorization keywords
const KEYWORDS = {
  'Setup help': ['how to', 'confused', 'help', 'tutorial', 'guide', 'setup', 'install', 'configure', 'problem', 'error', 'not working', 'stuck', 'instructions'],
  'Newsletter': ['newsletter', 'email list', 'subscribe', 'updates', 'notifications', 'mailing list', 'sign up', 'stay updated'],
  'Product inquiry': ['buy', 'purchase', 'price', 'pricing', 'cost', 'product', 'which one', 'recommend', 'interested in', 'how much'],
  'Partnership': ['collaborate', 'partnership', 'brand deal', 'sponsorship', 'business', 'cooperation', 'work together', 'affiliate', 'opportunity']
};

class YouTubeDMMonitor {
  constructor() {
    this.cache = this.loadCache();
    this.timestamp = TIMESTAMP;
    this.newDMs = [];
  }

  loadCache() {
    if (!fs.existsSync(CACHE_FILE)) {
      return { processed: {}, stats: { total: 0, auto_responses: 0, conversions: 0 } };
    }
    // Parse JSONL file
    const lines = fs.readFileSync(CACHE_FILE, 'utf-8').split('\n').filter(l => l && !l.startsWith('#'));
    const processed = {};
    lines.forEach(line => {
      try {
        const obj = JSON.parse(line);
        processed[obj.sender_id] = obj;
      } catch (e) {
        // Skip invalid JSON
      }
    });
    return { processed, stats: { total: 0, auto_responses: 0, conversions: 0 } };
  }

  saveCache(dm) {
    const line = JSON.stringify(dm) + '\n';
    fs.appendFileSync(CACHE_FILE, line);
  }

  categorizeDM(text) {
    const lower = text.toLowerCase();
    let maxScore = 0;
    let bestCategory = 'Setup help'; // default

    for (const [category, keywords] of Object.entries(KEYWORDS)) {
      const score = keywords.filter(kw => lower.includes(kw)).length;
      if (score > maxScore) {
        maxScore = score;
        bestCategory = category;
      }
    }

    return bestCategory;
  }

  async processDM(sender, senderId, text) {
    const category = this.categorizeDM(text);
    const dmId = crypto.createHash('md5').update(`${senderId}${text}${this.timestamp}`).digest('hex');
    
    // Check if already processed
    if (this.cache.processed[senderId]) {
      return null;
    }

    const template = TEMPLATES[category];
    const dm = {
      timestamp: this.timestamp,
      sender,
      sender_id: senderId,
      text,
      category,
      dm_id: dmId,
      response_sent: true,
      response_subject: template.subject,
      response_text: template.body
    };

    this.saveCache(dm);
    this.newDMs.push(dm);

    // Track stats
    this.cache.stats.total++;
    this.cache.stats.auto_responses++;
    if (category === 'Product inquiry') {
      this.cache.stats.conversions++;
    }

    return dm;
  }

  flagPartnership(dm) {
    return dm.category === 'Partnership';
  }

  async generateReport() {
    const flaggedPartnerships = this.newDMs.filter(dm => this.flagPartnership(dm));
    
    const report = {
      timestamp: this.timestamp,
      summary: {
        total_dms_processed: this.newDMs.length,
        auto_responses_sent: this.newDMs.length,
        conversion_potential: this.newDMs.filter(dm => dm.category === 'Product inquiry').length,
        partnerships_flagged: flaggedPartnerships.length
      },
      breakdown_by_category: {},
      flagged_partnerships: flaggedPartnerships,
      new_dms: this.newDMs
    };

    // Count by category
    this.newDMs.forEach(dm => {
      if (!report.breakdown_by_category[dm.category]) {
        report.breakdown_by_category[dm.category] = 0;
      }
      report.breakdown_by_category[dm.category]++;
    });

    return report;
  }
}

// Main execution
async function main() {
  const monitor = new YouTubeDMMonitor();

  // Note: In real implementation, this would fetch actual DMs from YouTube API or browser automation
  // For now, we'll provide example data structure
  
  console.log('YouTube DM Monitor - Cron Job');
  console.log(`Running at: ${TIMESTAMP}`);
  console.log('');

  // Example: Process sample DMs (replace with actual YouTube API calls)
  const sampleDMs = [
    // { sender: 'User123', id: 'user_123', text: 'How do I set this up? I\'m confused' },
    // { sender: 'BrandXYZ', id: 'brand_xyz', text: 'We\'d love to collaborate with you!' },
    // { sender: 'Interested', id: 'interested_001', text: 'What\'s the price for product 1?' }
  ];

  for (const dm of sampleDMs) {
    const result = await monitor.processDM(dm.sender, dm.id, dm.text);
    if (result) {
      console.log(`✓ Processed: ${dm.sender} - Category: ${result.category}`);
    }
  }

  // Generate and display report
  const report = await monitor.generateReport();
  console.log('\n=== REPORT ===');
  console.log(JSON.stringify(report, null, 2));

  // Save report
  const reportFile = path.join(process.env.HOME, '.openclaw/.cache/youtube-dms-report.json');
  fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
  console.log(`\nReport saved to: ${reportFile}`);
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
