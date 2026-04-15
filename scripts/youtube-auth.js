#!/usr/bin/env node

/**
 * YouTube OAuth2 Auth Flow
 * Generates and saves refresh token for YouTube API access
 */

const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl'];
const CREDENTIALS_PATH = path.join(process.env.HOME, '.youtube-credentials.json');

async function main() {
  console.log('🔐 YouTube OAuth2 Setup\n');
  
  // Check if credentials already exist
  if (fs.existsSync(CREDENTIALS_PATH)) {
    const existing = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf-8'));
    console.log('✓ Credentials found at:', CREDENTIALS_PATH);
    console.log('  Refresh token:', existing.tokens?.refresh_token ? '***' : 'missing');
    
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question('\nReconfigure? (y/n) ', answer => {
      rl.close();
      if (answer.toLowerCase() !== 'y') {
        console.log('Keeping existing credentials.\n');
        process.exit(0);
      }
    });
    return;
  }
  
  console.log('⚠️  Required: Google Cloud OAuth2 credentials (client_id, client_secret)');
  console.log('   Get them from: https://console.cloud.google.com/apis/credentials\n');
  
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  
  const ask = (question) => new Promise(resolve => {
    rl.question(question, resolve);
  });
  
  const clientId = await ask('Client ID: ');
  const clientSecret = await ask('Client Secret: ');
  
  rl.close();
  
  const oauth2Client = new google.auth.OAuth2(
    clientId,
    clientSecret,
    'urn:ietf:wg:oauth:2.0:oob' // Localhost callback
  );
  
  // Generate authorization URL
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES
  });
  
  console.log('\n🌐 Open this URL in your browser:');
  console.log(authUrl);
  console.log('');
  
  const newRl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const code = await new Promise(resolve => {
    newRl.question('Paste authorization code: ', resolve);
  });
  newRl.close();
  
  try {
    const { tokens } = await oauth2Client.getToken(code);
    
    const credentials = {
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uris: ['urn:ietf:wg:oauth:2.0:oob'],
      tokens: {
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
        scope: SCOPES.join(' '),
        token_type: 'Bearer',
        expiry_date: tokens.expiry_date
      }
    };
    
    fs.writeFileSync(CREDENTIALS_PATH, JSON.stringify(credentials, null, 2));
    fs.chmodSync(CREDENTIALS_PATH, 0o600);
    
    console.log('\n✅ Credentials saved to:', CREDENTIALS_PATH);
    console.log('   Refresh token: ***' + tokens.refresh_token.slice(-10));
    console.log('\nYou can now run: node scripts/youtube-monitor.js\n');
    
  } catch (err) {
    console.error('❌ Auth failed:', err.message);
    process.exit(1);
  }
}

main();
