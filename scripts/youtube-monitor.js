#!/usr/bin/env node

/**
 * YouTube Comment Monitor - Runs every 30 minutes
 * Monitors Concessa Obvius channel for new comments
 * Categories: Questions | Praise | Spam | Sales (review-only)
 */

const fs = require('fs');
const path = require('path');
const { google } = require('googleapis');

const CACHE_DIR = path.join(__dirname, '../.cache');
const COMMENTS_LOG = path.join(CACHE_DIR, 'youtube-comments.jsonl');
const STATE_FILE = path.join(CACHE_DIR, 'youtube-monitor-state.json');

// Ensure cache directory exists
if (!fs.existsSync(CACHE_DIR)) {
  fs.mkdirSync(CACHE_DIR, { recursive: true });
}

// Template responses
const TEMPLATES = {
  questions: `Thanks for your question! I appreciate your interest. I'm getting back to you with detailed info about {topic}. Check your email shortly!`,
  praise: `Thank you so much! 🙏 This means the world to me. Keep pushing forward — we're all learning together.`
};

// Categorization rules
function categorizeComment(text) {
  const lower = text.toLowerCase();
  
  // Spam patterns
  if (/crypto|bitcoin|ethereum|nft|mlm|"work from home"|"easy money"|discord\s+server|telegram/i.test(lower)) {
    return 'spam';
  }
  
  // Sales/Partnership patterns
  if (/partnership|collaboration|sponsor|brand deal|affiliate|promote|featured|collab\s+with/i.test(lower)) {
    return 'sales';
  }
  
  // Question patterns
  if (/\?|how|what|where|when|why|can i|should i|cost|price|timeline|tools|tutorial|where to start/i.test(lower)) {
    return 'questions';
  }
  
  // Praise patterns
  if (/amazing|inspiring|love|awesome|great|incredible|brilliant|thank you|appreciate|life-changing|helped|saved/i.test(lower)) {
    return 'praise';
  }
  
  return 'neutral'; // No auto-response
}

async function loadState() {
  if (fs.existsSync(STATE_FILE)) {
    return JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
  }
  return {
    lastChecked: 0,
    processedCommentIds: new Set()
  };
}

async function saveState(state) {
  fs.writeFileSync(STATE_FILE, JSON.stringify({
    ...state,
    processedCommentIds: Array.from(state.processedCommentIds)
  }, null, 2));
}

async function logComment(comment) {
  const entry = {
    timestamp: new Date().toISOString(),
    commenter: comment.authorDisplayName,
    comment_id: comment.id,
    video_id: comment.videoId,
    text: comment.textDisplay,
    category: comment.category,
    response_status: comment.response_status,
    response_id: comment.response_id || null
  };
  
  fs.appendFileSync(COMMENTS_LOG, JSON.stringify(entry) + '\n');
}

async function respondToComment(youtube, commentId, text) {
  try {
    const response = await youtube.comments.insert({
      part: 'snippet',
      requestBody: {
        snippet: {
          parentId: commentId,
          textOriginal: text
        }
      }
    });
    return response.data.id;
  } catch (err) {
    console.error(`Failed to respond to comment ${commentId}:`, err.message);
    return null;
  }
}

async function main() {
  try {
    // Load credentials from environment or file
    const credentials = JSON.parse(
      process.env.YOUTUBE_CREDENTIALS || 
      fs.readFileSync(path.join(process.env.HOME, '.youtube-credentials.json'), 'utf-8')
    );
    
    const oauth2Client = new google.auth.OAuth2(
      credentials.client_id,
      credentials.client_secret,
      credentials.redirect_uris[0]
    );
    
    oauth2Client.setCredentials(credentials.tokens);
    
    const youtube = google.youtube({
      version: 'v3',
      auth: oauth2Client
    });
    
    const state = await loadState();
    
    // Fetch channel ID for "Concessa Obvius"
    const channelRes = await youtube.search.list({
      part: 'snippet',
      q: 'Concessa Obvius',
      type: 'channel',
      maxResults: 1
    });
    
    if (!channelRes.data.items.length) {
      throw new Error('Channel "Concessa Obvius" not found');
    }
    
    const channelId = channelRes.data.items[0].id.channelId;
    console.log(`✓ Found channel: ${channelId}`);
    
    // Get all uploads playlist
    const channelDetails = await youtube.channels.list({
      part: 'contentDetails',
      id: channelId
    });
    
    const uploadsPlaylistId = channelDetails.data.items[0].contentDetails.relatedPlaylists.uploads;
    
    // Fetch recent videos
    const videosRes = await youtube.playlistItems.list({
      part: 'snippet',
      playlistId: uploadsPlaylistId,
      maxResults: 5
    });
    
    const stats = {
      processed: 0,
      autoResponded: 0,
      flaggedForReview: 0,
      byCategory: { questions: 0, praise: 0, spam: 0, sales: 0, neutral: 0 }
    };
    
    // Check comments on each video
    for (const video of videosRes.data.items) {
      const videoId = video.snippet.resourceId.videoId;
      
      const commentsRes = await youtube.commentThreads.list({
        part: 'snippet',
        videoId: videoId,
        maxResults: 100,
        order: 'relevance',
        searchTerms: ''
      });
      
      for (const thread of commentsRes.data.items || []) {
        const comment = thread.snippet.topLevelComment.snippet;
        const commentId = thread.id;
        
        // Skip if already processed
        if (state.processedCommentIds.has(commentId)) continue;
        
        state.processedCommentIds.add(commentId);
        stats.processed++;
        
        // Categorize
        const category = categorizeComment(comment.textDisplay);
        stats.byCategory[category]++;
        
        let responseStatus = 'none';
        let responseId = null;
        
        // Auto-respond to questions and praise
        if (category === 'questions') {
          const response = await respondToComment(
            youtube,
            commentId,
            TEMPLATES.questions.replace('{topic}', 'your question')
          );
          responseStatus = response ? 'sent' : 'failed';
          responseId = response;
          if (response) stats.autoResponded++;
        } else if (category === 'praise') {
          const response = await respondToComment(
            youtube,
            commentId,
            TEMPLATES.praise
          );
          responseStatus = response ? 'sent' : 'failed';
          responseId = response;
          if (response) stats.autoResponded++;
        } else if (category === 'sales') {
          responseStatus = 'flagged_review';
          stats.flaggedForReview++;
        }
        
        // Log entry
        await logComment({
          id: commentId,
          videoId: videoId,
          authorDisplayName: comment.authorDisplayName,
          textDisplay: comment.textDisplay,
          category,
          response_status: responseStatus,
          response_id: responseId
        });
      }
    }
    
    await saveState(state);
    
    // Report
    console.log('\n📊 YOUTUBE COMMENT MONITOR REPORT');
    console.log('='.repeat(50));
    console.log(`Total comments processed: ${stats.processed}`);
    console.log(`Auto-responses sent: ${stats.autoResponded}`);
    console.log(`Flagged for review (Sales): ${stats.flaggedForReview}`);
    console.log(`\nBy Category:`);
    console.log(`  Questions: ${stats.byCategory.questions}`);
    console.log(`  Praise: ${stats.byCategory.praise}`);
    console.log(`  Spam: ${stats.byCategory.spam}`);
    console.log(`  Sales: ${stats.byCategory.sales}`);
    console.log(`  Neutral: ${stats.byCategory.neutral}`);
    console.log('='.repeat(50));
    
  } catch (err) {
    console.error('❌ Error:', err.message);
    process.exit(1);
  }
}

main();
