/**
 * JARVIS-Neural Engine Connector
 * Bridges the neural engine to conversational interfaces (Discord, etc.)
 * Routes user questions through the live brain for active reasoning
 */

const NeuralEngine = require('./neural-engine-main');

class JARVISNeuralConnector {
  constructor(config = {}) {
    this.engine = new NeuralEngine(config);
    this.conversationHistory = [];
    this.enableVerbose = config.verbose || false;
  }

  /**
   * Process user message through neural engine
   * Returns augmented response with reasoning context
   */
  async processQuery(userMessage, context = {}) {
    try {
      // Run neural thinking
      const thinking = await this.engine.think(userMessage);

      // Build response with neural context
      const response = {
        userMessage,
        thinking: {
          firedPatterns: thinking.firedPatterns,
          insights: thinking.insights,
          quality: thinking.quality,
        },
        answer: thinking.insights[0] || 'Thinking...',
        context: {
          itemsRetrieved: thinking.retrievedItems,
          processingTime: thinking.processingTime,
        },
      };

      // Store in conversation history
      this.conversationHistory.push({
        timestamp: Date.now(),
        userMessage,
        response,
      });

      // Keep history size reasonable
      if (this.conversationHistory.length > 50) {
        this.conversationHistory.shift();
      }

      return response;
    } catch (err) {
      console.error(`[JARVIS-Neural] Error: ${err.message}`);
      return {
        userMessage,
        error: err.message,
        answer: 'Neural engine encountered an error during reasoning.',
      };
    }
  }

  /**
   * Format response for Discord/messaging
   */
  formatDiscordResponse(thinkingResult) {
    let message = '';

    // Main answer
    if (thinkingResult.answer) {
      message += `**Answer**: ${thinkingResult.answer}\n\n`;
    }

    // Show patterns that fired
    if (thinkingResult.thinking?.firedPatterns.length > 0) {
      message += '**Active Patterns**: ';
      message += thinkingResult.thinking.firedPatterns.map(p => `\`${p.name}\``).join(', ');
      message += '\n';
    }

    // Show key insights
    if (thinkingResult.thinking?.insights.length > 0) {
      message += '\n**Insights**:\n';
      for (const insight of thinkingResult.thinking.insights.slice(0, 3)) {
        message += `• ${insight}\n`;
      }
    }

    // Quality score
    if (thinkingResult.thinking?.quality) {
      const score = thinkingResult.thinking.quality.score;
      const bar = '█'.repeat(Math.floor(score * 10)) + '░'.repeat(10 - Math.floor(score * 10));
      message += `\n**Reasoning Quality**: [${bar}] ${(score * 100).toFixed(0)}%`;
    }

    return message.trim();
  }

  /**
   * Get neural state for diagnostic purposes
   */
  getNeuralState() {
    return this.engine.getState();
  }

  /**
   * Visualize what the brain is doing
   */
  visualizeBrain() {
    return this.engine.visualizeNeurons();
  }

  /**
   * Get conversation summary
   */
  getConversationSummary() {
    return {
      totalMessages: this.conversationHistory.length,
      lastMessage: this.conversationHistory[this.conversationHistory.length - 1] || null,
      averageProcessingTime:
        this.conversationHistory.reduce((sum, msg) => sum + (msg.response.context?.processingTime || 0), 0) /
        Math.max(this.conversationHistory.length, 1),
    };
  }

  /**
   * Reset neural engine
   */
  resetBrain() {
    this.engine.reset();
    this.conversationHistory = [];
    console.log('[JARVIS-Neural] Brain reset');
  }

  /**
   * Save session to Obsidian
   */
  saveSession() {
    this.engine.saveDailyReport();
    console.log('[JARVIS-Neural] Session saved to Obsidian');
  }
}

module.exports = JARVISNeuralConnector;
