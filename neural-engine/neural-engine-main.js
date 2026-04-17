/**
 * Neural Engine Orchestrator - Main System
 * Coordinates all components: state, patterns, retrieval, reasoning, persistence
 * This is the "brain" that thinks in real-time
 */

const NeuralStateManager = require('./neural-state');
const PatternMatcher = require('./pattern-matcher');
const ObsidianRetriever = require('./obsidian-retriever');
const ReasoningLoop = require('./reasoning-loop');
const ObsidianWriter = require('./obsidian-writer');

class NeuralEngine {
  constructor(config = {}) {
    this.state = new NeuralStateManager(config.stateFile);
    this.patterns = new PatternMatcher();
    this.retriever = new ObsidianRetriever(config.vaultPath);
    this.reasoner = new ReasoningLoop();
    this.writer = new ObsidianWriter(config.vaultPath);

    this.config = config;
    this.sessionStarted = Date.now();
    this.queriesProcessed = 0;
  }

  /**
   * Core thinking pipeline: input → patterns → retrieval → reasoning → persistence
   */
  async think(input) {
    console.log(`\n[NeuralEngine] Processing: "${input.substring(0, 60)}..."`);
    const startTime = Date.now();

    // Step 1: Add to active context
    this.state.addContext(input, 1.0);

    // Step 2: Fire patterns
    const firedPatterns = this.patterns.firePatterns(input);
    console.log(
      `[NeuralEngine] Fired ${firedPatterns.length} patterns: ${firedPatterns.map(p => p.pattern).join(', ')}`
    );

    for (const pattern of firedPatterns) {
      this.state.firePattern(pattern.pattern, pattern.confidence, input);
    }

    // Step 3: Retrieve context from Obsidian
    let retrievedContext = [];
    if (firedPatterns.length > 0) {
      // Use primary pattern domain for retrieval
      const primaryDomain = firedPatterns[0].domain;
      retrievedContext = this.retriever.retrieveByDomain(primaryDomain, 3);
      console.log(
        `[NeuralEngine] Retrieved ${retrievedContext.length} context items from domain: ${primaryDomain}`
      );
    }

    // Step 4: Reason about the input
    this.state.addQuery(input);
    console.log('[NeuralEngine] Starting reasoning loop...');

    const reasoning = await this.reasoner.reason(input, retrievedContext, firedPatterns);
    reasoning.quality = this.reasoner.evaluateReasoning(reasoning);

    console.log(`[NeuralEngine] Reasoning complete. Quality: ${reasoning.quality.score.toFixed(2)}`);

    // Step 5: Log insights
    for (const insight of reasoning.insights) {
      this.state.logInsight(insight);
    }

    // Step 6: Consider deeper reasoning if quality is high
    if (reasoning.quality.hasThinking && reasoning.quality.hasInsights) {
      console.log('[NeuralEngine] Quality insights detected. Attempting recursive reasoning...');
      const deeper = await this.reasoner.reasonRecursive(input, reasoning, 2);
      reasoning.deeperInsights = deeper.insights;
    }

    // Step 7: Persist results
    this.state.completeQuery(input, reasoning);
    this.writer.saveReasoning(reasoning);
    this.writer.updatePatternIndex(firedPatterns);

    // Save individual insights
    for (const insight of reasoning.insights) {
      this.writer.saveInsight(insight, 'neural-reasoning');
    }

    // Step 8: Prepare summary
    const elapsed = Date.now() - startTime;
    this.queriesProcessed++;

    const summary = {
      input,
      firedPatterns: firedPatterns.map(p => ({
        name: p.pattern,
        confidence: p.confidence,
        domain: p.domain,
      })),
      retrievedItems: retrievedContext.length,
      insights: reasoning.insights,
      thinkingLength: reasoning.thinking?.length || 0,
      responseLength: reasoning.response?.length || 0,
      quality: reasoning.quality,
      processingTime: elapsed,
    };

    console.log(`[NeuralEngine] ✓ Complete in ${elapsed}ms`);
    return summary;
  }

  /**
   * Get current neural state for visualization
   */
  getState() {
    return {
      engine: {
        uptime: Date.now() - this.sessionStarted,
        queriesProcessed: this.queriesProcessed,
      },
      neuralState: this.state.export(),
      topPatterns: this.state.getTopPatterns(5),
      thinkingDepth: this.state.getThinkingDepth(),
    };
  }

  /**
   * Generate visualization of current neural activity
   */
  visualizeNeurons() {
    const state = this.getState();
    const topPatterns = state.topPatterns;

    let viz = '\n╔════════════════════════════════════════╗\n';
    viz += '║       NEURAL ENGINE VISUALIZATION       ║\n';
    viz += '╚════════════════════════════════════════╝\n\n';

    viz += `⏱️  Uptime: ${(state.engine.uptime / 1000).toFixed(1)}s\n`;
    viz += `📊 Queries: ${state.engine.queriesProcessed}\n`;
    viz += `🧠 Depth: ${state.thinkingDepth}\n\n`;

    if (topPatterns.length > 0) {
      viz += '🔥 FIRING PATTERNS:\n';
      for (const p of topPatterns) {
        const bar = '█'.repeat(Math.floor(p.confidence * 20));
        const empty = '░'.repeat(20 - bar.length);
        viz += `  ${p.pattern.padEnd(25)} [${bar}${empty}] ${(p.confidence * 100).toFixed(0)}%\n`;
      }
    } else {
      viz += '(No patterns active)\n';
    }

    viz += '\n';
    return viz;
  }

  /**
   * Generate session report
   */
  generateReport() {
    const state = this.getState();

    return {
      session: {
        duration: state.engine.uptime,
        queriesProcessed: state.engine.queriesProcessed,
        averageTimePerQuery:
          state.engine.queriesProcessed > 0
            ? state.engine.uptime / state.engine.queriesProcessed
            : 0,
      },
      patterns: state.topPatterns,
      insights: state.neuralState.recentInsights,
      activeContext: state.neuralState.activeContext.length,
      recursionDepth: state.thinkingDepth,
    };
  }

  /**
   * Save daily neural report to Obsidian
   */
  saveDailyReport() {
    const report = this.generateReport();
    const recommendations = this.generateRecommendations(report);

    this.writer.saveDailyReport({
      duration: `${(report.session.duration / 1000).toFixed(1)}s`,
      queriesProcessed: report.session.queriesProcessed,
      patternsFired: report.patterns.length,
      insightsGenerated: report.insights.length,
      topPatterns: report.patterns.slice(0, 5),
      keyInsights: report.insights.slice(0, 5).map(i => i.insight),
      recommendations,
    });
  }

  /**
   * Generate recommendations based on reasoning
   */
  generateRecommendations(report) {
    const recs = [];

    const topDomains = {};
    for (const p of report.patterns) {
      topDomains[p.domain] = (topDomains[p.domain] || 0) + 1;
    }

    for (const [domain, count] of Object.entries(topDomains)) {
      if (count >= 2) {
        recs.push(`Explore more about ${domain} (${count} patterns active)`);
      }
    }

    if (report.recursionDepth > 2) {
      recs.push('Deep thinking detected - review insights for novel discoveries');
    }

    if (report.insights.length > 5) {
      recs.push('Many insights generated - consider synthesis note');
    }

    return recs.length > 0 ? recs : ['Continue monitoring patterns'];
  }

  /**
   * Reset session state
   */
  reset() {
    this.state.clearContext();
    this.queriesProcessed = 0;
    this.sessionStarted = Date.now();
    console.log('[NeuralEngine] Session reset');
  }
}

module.exports = NeuralEngine;
