#!/usr/bin/env node

/**
 * Neural Engine Live Demo
 * Shows the live neural engine thinking in real-time
 * Usage: node demo.js [query]
 */

const NeuralEngine = require('./neural-engine-main');
const JARVISNeuralConnector = require('./jarvis-neural-connector');

async function runDemo() {
  console.log('\n╔════════════════════════════════════════════════════════════╗');
  console.log('║   LIVE NEURAL ENGINE DEMO                                  ║');
  console.log('║   Active Reasoning Brain with Obsidian Integration          ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  // Initialize engines
  console.log('🧠 Initializing neural engine...');
  const engine = new NeuralEngine();
  const jarvis = new JARVISNeuralConnector();

  // Sample queries to demonstrate different pattern types
  const queries = [
    'How can I make better decisions?',
    'What are the latest insights about AI safety?',
    'Help me debug this reasoning error',
    'I want to create something innovative',
    'How do these concepts connect?',
  ];

  // Use command line argument if provided
  const userQuery = process.argv[2];
  const queriesToRun = userQuery ? [userQuery] : queries.slice(0, 2);

  console.log('Ready to think!\n');

  for (const query of queriesToRun) {
    await runQuery(jarvis, engine, query);
  }

  // Show final state
  console.log('\n');
  console.log(engine.visualizeNeurons());

  // Show session report
  console.log('\n📊 SESSION REPORT:');
  const report = engine.generateReport();
  console.log(`  Total Queries: ${report.session.queriesProcessed}`);
  console.log(
    `  Average Time: ${report.session.averageTimePerQuery.toFixed(0)}ms`
  );
  console.log(`  Insights: ${report.insights.length}`);
  console.log(`  Active Context Items: ${report.activeContext}`);

  console.log('\n✅ Demo complete!\n');
}

/**
 * Run a single query through the neural engine
 */
async function runQuery(jarvis, engine, query) {
  console.log('─'.repeat(60));
  console.log(`📝 Query: "${query}"`);
  console.log('─'.repeat(60));

  try {
    // Show thinking start
    console.log('🧠 Thinking...\n');

    // Process through JARVIS connector (which uses the neural engine)
    const result = await jarvis.processQuery(query);

    // Show patterns that fired
    if (result.thinking?.firedPatterns.length > 0) {
      console.log('🔥 Patterns Activated:');
      for (const pattern of result.thinking.firedPatterns) {
        const confidence = (pattern.confidence * 100).toFixed(0);
        console.log(`   • ${pattern.name} (${confidence}% - ${pattern.domain})`);
      }
      console.log();
    }

    // Show processing stats
    console.log(
      `⏱️  Processing: ${result.context.processingTime}ms | Retrieved: ${result.context.itemsRetrieved} items`
    );

    // Show quality
    if (result.thinking?.quality) {
      const q = result.thinking.quality;
      const bar = '█'.repeat(Math.floor(q.score * 20));
      const empty = '░'.repeat(20 - bar.length);
      console.log(`📈 Quality: [${bar}${empty}] ${(q.score * 100).toFixed(0)}%`);
    }

    // Show insights
    if (result.thinking?.insights.length > 0) {
      console.log('\n💡 Key Insights:');
      for (let i = 0; i < Math.min(result.thinking.insights.length, 3); i++) {
        const insight = result.thinking.insights[i];
        console.log(`   ${i + 1}. ${insight}`);
      }
    }

    console.log('\n');
  } catch (err) {
    console.error(`❌ Error: ${err.message}\n`);
  }
}

// Run demo
runDemo().catch(err => {
  console.error(`Fatal error: ${err.message}`);
  process.exit(1);
});
