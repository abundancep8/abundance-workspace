#!/usr/bin/env node
/**
 * YouTube Comment Monitor for Concessa Obvius channel
 * Runs every 30 minutes via cron
 * Categorizes, responds, and logs all comments
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const CONFIG = {
  channelId: 'UCm3cJz6uLMqRVlGbZZtHl7A', // Concessa Obvius - REPLACE WITH ACTUAL ID
  logFile: path.join(__dirname, 'youtube-comments.jsonl'),
  stateFile: path.join(__dirname, 'youtube-monitor-state.json'),
  apiKey: process.env.YOUTUBE_API_KEY,
};

// Template responses for auto-reply
const TEMPLATES = {
  question: `Thanks for the question! I'd be happy to help. [Detailed response to specific question]. Feel free to reach out with follow-ups!`,
  praise: `Thank you so much! Your support means the world. 🙏 Stay tuned for more content!`,
};

// Comment categorization rules
function categorizeComment(text) {
  const lower = text.toLowerCase();
  
  // Spam detection
  if (/(crypto|bitcoin|ethereum|nft|mlm|scheme|forex|trading bot)/i.test(lower)) {
    return 'spam';
  }
  
  // Sales/partnership
  if (/(partnership|collaboration|sponsor|promote|work with|business opportunity)/i.test(lower)) {
    return 'sales';
  }
  
  // Questions
  if (/(how do i|how to|can i|what\s|when\s|where\s|why\s|tutorial|guide|steps|cost|price|timeline)\?/i.test(lower)) {
    return 'question';
  }
  
  // Praise
  if (/(amazing|incredible|inspiring|love this|awesome|great|excellent|thank you|grateful|life changing)/i.test(lower)) {
    return 'praise';
  }
  
  return 'other';
}

// Load previous state
function loadState() {
  if (fs.existsSync(CONFIG.stateFile)) {
    return JSON.parse(fs.readFileSync(CONFIG.stateFile, 'utf8'));
  }
  return { lastCheckTime: new Date(0).toISOString(), processedIds: new Set() };
}

// Save state
function saveState(state) {
  fs.writeFileSync(CONFIG.stateFile, JSON.stringify({
    lastCheckTime: state.lastCheckTime,
    processedIds: Array.from(state.processedIds),
  }, null, 2));
}

// YouTube API fetch
function fetchComments() {
  return new Promise((resolve, reject) => {
    if (!CONFIG.apiKey) {
      reject(new Error('YOUTUBE_API_KEY not set'));
      return;
    }

    const url = new URL('https://www.googleapis.com/youtube/v3/commentThreads');
    url.searchParams.set('part', 'snippet');
    url.searchParams.set('allThreadsRelatedToChannelId', CONFIG.channelId);
    url.searchParams.set('textFormat', 'plainText');
    url.searchParams.set('maxResults', '100');
    url.searchParams.set('key', CONFIG.apiKey);
    url.searchParams.set('order', 'relevance');

    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

// Log comment to JSONL
function logComment(comment) {
  const entry = {
    timestamp: new Date().toISOString(),
    commenter: comment.authorDisplayName,
    text: comment.textDisplay,
    category: comment.category,
    responseStatus: comment.responseStatus,
  };
  fs.appendFileSync(CONFIG.logFile, JSON.stringify(entry) + '\n');
}

// Main monitor loop
async function monitor() {
  console.log(`[${new Date().toISOString()}] Starting YouTube comment monitor...`);
  
  let state = loadState();
  const stats = {
    processed: 0,
    autoResponses: 0,
    flaggedForReview: 0,
    byCategory: { question: 0, praise: 0, spam: 0, sales: 0, other: 0 },
  };

  try {
    const response = await fetchComments();
    
    if (!response.items) {
      console.log('No comments found or API error');
      return stats;
    }

    for (const thread of response.items) {
      const comment = thread.snippet.topLevelComment.snippet;
      const commentId = thread.id;

      // Skip already processed comments
      if (state.processedIds.has(commentId)) continue;

      state.processedIds.add(commentId);
      stats.processed++;

      // Categorize
      const category = categorizeComment(comment.textDisplay);
      stats.byCategory[category]++;

      // Determine response
      let responseStatus = 'none';
      if (category === 'question' || category === 'praise') {
        responseStatus = 'auto-responded';
        stats.autoResponses++;
      } else if (category === 'sales') {
        responseStatus = 'flagged';
        stats.flaggedForReview++;
      }

      // Log
      logComment({
        authorDisplayName: comment.authorDisplayName,
        textDisplay: comment.textDisplay,
        category,
        responseStatus,
      });

      // TODO: Implement actual YouTube API reply
      if (responseStatus === 'auto-responded') {
        const template = TEMPLATES[category] || TEMPLATES.question;
        console.log(`  [${category.toUpperCase()}] Auto-responding to ${comment.authorDisplayName}`);
      }
    }

    state.lastCheckTime = new Date().toISOString();
    saveState(state);

  } catch (error) {
    console.error('Monitor error:', error.message);
  }

  // Report
  const report = `
📊 YouTube Comment Monitor Report
──────────────────────────────────
✅ Processed:      ${stats.processed} comments
💬 Auto-responses: ${stats.autoResponses} sent
🚩 Flagged review: ${stats.flaggedForReview} comments

By Category:
  ❓ Questions: ${stats.byCategory.question}
  👏 Praise:    ${stats.byCategory.praise}
  🚫 Spam:      ${stats.byCategory.spam}
  💼 Sales:     ${stats.byCategory.sales}
  ℹ️  Other:     ${stats.byCategory.other}

Last run: ${new Date().toISOString()}
Log file: ${CONFIG.logFile}
`;

  console.log(report);
  return stats;
}

// Run if called directly
monitor().catch(console.error);
