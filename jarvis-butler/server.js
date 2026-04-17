#!/usr/bin/env node
/**
 * JARVIS Backend Server
 * Minimal Express server with /api/message endpoint and Cloudflare tunnel support
 */

const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors({
  origin: '*',
  credentials: true,
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json());
app.use(express.static('public'));

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Main message endpoint - handles user messages and returns JARVIS responses
app.post('/api/message', async (req, res) => {
  try {
    const { message } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: 'No message provided' });
    }

    console.log(`📨 Received: "${message}"`);

    // Simulate processing time (100-300ms)
    const processingTime = Math.random() * 200 + 100;
    await new Promise(resolve => setTimeout(resolve, processingTime));

    // Simple response logic
    const responses = {
      'hello': 'Hello there! I\'m JARVIS, your AI assistant. How can I help?',
      'hi': 'Hey! What can I do for you?',
      'how are you': 'I\'m functioning optimally. Thanks for asking!',
      'what is your name': 'I\'m JARVIS - Just Another Rather Very Intelligent System.',
      'help': 'I can help with tasks, answer questions, or have a conversation. Try asking me something!',
      'test': '🎯 System test complete. All neural pathways active.',
      'neural': 'My neural network is firing on all cylinders! ⚡',
      'status': 'All systems online. Neural visualization active. Ready to assist.',
      'default': 'That\'s interesting. I\'m processing that now. Tell me more!'
    };

    // Find matching response
    const lowerMessage = message.toLowerCase();
    let response = responses.default;
    
    for (const [key, value] of Object.entries(responses)) {
      if (lowerMessage.includes(key)) {
        response = value;
        break;
      }
    }

    console.log(`✅ Response: "${response}"`);

    // Return response with metadata
    res.json({
      success: true,
      message: response,
      timestamp: new Date().toISOString(),
      processingTime: processingTime,
      neuralStates: ['firing', 'pulsing', 'resonating']
    });

  } catch (error) {
    console.error('❌ Error:', error.message);
    res.status(500).json({ 
      error: 'Internal server error', 
      message: error.message 
    });
  }
});

// 404 handler
app.use((req, res) => {
  if (req.path.startsWith('/api/')) {
    res.status(404).json({ error: 'API endpoint not found' });
  } else {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
  }
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`
╔═════════════════════════════════════════════════╗
║          🤖 JARVIS NEURAL SERVER 🧠            ║
║                  Online & Ready                 ║
╠═════════════════════════════════════════════════╣
║  🌐 Server:  http://localhost:${PORT}
║  📡 API:     http://localhost:${PORT}/api/message
║  🎨 UI:      http://localhost:${PORT}
║  🔗 Status:  Connected & Monitoring
╚═════════════════════════════════════════════════╝
  `);
});

module.exports = app;
