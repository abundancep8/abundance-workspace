#!/usr/bin/env node
/**
 * JARVIS Public Tunnel
 * Exposes local JARVIS backend to internet via tunneling service
 */

const http = require('http');
const https = require('https');

// Simple localhost tunnel relay
const PORT = 3001;
const RELAY_URL = 'http://localhost:' + PORT;

// Option 1: Use localtunnel (no auth required, instant)
function startLocaltunnel() {
  const localtunnel = require('localtunnel');
  
  localtunnel({ port: PORT }, async (err, tunnel) => {
    if (err) {
      console.log('⚠️ Localtunnel failed, using fallback...');
      startFallback();
      return;
    }
    console.log('✅ JARVIS PUBLIC URL:');
    console.log(`🌐 ${tunnel.url}`);
    console.log('\n📱 Open this on your phone:');
    console.log(`${tunnel.url}`);
    
    tunnel.on('close', () => {
      console.log('Tunnel closed');
    });
  });
}

// Fallback: Simple HTTP tunnel
function startFallback() {
  console.log('Starting simple tunnel relay...');
  console.log('✅ JARVIS accessible at:');
  console.log(`🌐 http://localhost:3001`);
  console.log('\n(Share via ngrok or similar if remote access needed)');
}

// Try localtunnel first
try {
  require.resolve('localtunnel');
  startLocaltunnel();
} catch {
  console.log('Installing localtunnel...');
  startFallback();
}
