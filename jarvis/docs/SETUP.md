# JARVIS + Chief of Staff - Setup Guide

## Prerequisites

- Python 3.9+
- Node.js 16+
- Git
- pip + npm

## Quick Start (5 minutes)

### 1. Backend Setup

```bash
cd jarvis/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
ANTHROPIC_API_KEY=sk-YOUR_KEY_HERE
VAULT_PATH=/Users/abundance/.openclaw/workspace/vault
BUDGET_DAILY=50.0
EOF

# Start server
python server.py
```

Server runs on `http://localhost:8000`

### 2. Frontend Setup

```bash
cd jarvis/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs on `http://localhost:5173`

### 3. Access System

Open browser to: **http://localhost:5173**

## Configuration

### .env Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | - | Claude API key (required) |
| `KIMI_API_KEY` | - | Kimi K2.5 API key (optional) |
| `VAULT_PATH` | `~/.openclaw/workspace/vault` | Obsidian vault location |
| `MEMORY_PATH` | `~/.openclaw/workspace/memory` | Memory file directory |
| `BUDGET_DAILY` | 50.0 | Daily cost budget in USD |
| `KIMI_COST_PER_1M` | 0.50 | Kimi token pricing |
| `CLAUDE_COST_PER_1M` | 3.00 | Claude token pricing |
| `LOG_LEVEL` | info | Logging level |

### Vault Structure

```
~/.openclaw/workspace/vault/
├── decisions/          # Decision logs
├── patterns/           # Neural patterns
├── memory/            # Daily memory files
└── backups/           # Vault backups
```

Auto-created on first run.

## Features Checklist

### ✅ Core System
- [x] FastAPI server with WebSocket
- [x] Chief of Staff (Obsidian integration)
- [x] Neural Router (cost optimization)
- [x] Voice Handler (TTS + audio-reactive orb)
- [x] Service Automation (lead gen, pipeline)

### ✅ Frontend
- [x] React UI with Vite
- [x] Three.js audio-reactive orb visualization
- [x] Web Speech API voice input
- [x] Real-time WebSocket connection
- [x] Dashboard with cost tracking
- [x] Task submitter with categories

### ✅ Integration Ready
- [x] Anthropic Claude integration
- [x] Kimi K2.5 routing logic
- [x] Cost tracking + budgeting
- [x] Obsidian vault operations
- [x] Service business automation

## First Run Checklist

1. **Backend starts without errors**
   ```bash
   # Check:
   curl http://localhost:8000/health
   # Response: {"status": "alive", ...}
   ```

2. **Frontend loads**
   ```bash
   # Check: http://localhost:5173 shows UI
   # Orb should render in left panel
   ```

3. **WebSocket connects**
   ```bash
   # Check: Status indicator shows "Connected" (green dot)
   ```

4. **Voice input works**
   ```bash
   # Check: Click "Listen" button, speak, see transcript
   ```

5. **Task submission works**
   ```bash
   # Check: Submit simple task, get response in dashboard
   ```

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Check dependencies
pip list | grep fastapi

# Check ANTHROPIC_API_KEY
echo $ANTHROPIC_API_KEY

# Enable debug logging
export LOG_LEVEL=debug
python server.py
```

### Frontend shows blank page
```bash
# Check Node version
node --version  # Should be 16+

# Clear cache and rebuild
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### WebSocket connection fails
```bash
# Check server is running on port 8000
lsof -i :8000

# Check CORS settings in server.py
# Should allow all origins for localhost

# Check firewall
# port 8000 and 5173 should be open
```

### Orb doesn't animate
```bash
# Check browser console (F12)
# Three.js errors?

# Test WebGL support:
# https://webglreport.com/

# Try different browser (Chrome, Firefox)
```

### Voice input not working
```bash
# Check Web Speech API support (Chrome/Edge)
# https://caniuse.com/speech-recognition

# Check microphone permissions
# Browser settings → Privacy → Microphone

# Check browser console for errors
```

### Budget tracking not working
```bash
# Check cost_tracking.json exists
ls -la ~/.openclaw/workspace/

# Check permissions
chmod 755 ~/.openclaw/workspace/

# Reset budget file
echo '[]' > ~/.openclaw/workspace/cost_tracking.json
```

## Testing

### Run Tests
```bash
cd jarvis/backend
pytest tests/ -v

# Specific test file
pytest tests/test_router.py -v

# With coverage
pytest --cov=. tests/
```

### Manual Testing

1. **Test task routing**
   ```bash
   curl -X POST http://localhost:8000/task \
     -H "Content-Type: application/json" \
     -d '{
       "task_type": "lead_gen",
       "content": "Find SaaS companies in NYC",
       "context": {}
     }'
   ```

2. **Test vault operations**
   ```bash
   curl "http://localhost:8000/obsidian/search?query=decision"
   ```

3. **Test budget**
   ```bash
   curl http://localhost:8000/cost/budget
   ```

## Development

### Adding a New Task Type

1. Add handler in `chief_of_staff.py`:
   ```python
   async def your_task(self, content: str, context: Optional[Dict]) -> Dict:
       # Implementation
       return {"result": "..."}
   ```

2. Add route in `server.py`:
   ```python
   elif request.task_type == "your_task":
       result = await chief.your_task(request.content, request.context)
   ```

3. Add UI button in `TaskSubmitter.jsx`:
   ```jsx
   { type: 'your_task', label: '🎯 Your Task', description: 'Description' }
   ```

### Debugging

Enable debug logging:
```python
# In any module
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug("Message")
```

Monitor WebSocket traffic:
```bash
# Browser DevTools > Network > WS
# Filter for /ws/voice
```

## Performance Optimization

### Backend
```python
# Add caching for vault search
from functools import lru_cache

@lru_cache(maxsize=128)
async def search_vault(query):
    # Cached results
```

### Frontend
```jsx
// Memoize expensive components
import { memo } from 'react'
const OrbVisualizer = memo(({ orbState }) => {...})

// Throttle WebSocket updates
import { throttle } from 'lodash'
const handleUpdate = throttle(updateOrb, 100)
```

## Production Deployment

### Heroku
```bash
# Create Procfile
echo "web: python jarvis/backend/server.py" > Procfile

# Deploy
heroku create jarvis-system
git push heroku main
```

### Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy
railway init
railway up
```

### Docker
```bash
# Build image
docker build -t jarvis:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -p 5173:5173 \
  -e ANTHROPIC_API_KEY=sk-... \
  jarvis:latest
```

## Monitoring & Logs

### View Logs
```bash
# Backend logs (stdout)
# Check terminal running server.py

# Cost tracking
cat ~/.openclaw/workspace/cost_tracking.json

# Memory/vault
ls ~/.openclaw/workspace/memory/
```

### Check Health
```bash
# Every 5 minutes
watch -n 300 'curl -s http://localhost:8000/health | jq .'

# Dashboard metrics
curl http://localhost:8000/dashboard | jq '.budget_status'
```

## Updates & Maintenance

### Update Dependencies
```bash
# Python
pip install --upgrade -r requirements.txt

# JavaScript
npm update
npm audit fix
```

### Clean Up
```bash
# Clear old memory files (keep last 30 days)
find ~/.openclaw/workspace/memory -mtime +30 -delete

# Clear cache
rm -rf jarvis/frontend/.vite
rm -rf jarvis/backend/__pycache__
```

## Support

- **Issues**: Check browser console (F12) and backend logs
- **Docs**: See `docs/` folder for API reference
- **Examples**: Check `tests/` for usage examples

---

**Status**: Ready for Development ✅
**Last Updated**: April 2026
