#!/usr/bin/env node

/**
 * YouTube Comment Monitor
 * Fetches comments, categorizes, auto-responds, logs to JSONL
 * Run via: node youtube-monitor.js
 */

const fs = require("fs");
const path = require("path");
const https = require("https");

const CONFIG = {
  apiKey: process.env.YOUTUBE_API_KEY,
  channelId: process.env.YOUTUBE_CHANNEL_ID || "UCEczf6sINfNpDjZqMhXYqJA", // placeholder
  cacheDir: path.join(__dirname, "."),
  commentsFile: path.join(__dirname, "youtube-comments.jsonl"),
  stateFile: path.join(__dirname, "youtube-monitor-state.json"),
  templates: {
    question: `Thanks for the question! I'll follow up with a detailed answer soon.`,
    praise: `Thank you so much for the kind words! 🙏`,
  },
};

// ============================================================================
// UTILITIES
// ============================================================================

function log(msg) {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${msg}`);
}

function loadState() {
  if (fs.existsSync(CONFIG.stateFile)) {
    return JSON.parse(fs.readFileSync(CONFIG.stateFile, "utf-8"));
  }
  return { lastChecked: null, processedCommentIds: new Set() };
}

function saveState(state) {
  state.processedCommentIds = Array.from(state.processedCommentIds);
  fs.writeFileSync(CONFIG.stateFile, JSON.stringify(state, null, 2));
}

function appendLog(comment) {
  const line = JSON.stringify({
    timestamp: new Date().toISOString(),
    commentId: comment.id,
    videoId: comment.videoId,
    commenter: comment.author,
    text: comment.text,
    category: comment.category,
    response: comment.response || null,
    responseStatus: comment.responseStatus,
    flaggedForReview: comment.flaggedForReview,
  });
  fs.appendFileSync(CONFIG.commentsFile, line + "\n");
}

// ============================================================================
// CATEGORIZATION
// ============================================================================

function categorizeComment(text) {
  const lower = text.toLowerCase();

  // Category 1: Questions
  const questionKeywords = [
    "how do i",
    "how to",
    "what",
    "can i",
    "should i",
    "where do i",
    "when should",
    "cost",
    "price",
    "tools",
    "timeline",
    "how long",
    "?",
  ];
  if (questionKeywords.some((kw) => lower.includes(kw))) {
    return "question";
  }

  // Category 3: Spam
  const spamKeywords = [
    "crypto",
    "bitcoin",
    "ethereum",
    "mlm",
    "multi-level",
    "pyramid",
    "click here",
    "free money",
    "dm me",
  ];
  if (spamKeywords.some((kw) => lower.includes(kw))) {
    return "spam";
  }

  // Category 4: Sales/Partnership
  const salesKeywords = [
    "partnership",
    "collaboration",
    "sponsor",
    "brand deal",
    "affiliate",
    "promote",
    "work together",
    "contact me",
    "let's connect",
  ];
  if (salesKeywords.some((kw) => lower.includes(kw))) {
    return "sales";
  }

  // Category 2: Praise
  const praiseKeywords = [
    "amazing",
    "inspiring",
    "love",
    "awesome",
    "great",
    "thanks",
    "thank you",
    "appreciate",
    "incredible",
    "wonderful",
    "brilliant",
    "👏",
    "❤️",
  ];
  if (praiseKeywords.some((kw) => lower.includes(kw))) {
    return "praise";
  }

  return "other";
}

// ============================================================================
// YOUTUBE API
// ============================================================================

function fetchComments(pageToken = null) {
  return new Promise((resolve, reject) => {
    if (!CONFIG.apiKey) {
      reject(
        new Error(
          "YOUTUBE_API_KEY not set. Set env var or provide API key in CONFIG."
        )
      );
      return;
    }

    let url = `https://www.googleapis.com/youtube/v3/comments?key=${CONFIG.apiKey}&textFormat=plainText&part=snippet&parentId=${CONFIG.channelId}&maxResults=100`;
    if (pageToken) url += `&pageToken=${pageToken}`;

    https
      .get(url, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(e);
          }
        });
      })
      .on("error", reject);
  });
}

// ============================================================================
// MAIN LOGIC
// ============================================================================

async function monitor() {
  log("YouTube Comment Monitor started");

  const state = loadState();
  const stats = {
    total: 0,
    autoResponses: 0,
    flagged: 0,
    categories: { question: 0, praise: 0, spam: 0, sales: 0, other: 0 },
  };

  try {
    let pageToken = null;
    let hasNewComments = false;

    // Fetch comments (paginated)
    do {
      log(`Fetching comments (pageToken: ${pageToken || "none"})`);
      const response = await fetchComments(pageToken);

      if (!response.items) {
        log("No items in response. API error or rate limit?");
        break;
      }

      for (const item of response.items) {
        const snippet = item.snippet;
        const commentId = item.id;

        // Skip if already processed
        if (state.processedCommentIds.includes(commentId)) {
          continue;
        }

        hasNewComments = true;
        state.processedCommentIds.push(commentId);

        const text = snippet.textDisplay;
        const author = snippet.authorDisplayName;
        const videoId = snippet.videoId;

        // Categorize
        const category = categorizeComment(text);
        stats.categories[category]++;
        stats.total++;

        const comment = {
          id: commentId,
          videoId,
          author,
          text,
          category,
          response: null,
          responseStatus: "pending",
          flaggedForReview: false,
        };

        // Auto-respond or flag
        if (category === "question") {
          comment.response = CONFIG.templates.question;
          comment.responseStatus = "responded";
          stats.autoResponses++;
          log(`✓ Auto-responded to question from ${author}`);
        } else if (category === "praise") {
          comment.response = CONFIG.templates.praise;
          comment.responseStatus = "responded";
          stats.autoResponses++;
          log(`✓ Auto-responded to praise from ${author}`);
        } else if (category === "sales") {
          comment.flaggedForReview = true;
          comment.responseStatus = "flagged";
          stats.flagged++;
          log(`⚠ Flagged sales inquiry from ${author}`);
        }

        // Log to JSONL
        appendLog(comment);
      }

      // Check for next page
      pageToken = response.nextPageToken;
    } while (pageToken);

    // Save state
    state.lastChecked = new Date().toISOString();
    saveState(state);

    // Report
    log("\n=== REPORT ===");
    log(`Total comments processed: ${stats.total}`);
    log(`Auto-responses sent: ${stats.autoResponses}`);
    log(`Flagged for review: ${stats.flagged}`);
    log(`Categories: ${JSON.stringify(stats.categories)}`);
    log(`Last checked: ${state.lastChecked}`);

    if (!hasNewComments) {
      log("No new comments since last check.");
    }
  } catch (error) {
    log(`ERROR: ${error.message}`);
    process.exit(1);
  }
}

// ============================================================================
// RUN
// ============================================================================

monitor().catch((err) => {
  log(`Fatal error: ${err.message}`);
  process.exit(1);
});
