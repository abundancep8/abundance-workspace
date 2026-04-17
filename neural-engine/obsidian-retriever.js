/**
 * Context Retriever - Pull Knowledge from Obsidian on Demand
 * Retrieves relevant notes/snippets when patterns fire
 * Scores relevance and loads into active context
 */

const fs = require('fs');
const path = require('path');

class ObsidianRetriever {
  constructor(vaultPath = null) {
    // Default to user's Obsidian vault
    if (!vaultPath) {
      const home = require('os').homedir();
      vaultPath = path.join(home, 'Obsidian Vaults', 'My Second Brain');
    }
    this.vaultPath = vaultPath;
    this.cache = new Map();
    this.indexedFiles = [];
    this.indexVault();
  }

  // Index all markdown files in vault
  indexVault() {
    try {
      const walk = (dir, fileList = []) => {
        const files = fs.readdirSync(dir);
        for (const file of files) {
          const filePath = path.join(dir, file);
          const stat = fs.statSync(filePath);
          if (stat.isDirectory() && !file.startsWith('.')) {
            walk(filePath, fileList);
          } else if (file.endsWith('.md')) {
            fileList.push(filePath);
          }
        }
        return fileList;
      };

      this.indexedFiles = walk(this.vaultPath);
      console.log(`[NeuralEngine] Indexed ${this.indexedFiles.length} files from Obsidian vault`);
    } catch (err) {
      console.error(`Failed to index vault: ${err.message}`);
      this.indexedFiles = [];
    }
  }

  // Extract frontmatter from markdown
  parseFrontmatter(content) {
    if (!content.startsWith('---')) return { metadata: {}, content };

    const endIndex = content.indexOf('---', 3);
    if (endIndex === -1) return { metadata: {}, content };

    const fm = content.substring(3, endIndex);
    const rest = content.substring(endIndex + 3).trim();

    const metadata = {};
    for (const line of fm.split('\n')) {
      const [key, ...valueParts] = line.split(':');
      if (key && valueParts.length > 0) {
        metadata[key.trim()] = valueParts.join(':').trim();
      }
    }

    return { metadata, content: rest };
  }

  // Score file relevance to query
  scoreRelevance(filePath, fileName, query) {
    let score = 0;

    // Filename match (high weight)
    if (fileName.toLowerCase().includes(query.toLowerCase())) {
      score += 0.6;
    }

    // Path match (medium weight)
    if (filePath.toLowerCase().includes(query.toLowerCase())) {
      score += 0.3;
    }

    return Math.min(score, 1.0);
  }

  // Retrieve snippets related to fired pattern
  retrieveForPattern(pattern, limit = 3) {
    const results = [];

    try {
      for (const filePath of this.indexedFiles) {
        const fileName = path.basename(filePath, '.md');
        const relevance = this.scoreRelevance(filePath, fileName, pattern);

        if (relevance > 0.2) {
          const content = fs.readFileSync(filePath, 'utf-8');
          const { metadata, content: body } = this.parseFrontmatter(content);

          results.push({
            filePath,
            fileName,
            relevance,
            metadata,
            snippet: body.substring(0, 500), // First 500 chars
            fullContent: body,
          });
        }
      }
    } catch (err) {
      console.error(`Error during retrieval: ${err.message}`);
    }

    // Sort by relevance and return top N
    return results
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, limit);
  }

  // Retrieve by multiple patterns (domain-aware)
  retrieveByDomain(domain, limit = 5) {
    const domainMap = {
      'decision-making': ['10 Decisions', 'decision'],
      'learning': ['30 Memory', 'learning', 'insight'],
      'troubleshooting': ['00 System', 'debug', 'error'],
      'creativity': ['40 Projects', 'idea', 'design'],
      'synthesis': ['20 Patterns', 'pattern', 'connection'],
      'improvement': ['20 Patterns', 'optimize', 'enhance'],
    };

    const keywords = domainMap[domain] || [domain];
    const results = [];

    try {
      for (const filePath of this.indexedFiles) {
        const relPath = path.relative(this.vaultPath, filePath);
        let score = 0;

        for (const keyword of keywords) {
          if (relPath.toLowerCase().includes(keyword.toLowerCase())) {
            score += 0.5;
          }
        }

        if (score > 0) {
          const content = fs.readFileSync(filePath, 'utf-8');
          const { metadata } = this.parseFrontmatter(content);

          results.push({
            filePath,
            relPath,
            score,
            metadata,
            snippet: content.substring(0, 400),
          });
        }
      }
    } catch (err) {
      console.error(`Error retrieving by domain: ${err.message}`);
    }

    return results.sort((a, b) => b.score - a.score).slice(0, limit);
  }

  // Read full file content
  readFile(filePath) {
    try {
      return fs.readFileSync(filePath, 'utf-8');
    } catch (err) {
      console.error(`Failed to read file: ${err.message}`);
      return null;
    }
  }
}

module.exports = ObsidianRetriever;
