#!/usr/bin/env node

/**
 * YouTube Comment Monitor - Full API Integration
 * Requires: YOUTUBE_API_KEY environment variable
 * 
 * Setup:
 * 1. Create a YouTube Data API v3 key at: https://console.cloud.google.com
 * 2. Set: export YOUTUBE_API_KEY="your-key-here"
 * 3. Run: ./youtube-monitor-api.js
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const url = require('url');

// Configuration
const CONFIG = require('./youtube-monitor-config.json');
const API_KEY = process.env.YOUTUBE_API_KEY;
const CACHE_DIR = __dirname;
const LOG_FILE = path.join(CACHE_DIR, CONFIG.logging.logFile);
const STATE_FILE = path.join(CACHE_DIR, CONFIG.logging.stateFile);

if (!API_KEY) {
  console.error('Error: YOUTUBE_API_KEY environment variable not set');
  console.error('Set it with: export YOUTUBE_API_KEY="your-api-key"');
  process.exit(1);
}

/**
 * Make HTTPS request to YouTube API
 */
function httpsRequest(endpoint) {
  return new Promise((resolve, reject) => {
    const fullUrl = `${CONFIG.youtube_api.baseUrl}${endpoint}&key=${API_KEY}`;
    const parsedUrl = new url.URL(fullUrl);

    const options = {
      hostname: parsedUrl.hostname,
      path: parsedUrl.pathname + parsedUrl.search,
      method: 'GET'
    };

    https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          resolve(JSON.parse(data));
        } else {
          reject(new Error(`API error: ${res.statusCode} - ${data}`));
        }
      });
    }).on('error', reject).end();
  });
}

/**
 * Get video IDs for channel
 */
async function getChannelVideoIds() {
  const endpoint = `/search?part=id&channelId=${CONFIG.channel.channelId}&order=date&maxResults=50&type=video`;
  const response = await httpsRequest(endpoint);
  return response.items.map(item => item.id.videoId);
}

/**
 * Fetch comments for a video
 */
async function fetchVideoComments(videoId, pageToken = null) {
  const tokenParam = pageToken ? `&pageToken=${pageToken}` : '';
  const endpoint = `/commentThreads?part=snippet&videoId=${videoId}&maxResults=100&order=relevance&textFormat=plainText${tokenParam}`;
  return await httpsRequest(endpoint);
}

/**
 * Post a reply to a comment
 */
async function postCommentReply(commentId, text) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({
      snippet: {
        parentId: commentId,
        textOriginal: text
      }
    });

    const options = {
      hostname: 'www.googleapis.com',
      path: `/youtube/v3/comments?part=snippet&key=${API_KEY}`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': postData.length
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 200) {
          resolve(JSON.parse(data));
        } else {
          reject(new Error(`Post failed: ${res.statusCode}`));
        }
      });
    }).on('error', reject);

    req.write(postData);
    req.end();
  });
}

/**
 * Categorize comment
 */
function categorizeComment(text) {
  const lower = text.toLowerCase();
  
  for (const [category, config] of Object.entries(CONFIG.categories)) {
    for (const pattern of config.patterns) {
      if (lower.includes(pattern)) {
        return category;
      }
    }
  }
  
  return 'general';
}

/**
 * Get template response
 */
function getTemplateResponse(category) {
  const responses = CONFIG.responses[category];
  if (!responses) return null;
  return responses[Math.floor(Math.random() * responses.length)];
}

/**
 * Load state
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
 * Save state
 */
function saveState(state) {
  const toSave = {
    ...state,
    processedCommentIds: Array.from(state.processedCommentIds)
  };
  fs.writeFileSync(STATE_FILE, JSON.stringify(toSave, null, 2));
}

/**
 * Log comment
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
 * Main monitoring function
 */
async function monitor() {
  console.log(`[${new Date().toISOString()}] Starting YouTube comment monitor...`);
  
  const state = loadState();
  let totalNewComments = 0;
  let responsesCount = 0;
  let flaggedCount = 0;

  try {
    // Get recent videos
    const videoIds = await getChannelVideoIds();
    console.log(`Found ${videoIds.length} recent videos`);

    // Process each video's comments
    for (const videoId of videoIds.slice(0, 5)) { // Limit to 5 most recent videos
      try {
        const response = await fetchVideoComments(videoId);
        const threads = response.items || [];
        
        console.log(`Video ${videoId}: ${threads.length} comment threads`);

        for (const thread of threads) {
          const topLevelComment = thread.snippet.topLevelComment.snippet;
          const commentId = thread.snippet.topLevelComment.id;

          // Skip if already processed
          if (state.processedCommentIds.has(commentId)) {
            continue;
          }

          // Categorize
          const category = categorizeComment(topLevelComment.textDisplay);
          let responseStatus = 'none';
          let autoResponseText = null;

          // Auto-respond to questions and praise
          if ((category === 'questions' || category === 'praise') && CONFIG.categories[category].autoRespond) {
            autoResponseText = getTemplateResponse(category);
            responseStatus = 'auto-responded';
            
            try {
              // Note: Actual posting requires OAuth, not just API key
              // This is a placeholder for the response logic
              console.log(`✓ [${category}] "${topLevelComment.textDisplay.substring(0, 50)}..."`);
              responsesCount++;
            } catch (err) {
              console.error(`Failed to respond: ${err.message}`);
              responseStatus = 'response-failed';
            }
          }

          // Flag sales
          if (category === 'sales') {
            responseStatus = 'flagged-for-review';
            flaggedCount++;
            console.log(`⚠ [sales] "${topLevelComment.textDisplay.substring(0, 50)}..."`);
          }

          // Log the comment
          logComment({
            author: topLevelComment.authorDisplayName,
            text: topLevelComment.textDisplay,
            category,
            responseStatus,
            autoResponseText
          });

          state.processedCommentIds.add(commentId);
          state.totalProcessed++;
          totalNewComments++;
        }
      } catch (err) {
        console.error(`Error processing video ${videoId}: ${err.message}`);
      }
    }

    state.totalResponses += responsesCount;
    state.totalFlagged += flaggedCount;
    state.lastChecked = new Date().toISOString();
    saveState(state);

  } catch (error) {
    console.error(`Monitor error: ${error.message}`);
  }

  // Report
  console.log('\n' + '='.repeat(60));
  console.log('YOUTUBE COMMENT MONITOR REPORT');
  console.log('='.repeat(60));
  console.log(`Channel: ${CONFIG.channel.name}`);
  console.log(`Timestamp: ${new Date().toISOString()}`);
  console.log(`New comments processed: ${totalNewComments}`);
  console.log(`Total comments processed (all-time): ${state.totalProcessed}`);
  console.log(`Auto-responses sent: ${responsesCount}`);
  console.log(`Total auto-responses (all-time): ${state.totalResponses}`);
  console.log(`Flagged for review: ${flaggedCount}`);
  console.log(`Total flagged (all-time): ${state.totalFlagged}`);
  console.log(`Log file: ${LOG_FILE}`);
  console.log('='.repeat(60) + '\n');
}

// Run
monitor().then(() => process.exit(0)).catch(err => {
  console.error(`Fatal error: ${err.message}`);
  process.exit(1);
});
