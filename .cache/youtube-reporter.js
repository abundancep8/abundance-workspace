#!/usr/bin/env node
/**
 * YouTube Comment Monitor Reporter
 * Generates reports from the jsonl log file
 * Usage: node youtube-reporter.js [days]
 */

const fs = require('fs');
const path = require('path');

const logFile = path.join(__dirname, 'youtube-comments.jsonl');

function parseLogFile() {
  if (!fs.existsSync(logFile)) {
    console.log('No comments logged yet.');
    return [];
  }

  const lines = fs.readFileSync(logFile, 'utf8').trim().split('\n');
  return lines.map(line => JSON.parse(line)).filter(Boolean);
}

function formatDate(isoString) {
  return new Date(isoString).toLocaleString('en-US', {
    timeZone: 'America/Los_Angeles',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

function generateReport(days = 7) {
  const comments = parseLogFile();
  const cutoffTime = new Date();
  cutoffTime.setDate(cutoffTime.getDate() - days);

  const filtered = comments.filter(c => new Date(c.timestamp) >= cutoffTime);
  
  if (filtered.length === 0) {
    console.log(`No comments in the last ${days} days.`);
    return;
  }

  // Aggregations
  const byCategory = {};
  const byStatus = {};
  const byCommenter = {};

  filtered.forEach(comment => {
    byCategory[comment.category] = (byCategory[comment.category] || 0) + 1;
    byStatus[comment.responseStatus] = (byStatus[comment.responseStatus] || 0) + 1;
    if (!byCommenter[comment.commenter]) {
      byCommenter[comment.commenter] = [];
    }
    byCommenter[comment.commenter].push(comment);
  });

  // Print report
  console.log(`
╔════════════════════════════════════════════════════════════╗
║          YouTube Comment Monitor Report                    ║
║                  (Last ${days} Days)                          ║
╚════════════════════════════════════════════════════════════╝

📊 SUMMARY
──────────────────────────────────────────────────────────────
  Total Comments:    ${filtered.length}
  Unique Commenters: ${Object.keys(byCommenter).length}
  Period:            ${formatDate(cutoffTime)} → ${formatDate(new Date())}

📂 BY CATEGORY
──────────────────────────────────────────────────────────────
  ❓ Questions:  ${byCategory.question || 0}
  👏 Praise:     ${byCategory.praise || 0}
  🚫 Spam:       ${byCategory.spam || 0}
  💼 Sales:      ${byCategory.sales || 0}
  ℹ️  Other:      ${byCategory.other || 0}

💬 BY RESPONSE STATUS
──────────────────────────────────────────────────────────────
  ✅ Auto-responded: ${byStatus['auto-responded'] || 0}
  🚩 Flagged:       ${byStatus.flagged || 0}
  ⊖ None:           ${byStatus.none || 0}

👥 TOP COMMENTERS
──────────────────────────────────────────────────────────────
`);

  Object.entries(byCommenter)
    .sort((a, b) => b[1].length - a[1].length)
    .slice(0, 5)
    .forEach(([name, comments]) => {
      const cats = {};
      comments.forEach(c => {
        cats[c.category] = (cats[c.category] || 0) + 1;
      });
      const catStr = Object.entries(cats)
        .map(([cat, count]) => `${cat}(${count})`)
        .join(', ');
      console.log(`  ${name.substring(0, 30).padEnd(30)} ${comments.length} comments (${catStr})`);
    });

  console.log(`
🔍 SAMPLE COMMENTS
──────────────────────────────────────────────────────────────
`);

  // Show recent of each category
  ['question', 'praise', 'spam', 'sales'].forEach(cat => {
    const samples = filtered.filter(c => c.category === cat).slice(-2);
    if (samples.length > 0) {
      console.log(`\n  [${cat.toUpperCase()}]`);
      samples.forEach(c => {
        const text = c.text.substring(0, 60) + (c.text.length > 60 ? '...' : '');
        console.log(`    "${text}"`);
        console.log(`     — ${c.commenter} [${c.responseStatus}]`);
      });
    }
  });

  console.log(`
📁 LOGS
──────────────────────────────────────────────────────────────
  Main log:  ${logFile}
  State:     ${path.join(__dirname, 'youtube-monitor-state.json')}

`);
}

// Parse args
const days = parseInt(process.argv[2]) || 7;
generateReport(days);
