/**
 * Reasoning Loop - Active Thinking and Problem Solving
 * Executes dynamic reasoning chains with recursive thinking
 * Integrates with Claude API for actual thought generation
 */

const Anthropic = require('@anthropic-ai/sdk');

class ReasoningLoop {
  constructor() {
    this.client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
    this.thinkingBuffer = [];
    this.maxThinkingTokens = 3000; // Reasonable default
  }

  /**
   * Core reasoning method - generates thought chain
   * @param {string} problem - The problem to reason about
   * @param {object} context - Retrieved context from Obsidian
   * @param {object} patterns - Fired patterns from matcher
   * @returns {object} - Reasoning result with thought chain
   */
  async reason(problem, context = [], patterns = []) {
    try {
      // Build prompt with context
      let systemPrompt = `You are an active reasoning engine. Think deeply about the problem.`;

      let userPrompt = `Problem: ${problem}\n\n`;

      if (patterns.length > 0) {
        userPrompt += `Active Patterns:\n`;
        for (const p of patterns) {
          userPrompt += `- ${p.pattern} (confidence: ${(p.confidence * 100).toFixed(0)}%)\n`;
        }
        userPrompt += '\n';
      }

      if (context.length > 0) {
        userPrompt += `Relevant Context from Knowledge Base:\n`;
        for (const ctx of context) {
          userPrompt += `- ${ctx.fileName}: ${ctx.snippet}\n`;
        }
        userPrompt += '\n';
      }

      userPrompt += `\nThink step by step. Consider multiple angles. Generate insights.`;

      // Call Claude with extended thinking
      const response = await this.client.messages.create({
        model: 'claude-3-7-sonnet-20250219',
        max_tokens: 16000,
        thinking: {
          type: 'enabled',
          budget_tokens: this.maxThinkingTokens,
        },
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: userPrompt,
          },
        ],
      });

      // Extract thinking and response
      let thinkingContent = '';
      let textContent = '';

      for (const block of response.content) {
        if (block.type === 'thinking') {
          thinkingContent = block.thinking;
        } else if (block.type === 'text') {
          textContent = block.text;
        }
      }

      // Parse reasoning into insights
      const insights = this.parseInsights(thinkingContent, textContent);

      return {
        problem,
        thinking: thinkingContent,
        response: textContent,
        insights,
        timestamp: Date.now(),
        tokensUsed: response.usage?.output_tokens || 0,
      };
    } catch (err) {
      console.error(`Reasoning failed: ${err.message}`);
      return {
        problem,
        error: err.message,
        insights: [],
        timestamp: Date.now(),
      };
    }
  }

  /**
   * Recursive reasoning - reason about the output of reasoning
   * @param {string} initialProblem - Original problem
   * @param {object} prevResult - Previous reasoning result
   * @param {number} depth - Recursion depth (max 3)
   */
  async reasonRecursive(initialProblem, prevResult, depth = 1) {
    if (depth > 3) {
      console.log('[NeuralEngine] Max reasoning depth reached');
      return prevResult;
    }

    try {
      const followUp = `Previous thinking:\n${prevResult.thinking}\n\nPrevious insights: ${prevResult.insights.join(', ')}\n\nGo deeper. Find hidden assumptions. What else matters?`;

      const response = await this.client.messages.create({
        model: 'claude-3-7-sonnet-20250219',
        max_tokens: 8000,
        thinking: {
          type: 'enabled',
          budget_tokens: 2000,
        },
        messages: [
          {
            role: 'user',
            content: followUp,
          },
        ],
      });

      let newThinking = '';
      let newResponse = '';

      for (const block of response.content) {
        if (block.type === 'thinking') {
          newThinking = block.thinking;
        } else if (block.type === 'text') {
          newResponse = block.text;
        }
      }

      const deeperInsights = this.parseInsights(newThinking, newResponse);

      return {
        ...prevResult,
        thinking: newThinking,
        response: newResponse,
        insights: [...prevResult.insights, ...deeperInsights],
        depth,
        timestamp: Date.now(),
      };
    } catch (err) {
      console.error(`Recursive reasoning failed: ${err.message}`);
      return prevResult;
    }
  }

  /**
   * Parse Claude's thinking into structured insights
   */
  parseInsights(thinking, response) {
    const insights = [];

    // Extract key phrases from thinking
    const sentences = thinking.split(/[.!?]+/);
    for (const sentence of sentences) {
      const trimmed = sentence.trim();
      if (trimmed.length > 20 && trimmed.length < 200) {
        // Filter for reasonable insight length
        if (
          trimmed.includes('important') ||
          trimmed.includes('key') ||
          trimmed.includes('realize') ||
          trimmed.includes('insight') ||
          trimmed.includes('should') ||
          trimmed.includes('could')
        ) {
          insights.push(trimmed);
        }
      }
    }

    // Also extract from response
    const responseLines = response
      .split('\n')
      .filter(line => line.length > 20 && line.length < 300);
    insights.push(...responseLines.slice(0, 3));

    return [...new Set(insights)].slice(0, 5); // Deduplicate, limit to 5
  }

  /**
   * Evaluate reasoning quality
   */
  evaluateReasoning(result) {
    const quality = {
      hasThinking: !!result.thinking && result.thinking.length > 100,
      hasInsights: result.insights.length > 0,
      thinkingLength: result.thinking?.length || 0,
      insightCount: result.insights.length,
      score: 0,
    };

    quality.score =
      (quality.hasThinking ? 0.5 : 0) + (quality.hasInsights ? 0.5 : 0);

    return quality;
  }
}

module.exports = ReasoningLoop;
