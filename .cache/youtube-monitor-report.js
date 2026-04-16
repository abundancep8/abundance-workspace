#!/usr/bin/env node

/**
 * YouTube Comment Monitor - Report Generator
 * Summarizes youtube-comments.jsonl
 * Usage: node youtube-monitor-report.js [--since HOURS] [--category CATEGORY]
 */

const fs = require("fs");
const path = require("path");

const args = process.argv.slice(2);
const since = parseFloat(args.find((a) => a.startsWith("--since"))?.split("=")[1] || "24"); // hours
const filterCategory = args.find((a) => a.startsWith("--category"))?.split("=")[1];

const logFile = path.join(__dirname, "youtube-comments.jsonl");

if (!fs.existsSync(logFile)) {
  console.log("No comments logged yet.");
  process.exit(0);
}

const lines = fs
  .readFileSync(logFile, "utf-8")
  .split("\n")
  .filter((l) => l.trim());

const since_ms = since * 60 * 60 * 1000;
const cutoff = new Date(Date.now() - since_ms);

const comments = lines
  .map((l) => JSON.parse(l))
  .filter((c) => new Date(c.timestamp) >= cutoff)
  .filter((c) => !filterCategory || c.category === filterCategory);

const stats = {
  total: comments.length,
  autoResponses: comments.filter((c) => c.responseStatus === "responded").length,
  flagged: comments.filter((c) => c.flaggedForReview).length,
  categories: {
    question: 0,
    praise: 0,
    spam: 0,
    sales: 0,
    other: 0,
  },
};

comments.forEach((c) => {
  stats.categories[c.category]++;
});

console.log("\n=== YouTube Comment Report ===\n");
console.log(`Period: Last ${since} hours`);
console.log(`Total comments: ${stats.total}`);
console.log(`Auto-responses sent: ${stats.autoResponses}`);
console.log(`Flagged for review: ${stats.flagged}`);
console.log(`\nBreakdown by category:`);
Object.entries(stats.categories).forEach(([cat, count]) => {
  console.log(`  ${cat}: ${count}`);
});

if (stats.flagged > 0) {
  console.log(`\n⚠️ Flagged comments (sales inquiries):\n`);
  comments
    .filter((c) => c.flaggedForReview)
    .forEach((c) => {
      console.log(`  From: ${c.commenter}`);
      console.log(`  Text: ${c.text.substring(0, 80)}${c.text.length > 80 ? "..." : ""}`);
      console.log(`  Time: ${new Date(c.timestamp).toLocaleString()}`);
      console.log("");
    });
}

if (filterCategory) {
  console.log(`\nFiltered: ${filterCategory} comments only`);
}
