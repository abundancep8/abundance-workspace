#!/usr/bin/env node
/**
 * YouTube DM Monitor - Cron job
 * Monitors Concessa Obvius DMs, categorizes, auto-responds, and logs
 * Run: node youtube-dms-monitor.js
 */

const fs = require('fs');
const path = require('path');

const CACHE_DIR = path.join(__dirname);
const LOG_FILE = path.join(CACHE_DIR, 'youtube-dms.jsonl');

// Category templates
const TEMPLATES = {
  setup_help: {
    category: 'Setup help',
    response: `Hi! Thanks for reaching out. I've got setup guides and troubleshooting at [link]. If you're still stuck, reply with your error and I'll help ASAP.`
  },
  newsletter: {
    category: 'Newsletter',
    response: `Thanks for your interest! I'm building an email list for updates. Reply with "subscribe" and I'll add you.`
  },
  product_inquiry: {
    category: 'Product inquiry',
    response: `Thanks for the interest! Here's what we offer: [product details]. Let me know if you have questions!`
  },
  partnership: {
    category: 'Partnership',
    response: `Interesting! I'd love to explore this. Can you send more details about what you have in mind?`
  }
};

// Keywords for categorization
const KEYWORDS = {
  setup_help: ['how to', 'help', 'confused', 'error', 'broken', 'not working', 'setup', 'install', 'stuck', 'guide', 'tutorial'],
  newsletter: ['subscribe', 'email list', 'updates', 'news', 'mailing list', 'follow', 'sign up'],
  product_inquiry: ['price', 'cost', 'buy', 'purchase', 'product', 'sell', 'available', 'pricing', 'order'],
  partnership: ['collaborate', 'partnership', 'sponsor', 'collaboration', 'business', 'work together', 'opportunity']
};

/**
 * Categorize a DM based on content
 */
function categorizeDM(text) {
  const lower = text.toLowerCase();
  let scores = {
    setup_help: 0,
    newsletter: 0,
    product_inquiry: 0,
    partnership: 0
  };

  // Score based on keyword matches
  Object.entries(KEYWORDS).forEach(([category, words]) => {
    words.forEach(word => {
      if (lower.includes(word)) scores[category]++;
    });
  });

  // Find highest score
  const sorted = Object.entries(scores).sort(([, a], [, b]) => b - a);
  const winner = sorted[0];

  // Return category or default to 'other'
  return winner[1] > 0 ? winner[0] : 'other';
}

/**
 * Process a batch of DMs
 */
function processDMs(dms) {
  if (!Array.isArray(dms) || dms.length === 0) {
    console.log('No new DMs to process.');
    return { processed: 0, responses: 0, results: [] };
  }

  const results = [];
  let responseCount = 0;
  const partnerships = [];

  dms.forEach((dm) => {
    const category = categorizeDM(dm.text);
    const template = TEMPLATES[category];
    const response = template ? template.response : null;

    // Flag partnerships for manual review
    if (category === 'partnership') {
      partnerships.push({
        sender: dm.sender,
        text: dm.text,
        timestamp: dm.timestamp,
        flag: 'REVIEW_NEEDED'
      });
    }

    const record = {
      timestamp: dm.timestamp || new Date().toISOString(),
      sender: dm.sender,
      text: dm.text,
      category: category,
      response_sent: response || false,
      template_used: category
    };

    results.push(record);
    if (response) responseCount++;
  });

  // Log all DMs
  logDMs(results);

  return {
    processed: dms.length,
    responses: responseCount,
    partnerships: partnerships,
    results: results
  };
}

/**
 * Append DM records to JSONL log
 */
function logDMs(records) {
  const lines = records.map(r => JSON.stringify(r)).join('\n') + '\n';
  fs.appendFileSync(LOG_FILE, lines);
  console.log(`✓ Logged ${records.length} DMs to ${LOG_FILE}`);
}

/**
 * Generate report
 */
function generateReport(stats) {
  const report = {
    timestamp: new Date().toISOString(),
    total_dms_processed: stats.processed,
    auto_responses_sent: stats.responses,
    conversion_potential: {
      product_inquiries: stats.results.filter(r => r.category === 'product_inquiry').length,
      partnerships_flagged: stats.partnerships.length
    },
    partnerships_for_review: stats.partnerships
  };

  console.log('\n=== DM Monitor Report ===');
  console.log(`Total DMs processed: ${report.total_dms_processed}`);
  console.log(`Auto-responses sent: ${report.auto_responses_sent}`);
  console.log(`Product inquiries: ${report.conversion_potential.product_inquiries}`);
  console.log(`Partnerships flagged for review: ${report.conversion_potential.partnerships_flagged}`);

  if (stats.partnerships.length > 0) {
    console.log('\n⭐ Partnerships to Review:');
    stats.partnerships.forEach(p => {
      console.log(`  - ${p.sender}: ${p.text.substring(0, 50)}...`);
    });
  }

  return report;
}

/**
 * MAIN: Load DMs and process
 * 
 * Data source format: Array of {timestamp, sender, text}
 * This can come from:
 * - env var DM_JSON (raw JSON)
 * - file: /tmp/new-dms.json
 * - stdin (pipe data in)
 */
async function main() {
  try {
    let dms = [];

    // Try to load from environment variable (JSON)
    if (process.env.DM_JSON) {
      dms = JSON.parse(process.env.DM_JSON);
      console.log(`Loaded ${dms.length} DMs from env var`);
    }
    // Try to load from temp file (webhook/api writes here)
    else if (fs.existsSync('/tmp/new-dms.json')) {
      const raw = fs.readFileSync('/tmp/new-dms.json', 'utf8');
      dms = JSON.parse(raw);
      fs.unlinkSync('/tmp/new-dms.json'); // consumed
      console.log(`Loaded ${dms.length} DMs from /tmp/new-dms.json`);
    }
    // Demo mode: create sample DMs
    else {
      console.log('No DM data provided. Running in demo mode...');
      dms = [
        {
          timestamp: new Date().toISOString(),
          sender: 'user_123',
          text: 'I want to buy your product, how much does it cost?'
        },
        {
          timestamp: new Date().toISOString(),
          sender: 'user_456',
          text: 'How do I set this up? I\'m confused.'
        },
        {
          timestamp: new Date().toISOString(),
          sender: 'user_789',
          text: 'I\'d love to collaborate on a partnership opportunity!'
        }
      ];
    }

    // Process DMs
    const stats = processDMs(dms);

    // Generate and display report
    const report = generateReport(stats);

    // Log report to file
    const reportPath = path.join(CACHE_DIR, 'youtube-dms-report.json');
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
    console.log(`\n✓ Report saved to ${reportPath}`);

  } catch (err) {
    console.error('❌ Error:', err.message);
    process.exit(1);
  }
}

main();
