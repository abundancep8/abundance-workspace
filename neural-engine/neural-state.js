/**
 * Neural State Manager - Active Memory for Real-Time Thinking
 * Maintains what's currently "in focus" for the AI
 * Data: active context, detected patterns, queries, attention weights
 */

const fs = require('fs');
const path = require('path');

class NeuralStateManager {
  constructor(stateFilePath = './neural-state.json') {
    this.stateFile = stateFilePath;
    this.state = this.loadState() || this.initializeState();
  }

  initializeState() {
    return {
      timestamp: Date.now(),
      activeContext: [],
      firedPatterns: [],
      activeQueries: [],
      attentionWeights: {},
      recentInsights: [],
      thinkingDepth: 0,
      recursionStack: [],
    };
  }

  loadState() {
    try {
      if (fs.existsSync(this.stateFile)) {
        const data = fs.readFileSync(this.stateFile, 'utf-8');
        return JSON.parse(data);
      }
    } catch (err) {
      console.error(`Failed to load state: ${err.message}`);
    }
    return null;
  }

  // Add to active context (what we're currently thinking about)
  addContext(item, weight = 1.0) {
    this.state.activeContext.push({
      content: item,
      weight,
      addedAt: Date.now(),
    });
    this.state.attentionWeights[item] = weight;
    this.persist();
  }

  // Fire a pattern (activate it in neural state)
  firePattern(patternName, confidence, relatedContext) {
    const firing = {
      pattern: patternName,
      confidence,
      firedAt: Date.now(),
      relatedContext,
    };
    this.state.firedPatterns.push(firing);
    // Keep last 10 fired patterns
    if (this.state.firedPatterns.length > 10) {
      this.state.firedPatterns.shift();
    }
    this.persist();
    return firing;
  }

  // Track active reasoning queries
  addQuery(query) {
    this.state.activeQueries.push({
      query,
      startedAt: Date.now(),
      status: 'processing',
    });
    this.persist();
  }

  // Complete a query
  completeQuery(query, result) {
    const idx = this.state.activeQueries.findIndex(q => q.query === query);
    if (idx >= 0) {
      this.state.activeQueries[idx].status = 'complete';
      this.state.activeQueries[idx].result = result;
      this.state.activeQueries[idx].completedAt = Date.now();
    }
    this.persist();
  }

  // Log an insight discovered during reasoning
  logInsight(insight) {
    this.state.recentInsights.push({
      insight,
      discoveredAt: Date.now(),
      source: 'active_reasoning',
    });
    // Keep last 20 insights
    if (this.state.recentInsights.length > 20) {
      this.state.recentInsights.shift();
    }
    this.persist();
  }

  // Push to reasoning stack (for recursive thinking)
  pushReasoning(reasoning) {
    this.state.thinkingDepth++;
    this.state.recursionStack.push({
      depth: this.state.thinkingDepth,
      reasoning,
      timestamp: Date.now(),
    });
  }

  // Pop from reasoning stack
  popReasoning() {
    if (this.state.recursionStack.length > 0) {
      this.state.recursionStack.pop();
      this.state.thinkingDepth--;
    }
  }

  // Clear context (reset between major tasks)
  clearContext() {
    this.state.activeContext = [];
    this.state.attentionWeights = {};
    this.state.recursionStack = [];
    this.state.thinkingDepth = 0;
    this.persist();
  }

  // Get top patterns by confidence
  getTopPatterns(limit = 5) {
    return this.state.firedPatterns
      .sort((a, b) => b.confidence - a.confidence)
      .slice(0, limit);
  }

  // Get active reasoning depth
  getThinkingDepth() {
    return this.state.thinkingDepth;
  }

  // Persist state to disk
  persist() {
    try {
      this.state.timestamp = Date.now();
      fs.writeFileSync(this.stateFile, JSON.stringify(this.state, null, 2));
    } catch (err) {
      console.error(`Failed to persist state: ${err.message}`);
    }
  }

  // Export current state for visualization
  export() {
    return JSON.parse(JSON.stringify(this.state));
  }
}

module.exports = NeuralStateManager;
