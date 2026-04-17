# Neural Engine Setup & Verification

Complete setup guide for the Live Neural Engine.

## ✅ Pre-Flight Checklist

### 1. Prerequisites

- Node.js 14+ installed
- Anthropic API key (export ANTHROPIC_API_KEY)
- Obsidian vault at: `/Users/abundance/Obsidian Vaults/My Second Brain`

### 2. Quick Setup

```bash
cd ~/path/to/neural-engine

# Install dependencies
npm install

# Verify installation
npm list
```

Expected output:
```
@abundance/neural-engine@1.0.0
├── @anthropic-ai/sdk@0.24.3
└── (other transitive deps)
```

### 3. Environment Setup

```bash
# Ensure API key is set
export ANTHROPIC_API_KEY="sk-ant-..."

# Verify
echo $ANTHROPIC_API_KEY  # Should show your key (or part of it)
```

### 4. Run Tests

```bash
npm test
# or: node test-neural-engine.js
```

Expected output:
```
▶ Testing Neural State Manager...
  ✓ Context addition works
  ✓ Pattern firing works
  ✓ Query tracking works
  ✓ Insight logging works

▶ Testing Pattern Matcher...
  ✓ Pattern matching works (6 patterns fired)
  ✓ Learning pattern detection works
  ✓ Custom pattern addition works
  ✓ Pattern combination works

▶ Testing Obsidian Retriever...
  ✓ Vault indexed (XX files found)
  ✓ Pattern retrieval works (X items found)
  ✓ Domain retrieval works (X items)

▶ Testing Neural Engine (Orchestration)...
  ✓ Engine initialization works
  ✓ State export works
  ✓ Neural visualization works
  ✓ Report generation works

╔════════════════════════════════════════╗
║   TEST SUMMARY                         ║
╚════════════════════════════════════════╝
✓ Passed: 16
✗ Failed: 0
Total: 16
Success Rate: 100%

🎉 All tests passed!
```

### 5. Run Demo

```bash
npm run demo
# or: node demo.js

# With custom query:
npm run demo:query "What should I focus on?"
# or: node demo.js "What should I focus on?"
```

Expected output:
```
╔════════════════════════════════════════════════════════════╗
║   LIVE NEURAL ENGINE DEMO                                  ║
║   Active Reasoning Brain with Obsidian Integration          ║
╚════════════════════════════════════════════════════════════╝

🧠 Initializing neural engine...
Ready to think!

────────────────────────────────────────────────────────────
📝 Query: "How can I make better decisions?"
────────────────────────────────────────────────────────────
🧠 Thinking...

🔥 Patterns Activated:
   • decision-pattern (90% - decision-making)
   • optimization-pattern (78% - improvement)

⏱️  Processing: 2340ms | Retrieved: 3 items
📈 Quality: [████████░░░░░░░░░░░░] 95%

💡 Key Insights:
   1. Break down decisions into smaller steps
   2. Consider multiple perspectives
   3. Review past decisions for patterns
```

## 📁 Directory Structure

```
neural-engine/
├── node_modules/          # Dependencies (after npm install)
├── neural-state.js        # Active memory manager
├── pattern-matcher.js     # Dynamic pattern detection
├── obsidian-retriever.js  # Knowledge lookup
├── reasoning-loop.js      # Deep thinking engine
├── obsidian-writer.js     # Persistence layer
├── neural-engine-main.js  # Main orchestrator
├── jarvis-neural-connector.js  # Conversational bridge
├── test-neural-engine.js  # Test suite
├── demo.js                # Interactive demo
├── package.json           # Dependencies
├── README.md              # Full documentation
├── INTEGRATION_GUIDE.md   # JARVIS integration
├── SETUP.md              # This file
└── neural-state.json      # Runtime state (created on first run)
```

## 🚀 First Run

### Option 1: Run Tests (Recommended)
```bash
npm test
```
This validates all components work together.

### Option 2: Run Demo
```bash
npm run demo
```
This shows the neural engine thinking in action.

### Option 3: Use Interactively
```javascript
const NeuralEngine = require('./neural-engine-main');

const engine = new NeuralEngine();
const result = await engine.think("What matters most to me?");

console.log(result);
```

## 🔧 Configuration

### Custom Vault Path

```javascript
const engine = new NeuralEngine({
  vaultPath: '/path/to/your/vault',
  stateFile: './custom-state.json'
});
```

### Custom Thinking Tokens

```javascript
const loop = new ReasoningLoop();
loop.maxThinkingTokens = 5000;  // Default: 3000
```

### Verbose Logging

```javascript
const brain = new JARVISNeuralConnector({
  verbose: true
});
```

## 🧠 Verifying Integration

### Check Obsidian Vault Connection

```javascript
const ObsidianRetriever = require('./obsidian-retriever');
const retriever = new ObsidianRetriever();

console.log(`Indexed ${retriever.indexedFiles.length} files`);
console.log(retriever.indexedFiles.slice(0, 5));
```

### Test Reasoning

```javascript
const ReasoningLoop = require('./reasoning-loop');
const loop = new ReasoningLoop();

const result = await loop.reason(
  "Test problem",
  [],  // context
  []   // patterns
);

console.log('Thinking:', result.thinking.substring(0, 200));
console.log('Insights:', result.insights);
```

### Verify Pattern Matching

```javascript
const PatternMatcher = require('./pattern-matcher');
const matcher = new PatternMatcher();

const fired = matcher.firePatterns("I want to learn about AI");
console.log('Fired patterns:', fired);
```

## 📊 Neural State File

After first run, check `neural-state.json`:

```json
{
  "timestamp": 1713350400000,
  "activeContext": [
    {"content": "First query", "weight": 1.0, "addedAt": 1713350300000}
  ],
  "firedPatterns": [
    {"pattern": "learning-pattern", "confidence": 0.85, "firedAt": 1713350350000}
  ],
  "activeQueries": [
    {"query": "First query", "status": "complete", "completedAt": 1713350380000}
  ],
  "recentInsights": [
    {"insight": "Learning is iterative", "discoveredAt": 1713350380000}
  ],
  "thinkingDepth": 1,
  "recursionStack": []
}
```

## 🔍 Debugging

### Enable Verbose Logging

```bash
DEBUG=neural-engine:* node demo.js
```

### Check Generated Files

After running, check Obsidian vault:
```bash
ls -la ~/Obsidian\ Vaults/My\ Second\ Brain/30\ Memory/
```

You should see:
- `neural-reasoning-*.md` (full reasoning logs)
- `neural-report-*.md` (daily summaries)
- `insight-*.md` (individual insights)

### Inspect State

```javascript
const engine = new NeuralEngine();
const state = engine.getState();
console.log(JSON.stringify(state, null, 2));
```

## 🐛 Common Issues

### Issue: "ANTHROPIC_API_KEY not set"
**Solution:**
```bash
export ANTHROPIC_API_KEY="your-key-here"
# Or add to ~/.zshrc / ~/.bashrc
```

### Issue: "Vault not found"
**Solution:**
Check actual vault path:
```bash
ls ~/Obsidian\ Vaults/
```

Then update config:
```javascript
const engine = new NeuralEngine({
  vaultPath: '/your/actual/path'
});
```

### Issue: "No files indexed"
**Solution:**
Ensure vault has `.md` files:
```bash
find ~/Obsidian\ Vaults/ -name "*.md" | wc -l
```

### Issue: "Reasoning timeout"
**Solution:**
Reduce thinking depth:
```javascript
loop.maxThinkingTokens = 1000;  // Instead of 3000
```

## ✨ Next Steps

1. **Run tests**: `npm test` ✓
2. **Run demo**: `npm run demo` ✓
3. **Review README**: Read full documentation ✓
4. **Check INTEGRATION_GUIDE**: For JARVIS setup ✓
5. **Integrate with JARVIS**: Use JARVISNeuralConnector ✓
6. **Monitor Obsidian**: Check generated notes ✓

## 📞 Support

If setup fails:

1. Check Node version: `node --version` (should be 14+)
2. Check npm: `npm --version`
3. Check API key: `echo $ANTHROPIC_API_KEY`
4. Run tests: `npm test`
5. Check vault: `ls ~/Obsidian\ Vaults/My\ Second\ Brain/`

---

**Setup complete!** Your live neural engine is ready to think. 🧠✨
