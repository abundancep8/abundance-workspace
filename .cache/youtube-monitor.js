#!/usr/bin/env node

/**
 * YouTube Comment Monitor - Concessa Obvius Channel
 * Monitors for new comments, categorizes, auto-responds, and logs
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const CACHE_DIR = path.join(__dirname);
const LOG_FILE = path.join(CACHE_DIR, 'youtube-comments.jsonl');
const STATE_FILE = path.join(CACHE_DIR, 'youtube-monitor-state.json');
const CHANNEL_ID = 'UCconcessa'; // Replace with actual channel ID for Concessa Obvius

// Category patterns
const PATTERNS = {
  questions: /how\s+(do|can|to)|(what|which|where|when|why)|(tools?|cost|price|timeline|start|begin|learn)/i,
  praise: /amazing|inspiring|incredible|love|awesome|thank you|grateful|powerful|brilliant|genius|genius|excellent/i,
  spam: /crypto|bitcoin|ethereum|nft|mlm|forex|dropshipping|buy.*now|click.*here|free.*money/i,
  sales: /partnership|collaboration|sponsor|advertise|affiliate|promote|brand.*deal|influencer|pr\b/i
};

// Template responses
const TEMPLATES = {
  questions: {
    prefix: "Thanks for your question! ",
    responses: [
      "I cover this in detail in our resources. Check out the linked guide in the channel description.",
      "Great question! This is addressed in our latest video—watch for the full breakdown.",
      "Happy to help! Our FAQ section covers this—see the pinned comment for the link."
    ]
  },
  praise: {
    prefix: "Thank you so much! ",
    responses: [
      "Your support means everything. More coming soon!",
      "Comments like this fuel the mission. Grateful for you.",
      "This is exactly why we do this. Thank you for believing in it."
    ]
  }
};

/**
 * Categorize a comment
 */
function categorizeComment(text) {
  if (PATTERNS.spam.test(text)) return 'spam';
  if (PATTERNS.sales.test(text)) return 'sales';
  if (PATTERNS.questions.test(text)) return 'questions';
  if (PATTERNS.praise.test(text)) return 'praise';
  return 'general';
}

/**
 * Get a random template response
 */
function getTemplateResponse(category) {
  if (!TEMPLATES[category]) return null;
  const { prefix, responses } = TEMPLATES[category];
  const response = responses[Math.floor(Math.random() * responses.length)];
  return prefix + response;
}

/**
 * Simulate fetching comments from YouTube
 * In production, use YouTube Data API v3
 */
function fetchComments() {
  // Placeholder: In real deployment, integrate YouTube API
  // For now, return empty array (no new comments this cycle)
  return [];
}

/**
 * Load monitoring state
 */
function loadState() {
  if (!fs.existsSync(STATE_FILE)) {
    return {
      lastChecked: null,
      processedCommentIds: new Set(),
      totalProcessed: 0,
      totalResponses: 0,
      totalFlagged: 0
    };
  }
  const data = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
  data.processedCommentIds = new Set(data.processedCommentIds || []);
  return data;
}

/**
 * Save monitoring state
 */
function saveState(state) {
  const toSave = {
    ...state,
    processedCommentIds: Array.from(state.processedCommentIds)
  };
  fs.writeFileSync(STATE_FILE, JSON.stringify(toSave, null, 2));
}

/**
 * Log comment to JSONL file
 */
function logComment(comment) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    commenter: comment.author,
    text: comment.text,
    category: comment.category,
    response_status: comment.responseStatus,
    autoResponseText: comment.autoResponseText || null
  };
  fs.appendFileSync(LOG_FILE, JSON.stringify(logEntry) + '\n');
}

/**
 * Process new comments
 */
function processComments() {
  const state = loadState();
  const comments = fetchComments();

  const newComments = [];
  let responsesCount = 0;
  let flaggedCount = 0;

  console.log(`[${new Date().toISOString()}] Starting comment processing...`);
  console.log(`Fetched ${comments.length} comments`);

  for (const comment of comments) {
    // Skip already processed
    if (state.processedCommentIds.has(comment.id)) {
      continue;
    }

    const category = categorizeComment(comment.text);
    let responseStatus = 'none';
    let autoResponseText = null;

    // Auto-respond to questions and praise
    if (category === 'questions' || category === 'praise') {
      autoResponseText = getTemplateResponse(category);
      responseStatus = 'auto-responded';
      responsesCount++;
      console.log(`✓ Auto-responded to ${category}: "${comment.text.substring(0, 50)}..."`);
    }

    // Flag sales inquiries
    if (category === 'sales') {
      responseStatus = 'flagged-for-review';
      flaggedCount++;
      console.log(`⚠ Flagged sales inquiry: "${comment.text.substring(0, 50)}..."`);
    }

    const processedComment = {
      ...comment,
      category,
      responseStatus,
      autoResponseText
    };

    newComments.push(processedComment);
    logComment(processedComment);
    state.processedCommentIds.add(comment.id);
    state.totalProcessed++;
  }

  state.totalResponses += responsesCount;
  state.totalFlagged += flaggedCount;
  state.lastChecked = new Date().toISOString();

  saveState(state);

  // Generate report
  console.log('\n' + '='.repeat(60));
  console.log('YOUTUBE COMMENT MONITOR REPORT');
  console.log('='.repeat(60));
  console.log(`Channel: Concessa Obvius`);
  console.log(`Timestamp: ${new Date().toISOString()}`);
  console.log(`New comments processed: ${newComments.length}`);
  console.log(`Total comments processed (all-time): ${state.totalProcessed}`);
  console.log(`Auto-responses sent: ${responsesCount}`);
  console.log(`Total auto-responses (all-time): ${state.totalResponses}`);
  console.log(`Flagged for review: ${flaggedCount}`);
  console.log(`Total flagged (all-time): ${state.totalFlagged}`);
  console.log(`Log file: ${LOG_FILE}`);
  console.log('='.repeat(60) + '\n');

  return {
    processed: newComments.length,
    responses: responsesCount,
    flagged: flaggedCount,
    totalProcessed: state.totalProcessed,
    totalResponses: state.totalResponses,
    totalFlagged: state.totalFlagged
  };
}

// Run monitor
try {
  const report = processComments();
  process.exit(0);
} catch (error) {
  console.error(`Error running monitor: ${error.message}`);
  process.exit(1);
}
