/**
 * Pattern Matcher - Neuron Firing for Dynamic Pattern Detection
 * Identifies relevant patterns when new input arrives
 * Scores matches and activates patterns in neural state
 */

class PatternMatcher {
  constructor() {
    this.patterns = new Map();
    this.initializePatterns();
  }

  initializePatterns() {
    // Core pattern types - can be expanded from Obsidian
    this.patterns.set('decision-pattern', {
      keywords: ['decide', 'choice', 'option', 'alternative', 'select'],
      relevance: 0.9,
      domain: 'decision-making',
    });

    this.patterns.set('learning-pattern', {
      keywords: ['learn', 'understand', 'insight', 'discovery', 'knowledge'],
      relevance: 0.85,
      domain: 'learning',
    });

    this.patterns.set('problem-solving', {
      keywords: ['solve', 'fix', 'issue', 'problem', 'debug', 'error'],
      relevance: 0.9,
      domain: 'troubleshooting',
    });

    this.patterns.set('creativity-pattern', {
      keywords: ['create', 'design', 'idea', 'imagine', 'innovate', 'invent'],
      relevance: 0.8,
      domain: 'creativity',
    });

    this.patterns.set('connection-pattern', {
      keywords: ['relate', 'connect', 'similar', 'analogy', 'link', 'bridge'],
      relevance: 0.75,
      domain: 'synthesis',
    });

    this.patterns.set('optimization-pattern', {
      keywords: ['optimize', 'efficient', 'faster', 'better', 'improve', 'enhance'],
      relevance: 0.8,
      domain: 'improvement',
    });
  }

  // Score text against a pattern (0-1)
  scoreTextAgainstPattern(text, pattern) {
    const lowerText = text.toLowerCase();
    const keywords = pattern.keywords;

    let matches = 0;
    for (const keyword of keywords) {
      if (lowerText.includes(keyword)) {
        matches++;
      }
    }

    // Weighted score: more matches = higher confidence
    const matchRatio = matches / keywords.length;
    return matchRatio * pattern.relevance;
  }

  // Fire patterns for given input - returns ranked list of activated patterns
  firePatterns(input, threshold = 0.3) {
    const fired = [];

    for (const [patternName, patternDef] of this.patterns) {
      const score = this.scoreTextAgainstPattern(input, patternDef);

      if (score >= threshold) {
        fired.push({
          pattern: patternName,
          confidence: score,
          domain: patternDef.domain,
          timestamp: Date.now(),
        });
      }
    }

    // Sort by confidence (descending)
    return fired.sort((a, b) => b.confidence - a.confidence);
  }

  // Add custom pattern from Obsidian
  addPattern(name, keywords, relevance = 0.8, domain = 'custom') {
    this.patterns.set(name, {
      keywords,
      relevance,
      domain,
    });
  }

  // Get all patterns
  getAllPatterns() {
    return Array.from(this.patterns.entries()).map(([name, def]) => ({
      name,
      ...def,
    }));
  }

  // Combine multiple fired patterns for context
  combinePatterns(firedPatterns) {
    if (firedPatterns.length === 0) return null;

    const combined = {
      dominantPattern: firedPatterns[0],
      relatedPatterns: firedPatterns.slice(1),
      combinedConfidence: firedPatterns[0].confidence,
      domains: [...new Set(firedPatterns.map(p => p.domain))],
      timestamp: Date.now(),
    };

    return combined;
  }
}

module.exports = PatternMatcher;
