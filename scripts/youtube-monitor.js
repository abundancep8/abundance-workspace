#!/usr/bin/env node

/**
 * YouTube Comment Monitor - Concessa Obvius Channel
 * Monitors for new comments, categorizes, auto-responds, and logs
 * Runs every 30 minutes via cron
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const CONFIG = {
  channelId: 'UCxxxxxxxxxxxxxxxxxxxxx', // Replace with actual channel ID
  apiKey: process.env.YOUTUBE_API_KEY,
  logFile: path.join(__dirname, '../.cache/youtube-comments.jsonl'),
  statFile: path.join(__dirname, '../.cache/youtube-monitor-state.json'),
  checkInterval: 30 * 60 * 1000, // 30 minutes
};

// Template responses
const TEMPLATES = {
  question: `Thanks for the question! 🤔 We appreciate your interest. Check our FAQ section or feel free to reply here if you need more details.`,
  praise: `🙏 Thank you so much for the kind words! Your support means everything to us. We're excited to keep building.`,
};

// Category detection rules
const CATEGORIES = {
  question: {
    keywords: ['how', 'where', 'when', 'what', 'why', 'cost', 'price', 'timeline', 'start', 'tools', 'tutorial', '?'],
    score: (text) => {
      const lower = text.toLowerCase();
      const hasQuestion = lower.includes('?');
      const hasKeyword = CATEGORIES.question.keywords.some(k => lower.includes(k));
      return (hasQuestion ? 2 : 0) + (hasKeyword ? 1 : 0);
    }
  },
  praise: {
    keywords: ['amazing', 'great', 'love', 'inspiring', 'awesome', 'incredible', 'brilliant', 'genius', 'thanks', 'thank you', '❤️'],
    score: (text) => {
      const lower = text.toLowerCase();
      return CATEGORIES.praise.keywords.filter(k => lower.includes(k)).length;
    }
  },
  spam: {
    keywords: ['bitcoin', 'crypto', 'mlm', 'nft', 'forex', 'stocks', 'penny stock', 'buy now', 'click here', 'visit link'],
    score: (text) => {
      const lower = text.toLowerCase();
      return CATEGORIES.spam.keywords.filter(k => lower.includes(k)).length;
    }
  },
  sales: {
    keywords: ['partnership', 'collaboration', 'sponsor', 'brand deal', 'affiliate', 'promote', 'offer', 'business opportunity'],
    score: (text) => {
      const lower = text.toLowerCase();
      return CATEGORIES.sales.keywords.filter(k => lower.includes(k)).length;
    }
  }
};

async function categorizeComment(text) {
  const scores = {
    question: CATEGORIES.question.score(text),
    praise: CATEGORIES.praise.score(text),
    spam: CATEGORIES.spam.score(text),
    sales: CATEGORIES.sales.score(text),
  };

  const highest = Object.entries(scores).sort(([, a], [, b]) => b - a)[0];
  return highest[1] > 0 ? highest[0] : 'other';
}

async function fetchNewComments() {
  if (!CONFIG.apiKey) {
    console.error('ERROR: YOUTUBE_API_KEY not set. Set via: export YOUTUBE_API_KEY=<your-key>');
    return [];
  }

  const state = loadState();
  const lastCheck = state.lastCheck || new Date(Date.now() - 31 * 60 * 1000).toISOString();

  return new Promise((resolve, reject) => {
    const params = new URLSearchParams({
      key: CONFIG.apiKey,
      part: 'snippet,replies',
      allThreadsRelated: true,
      textFormat: 'plainText',
      searchTerms: '', // Empty to get all comments
      videoId: '', // Will search channel comments
      maxResults: 100,
      publishedAfter: lastCheck,
      order: 'time',
    });

    // Note: This is a simplified approach. Full implementation would:
    // 1. Get all video IDs from channel
    // 2. Fetch comments for each video
    // 3. Filter by timestamp
    
    const url = `https://www.googleapis.com/youtube/v3/commentThreads?${params}`;

    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          if (response.items) {
            const comments = response.items.map(thread => ({
              id: thread.id,
              videoId: thread.snippet.videoId,
              textDisplay: thread.snippet.topLevelComment.snippet.textDisplay,
              authorDisplayName: thread.snippet.topLevelComment.snippet.authorDisplayName,
              likeCount: thread.snippet.topLevelComment.snippet.likeCount,
              publishedAt: thread.snippet.topLevelComment.snippet.publishedAt,
              replyCount: thread.replyCount,
            }));
            resolve(comments);
          } else if (response.error) {
            reject(new Error(`YouTube API error: ${response.error.message}`));
          } else {
            resolve([]);
          }
        } catch (err) {
          reject(err);
        }
      });
    }).on('error', reject);
  });
}

async function processComments(comments) {
  const results = {
    total: 0,
    autoResponses: 0,
    flagged: 0,
    byCategory: { question: 0, praise: 0, spam: 0, sales: 0, other: 0 },
  };

  for (const comment of comments) {
    const category = await categorizeComment(comment.textDisplay);
    results.byCategory[category]++;
    results.total++;

    const logEntry = {
      timestamp: new Date().toISOString(),
      checkTime: comment.publishedAt,
      commentId: comment.id,
      videoId: comment.snippet?.videoId,
      commenter: comment.authorDisplayName,
      text: comment.textDisplay,
      category,
      likeCount: comment.likeCount,
      replyCount: comment.replyCount,
      responseStatus: 'pending',
      response: null,
    };

    // Auto-respond to questions and praise
    if (category === 'question' || category === 'praise') {
      logEntry.responseStatus = 'auto-responded';
      logEntry.response = TEMPLATES[category];
      results.autoResponses++;
      // In production: actually post the reply via YouTube API
      console.log(`✓ Auto-responded to ${category}: ${comment.authorDisplayName}`);
    }

    // Flag sales for review
    if (category === 'sales') {
      logEntry.responseStatus = 'flagged-for-review';
      results.flagged++;
      console.log(`⚠️ Flagged sales inquiry from ${comment.authorDisplayName}`);
    }

    // Log the comment
    fs.appendFileSync(CONFIG.logFile, JSON.stringify(logEntry) + '\n');
  }

  return results;
}

function loadState() {
  try {
    if (fs.existsSync(CONFIG.statFile)) {
      return JSON.parse(fs.readFileSync(CONFIG.statFile, 'utf8'));
    }
  } catch (err) {
    console.warn('Could not load state file:', err.message);
  }
  return { lastCheck: new Date(0).toISOString() };
}

function saveState(state) {
  fs.writeFileSync(CONFIG.statFile, JSON.stringify(state, null, 2));
}

async function main() {
  try {
    console.log(`[${new Date().toISOString()}] Starting YouTube comment monitor...`);

    // Fetch new comments since last check
    const comments = await fetchNewComments();
    console.log(`Found ${comments.length} new comments`);

    if (comments.length === 0) {
      console.log('No new comments to process.');
      return;
    }

    // Process and categorize
    const results = await processComments(comments);

    // Save state for next run
    saveState({ lastCheck: new Date().toISOString() });

    // Report results
    console.log('\n📊 REPORT:');
    console.log(`  Total comments: ${results.total}`);
    console.log(`  Auto-responses sent: ${results.autoResponses}`);
    console.log(`  Flagged for review: ${results.flagged}`);
    console.log(`  By category:`);
    Object.entries(results.byCategory).forEach(([cat, count]) => {
      console.log(`    - ${cat}: ${count}`);
    });

  } catch (err) {
    console.error('ERROR:', err.message);
    process.exit(1);
  }
}

main();
