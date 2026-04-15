#!/usr/bin/env node
/**
 * YouTube DM Monitor & Auto-Responder
 * 
 * Processes DMs from a webhook/queue and:
 * - Categorizes by intent
 * - Auto-responds with templates
 * - Logs to jsonl
 * - Reports metrics
 */

const fs = require('fs');
const path = require('path');

const DM_LOG = path.join(__dirname, '../.cache/youtube-dms.jsonl');
const TEMPLATES = {
  'setup-help': `Thanks for reaching out! I'd be happy to help you get set up. Could you describe which step you're stuck on? I'll send over specific guidance.`,
  'newsletter': `Great to hear! You can join our newsletter here: [LINK]. You'll get exclusive updates, new features, and insider tips.`,
  'product-inquiry': `Thanks for your interest! I'd love to help you find the right solution. What are you looking to accomplish? I can send over pricing and details.`,
  'partnership': `This sounds interesting! Let me loop in our partnerships team. They'll reach out within 24 hours to explore this further.`
};

/**
 * Categorize a DM by intent
 */
function categorizeDM(text) {
  const lower = text.toLowerCase();
  
  if (/how|set.*up|confused|help.*start|install|guide|tutorial|stuck/i.test(lower)) {
    return 'setup-help';
  }
  if (/subscribe|newsletter|email.*list|updates|news|follow/i.test(lower)) {
    return 'newsletter';
  }
  if (/buy|price|cost|purchase|plan|feature|product|interested|available/i.test(lower)) {
    return 'product-inquiry';
  }
  if (/partner|collaborate|sponsor|collab|brand.*deal|affiliate|ambassador/i.test(lower)) {
    return 'partnership';
  }
  
  return 'general'; // fallback
}

/**
 * Process a single DM
 */
function processDM(dm) {
  const category = categorizeDM(dm.text || '');
  const response = TEMPLATES[category] || TEMPLATES['setup-help'];
  const timestamp = new Date().toISOString();
  
  const record = {
    timestamp,
    sender: dm.sender || 'unknown',
    text: dm.text || '',
    category,
    response_sent: response,
    flagged_for_review: category === 'partnership'
  };
  
  // Append to log
  fs.appendFileSync(DM_LOG, JSON.stringify(record) + '\n');
  
  return record;
}

/**
 * Generate report from log
 */
function generateReport() {
  if (!fs.existsSync(DM_LOG)) {
    return { totalProcessed: 0, autoResponsesSent: 0, conversions: [] };
  }
  
  const lines = fs.readFileSync(DM_LOG, 'utf8').split('\n').filter(Boolean);
  const records = lines.map(l => JSON.parse(l));
  
  const conversions = records
    .filter(r => r.category === 'product-inquiry')
    .map(r => ({ sender: r.sender, timestamp: r.timestamp, text: r.text }));
  
  return {
    totalProcessed: records.length,
    autoResponsesSent: records.length,
    productInquiries: records.filter(r => r.category === 'product-inquiry').length,
    partnerships: records.filter(r => r.flagged_for_review).length,
    byCategory: {
      'setup-help': records.filter(r => r.category === 'setup-help').length,
      'newsletter': records.filter(r => r.category === 'newsletter').length,
      'product-inquiry': records.filter(r => r.category === 'product-inquiry').length,
      'partnership': records.filter(r => r.category === 'partnership').length
    }
  };
}

// If run directly with stdin
if (require.main === module) {
  const input = process.argv[2];
  
  if (input === '--report') {
    console.log(JSON.stringify(generateReport(), null, 2));
  } else if (input) {
    try {
      const dm = JSON.parse(input);
      const record = processDM(dm);
      console.log(JSON.stringify(record));
    } catch (e) {
      console.error('Invalid input:', e.message);
    }
  } else {
    console.log('Usage: youtube-dm-processor.js [--report] [dm-json]');
  }
}

module.exports = { processDM, categorizeDM, generateReport };
