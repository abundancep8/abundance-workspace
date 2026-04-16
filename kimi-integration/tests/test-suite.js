#!/usr/bin/env node

/**
 * Test Suite - 10 Sample Tasks
 * Tests routing logic and quality across both models
 */

const path = require('path');
const router = require('../router');

const TESTS = [
  {
    id: 1,
    taskName: 'Research: LinkedIn Competitor Analysis',
    type: 'research',
    estimatedTokens: 15000,
    timeSensitive: false,
    qualityCritical: false,
    messages: [
      {
        role: 'user',
        content: 'Analyze the top 3 LinkedIn-like platforms in Asia. Focus on market size, user base, and competitive advantages. Provide a 200-word summary.'
      }
    ],
    expectedModel: 'kimi',
    description: 'Research task with high token count - should route to Kimi'
  },
  {
    id: 2,
    taskName: 'Discord: Real-time Response',
    type: 'discord',
    estimatedTokens: 500,
    timeSensitive: true,
    qualityCritical: true,
    messages: [
      {
        role: 'user',
        content: 'Quick response: what\'s a good nodejs testing framework?'
      }
    ],
    expectedModel: 'claude',
    description: 'Discord message - should stay on Claude for speed'
  },
  {
    id: 3,
    taskName: 'Batch: Document Analysis (100 PDFs)',
    type: 'batch_processing',
    estimatedTokens: 50000,
    timeSensitive: false,
    qualityCritical: false,
    messages: [
      {
        role: 'user',
        content: 'Extract key financial metrics from 100 annual reports. Return CSV format. This is a batch processing task.'
      }
    ],
    expectedModel: 'kimi',
    description: 'Batch processing with massive token requirement - route to Kimi'
  },
  {
    id: 4,
    taskName: 'Complex Reasoning: Algorithm Design',
    type: 'reasoning',
    estimatedTokens: 5000,
    timeSensitive: false,
    qualityCritical: true,
    messages: [
      {
        role: 'user',
        content: 'Design an efficient algorithm for distributed consensus with Byzantine fault tolerance. Explain trade-offs.'
      }
    ],
    expectedModel: 'claude',
    description: 'Quality-critical reasoning - should use Claude'
  },
  {
    id: 5,
    taskName: 'Market Research: Industry Trends',
    type: 'research',
    estimatedTokens: 12000,
    timeSensitive: false,
    qualityCritical: false,
    messages: [
      {
        role: 'user',
        content: 'What are the top emerging trends in AI infrastructure (2025-2026)? Include market sizing and player analysis.'
      }
    ],
    expectedModel: 'kimi',
    description: 'Research with cost optimization - route to Kimi'
  },
  {
    id: 6,
    taskName: 'JARVIS Integration Task',
    type: 'jarvis',
    estimatedTokens: 2000,
    timeSensitive: true,
    qualityCritical: true,
    messages: [
      {
        role: 'user',
        content: 'Update the home automation routine and confirm status.'
      }
    ],
    expectedModel: 'claude',
    description: 'JARVIS system interaction - stay on Claude'
  },
  {
    id: 7,
    taskName: 'Long Context: Memory Synthesis',
    type: 'long_context',
    estimatedTokens: 25000,
    timeSensitive: false,
    qualityCritical: false,
    messages: [
      {
        role: 'user',
        content: 'Synthesize 50 daily memory files into actionable insights about productivity patterns over 60 days.'
      }
    ],
    expectedModel: 'kimi',
    description: 'Long context processing - route to Kimi'
  },
  {
    id: 8,
    taskName: 'Customer Support: Complaint Resolution',
    type: 'support',
    estimatedTokens: 3000,
    timeSensitive: false,
    qualityCritical: true,
    messages: [
      {
        role: 'user',
        content: 'Draft a professional response to a customer complaint about delayed delivery. Be empathetic and solution-focused.'
      }
    ],
    expectedModel: 'claude',
    description: 'Customer-facing quality-critical response - use Claude'
  },
  {
    id: 9,
    taskName: 'Data Processing: Pattern Extraction',
    type: 'batch_processing',
    estimatedTokens: 20000,
    timeSensitive: false,
    qualityCritical: false,
    messages: [
      {
        role: 'user',
        content: 'Extract behavioral patterns from 10000 user session logs. Identify top 5 user segments.'
      }
    ],
    expectedModel: 'kimi',
    description: 'Cost-sensitive batch processing - route to Kimi'
  },
  {
    id: 10,
    taskName: 'General: Simple Question',
    type: 'general',
    estimatedTokens: 500,
    timeSensitive: false,
    qualityCritical: false,
    messages: [
      {
        role: 'user',
        content: 'What is the capital of France?'
      }
    ],
    expectedModel: 'claude',
    description: 'General task with low tokens - default to Claude'
  }
];

/**
 * Run all tests
 */
async function runTests() {
  console.log('\n╔════════════════════════════════════════════════════════════════╗');
  console.log('║          KIMI K2.5 ROUTING TEST SUITE (10 Tasks)              ║');
  console.log('╚════════════════════════════════════════════════════════════════╝\n');

  let passed = 0;
  let failed = 0;
  const results = [];

  for (const test of TESTS) {
    console.log(`\n[${test.id}/10] ${test.taskName}`);
    console.log(`     Description: ${test.description}`);

    // Test routing decision
    const routing = router.routeTask({
      type: test.type,
      estimatedTokens: test.estimatedTokens,
      timeSensitive: test.timeSensitive,
      qualityCritical: test.qualityCritical,
      taskName: test.taskName
    });

    const routingCorrect = routing.model === test.expectedModel;
    const routingStatus = routingCorrect ? '✓ PASS' : '✗ FAIL';

    console.log(`     Expected: ${test.expectedModel.toUpperCase()} | Got: ${routing.model.toUpperCase()} [${routingStatus}]`);
    console.log(`     Reason: ${routing.reason}`);

    if (routingCorrect) {
      passed++;
    } else {
      failed++;
    }

    results.push({
      id: test.id,
      taskName: test.taskName,
      routingCorrect,
      expected: test.expectedModel,
      actual: routing.model
    });
  }

  // Summary
  console.log('\n╔════════════════════════════════════════════════════════════════╗');
  console.log(`║  RESULTS: ${passed} PASSED, ${failed} FAILED out of ${TESTS.length} TESTS              ║`);
  console.log('╚════════════════════════════════════════════════════════════════╝\n');

  if (failed === 0) {
    console.log('🎉 All routing tests passed! Integration ready for deployment.\n');
  } else {
    console.log(`⚠️  ${failed} routing tests failed. Review logic before deployment.\n`);
  }

  return { passed, failed, totalTests: TESTS.length, results };
}

// Run if executed directly
if (require.main === module) {
  runTests().then(result => {
    process.exit(result.failed > 0 ? 1 : 0);
  }).catch(err => {
    console.error('Test execution failed:', err);
    process.exit(1);
  });
}

module.exports = { TESTS, runTests };
