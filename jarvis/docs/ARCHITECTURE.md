# JARVIS + Chief of Staff Architecture Guide

## System Overview

**JARVIS** is a hybrid AI orchestration system combining:
- **Chief of Staff** pattern: Obsidian vault + Claude Code integration for knowledge management
- **JARVIS Audio-Reactive Orb**: FastAPI + WebSocket + Three.js for voice-driven visualization
- **Neural Router**: Cost-optimized task routing between Kimi K2.5 (70%) and Claude (30%)
- **Service Automation**: Lead gen, sales pipeline, CRM integration
- **Mobile-first**: Public URL, responsive design, Web Speech API

## Architecture Layers

### 1. Backend (Python FastAPI)
```
server.py
├── FastAPI app with WebSocket support
├── Task routing endpoint POST /task
├── Voice streaming endpoint WS /ws/voice
├── Dashboard endpoint GET /dashboard
└── Obsidian integration GET /obsidian/*
```

**Key Features:**
- Async task processing
- Real-time voice streaming via WebSocket
- Cost-aware routing (Kimi vs Claude)
- Obsidian vault integration
- Service automation workflows

### 2. Chief of Staff Bridge (Python)
```
chief_of_staff.py
├── Obsidian vault manager
├── Memory + decision logging
├── Pattern recognition engine
├── Claude Code execution layer
└── Context gathering
```

**Responsibilities:**
- Vault operations (read, write, search)
- Pattern extraction and learning
- Memory persistence
- Task execution with context awareness
- Decision tracking

### 3. Neural Router (Cost Optimizer)
```
neural_router.py
├── Kimi K2.5 routing (70% of tasks)
├── Claude routing (30% critical/real-time)
├── Cost tracking + budgeting
├── Performance logging
└── Alert system
```

**Pricing Model:**
- Kimi K2.5: $0.50 per 1M tokens (cost optimized)
- Claude: $3.00 per 1M tokens (premium quality)
- Daily budget: $50 (configurable)
- Auto-alerts at 80%, 90%, 100%

### 4. Voice Handler (Audio I/O)
```
voice_handler.py
├── TTS synthesis (pyttsx3)
├── Audio-reactive orb calculation
├── Neural firing pattern generation
├── Particle effect system
└── Visualization state management
```

**Audio-Reactive Features:**
- Real-time orb deformation based on intensity
- Neural firing visualization
- Color shifts by intensity level
- Pulse animation
- Vertex displacement calculation

### 5. Service Automation
```
service_automation.py
├── Lead generation + enrichment
├── Sales pipeline management
├── Meeting scheduling (Calendly)
├── Email prospecting
├── Proposal generation
└── CRM integration hooks
```

### 6. Frontend (React + Three.js)
```
src/
├── App.jsx (main orchestrator)
├── components/
│   ├── OrbVisualizer.jsx (Three.js 3D)
│   ├── VoiceInterface.jsx (Web Speech API)
│   ├── TaskSubmitter.jsx (task UI)
│   └── Dashboard.jsx (metrics)
├── App.css (responsive styling)
└── vite.config.js (bundler config)
```

**Frontend Stack:**
- React 18.2 for UI
- Three.js r162 for 3D visualization
- Web Speech API for voice input
- WebSocket for real-time sync
- Axios for HTTP requests

## Data Flow

### Voice Command Flow
```
User speaks
↓
Web Speech API captures audio
↓
Send audio via WebSocket to FastAPI
↓
VoiceHandler transcribes audio
↓
ChiefOfStaff executes with context
↓
NeuralRouter handles routing
↓
VoiceHandler generates TTS response
↓
Orb visualization updates
↓
Audio response plays + orb animates
```

### Task Submission Flow
```
User submits task via UI
↓
POST /task request
↓
NeuralRouter decides: Kimi or Claude?
↓
ChiefOfStaff gathers vault context
↓
Execute with LLM
↓
Store patterns + remember outcome
↓
Track cost + budget
↓
Return result + metrics
```

### Cost Optimization Flow
```
Task submitted
↓
Estimate cost for both models
↓
Check remaining budget
↓
Route to cheapest viable option
↓
Execute task
↓
Calculate actual cost
↓
Update budget tracking
↓
Check alerts + generate report
```

## File Structure
```
jarvis/
├── backend/
│   ├── server.py              # FastAPI main
│   ├── chief_of_staff.py      # Obsidian + memory
│   ├── neural_router.py       # Cost routing
│   ├── voice_handler.py       # TTS + orb
│   ├── service_automation.py  # Business workflows
│   ├── requirements.txt       # Python deps
│   └── .env.example           # Config template
├── frontend/
│   ├── index.html             # Entry HTML
│   ├── vite.config.js         # Build config
│   ├── package.json           # JS deps
│   └── src/
│       ├── main.jsx           # React entry
│       ├── App.jsx            # Main component
│       ├── App.css            # Styling
│       └── components/
│           ├── OrbVisualizer.jsx
│           ├── VoiceInterface.jsx
│           ├── TaskSubmitter.jsx
│           └── Dashboard.jsx
├── tests/
│   ├── test_router.py         # Cost routing tests
│   ├── test_chief.py          # Chief of Staff tests
│   └── test_integration.py    # E2E tests
├── docs/
│   ├── ARCHITECTURE.md        # This file
│   ├── SETUP.md               # Installation guide
│   ├── API.md                 # API reference
│   └── SERVICE_WORKFLOWS.md   # Business automation
└── README.md
```

## API Endpoints

### Health & Status
- **GET** `/health` - System health check
- **GET** `/dashboard` - Real-time metrics

### Task Execution
- **POST** `/task` - Submit task with type + content
  - Routes to Kimi or Claude
  - Returns: task_id, status, result, cost, model_used

### Voice Streaming
- **WS** `/ws/voice` - WebSocket for real-time voice
  - Send: `{type: "audio", audio: base64_data, intensity: 0-1}`
  - Receive: `{type: "response", text, audio, orb, timestamp}`

### Obsidian Integration
- **GET** `/obsidian/search?query=term` - Search vault
- **POST** `/obsidian/remember` - Store knowledge
  - Body: `{content: text, tags: [...]}`

### Cost Tracking
- **GET** `/cost/budget` - Current budget status
- **POST** `/cost/alert` - Set budget alert threshold

## Environment Setup

```bash
# Backend
cd jarvis/backend
cp .env.example .env
# Edit .env with:
ANTHROPIC_API_KEY=sk-...
KIMI_API_KEY=... (optional for multi-provider)
VAULT_PATH=/Users/abundance/.openclaw/workspace/vault
BUDGET_DAILY=50.0

pip install -r requirements.txt
python server.py

# Frontend (in separate terminal)
cd jarvis/frontend
npm install
npm run dev
```

## Key Design Patterns

### 1. **Cost-Aware Routing**
- Default: 70% Kimi (cheap + fast), 30% Claude (premium)
- Logic: Estimate both, pick cheapest that meets requirements
- Budget-aware: Falls back to Kimi if budget tight

### 2. **Memory Persistence**
- Vault: Structured decisions, patterns, backlinks
- Memory: Raw logs in JSON
- CONVERSATION_LOG: Distilled learnings + insights
- Auto-sync to Obsidian for backups

### 3. **Audio-Reactive Visualization**
- Intensity drives scale, color, rotation speed
- Neural firing pattern matches text complexity
- Pulse frequency = 2 + (intensity × 4)
- Real-time vertex deformation on GPU

### 4. **Service Business Automation**
- Lead pipeline from prospects → deals → closed
- Calendly integration for scheduling
- Email outreach via Mailgun
- Proposal auto-generation from deal data

## Scaling Considerations

### For Production:
1. **Database**: Replace JSON with PostgreSQL
2. **Caching**: Add Redis for expensive vault queries
3. **Monitoring**: Integrate Sentry for error tracking
4. **Logging**: ELK stack for centralized logs
5. **Auth**: Add OAuth2 + API key management
6. **Rate Limiting**: Implement per-user budgets

### Performance Targets:
- Voice transcription: <2s latency
- Task routing decision: <100ms
- Vault search: <500ms
- Orb animation: 60 FPS
- WebSocket round-trip: <500ms

## Security Notes

- Store API keys in .env (never commit)
- Validate all user inputs
- Rate limit WebSocket connections
- Encrypt sensitive data at rest (vault, budgets)
- Audit log all cost tracking
- CORS restricted to approved domains

## Testing Strategy

```bash
# Run all tests
pytest tests/ -v

# Specific tests
pytest tests/test_router.py::test_kimi_routing -v
pytest tests/test_chief.py::test_obsidian_remember -v

# Coverage
pytest --cov=jarvis tests/
```

## Deployment

### Local Development
```bash
# Terminal 1: Backend
cd jarvis/backend && python server.py

# Terminal 2: Frontend
cd jarvis/frontend && npm run dev

# Access: http://localhost:5173
```

### Docker (Production)
```bash
docker build -t jarvis-system .
docker run -p 8000:8000 -p 5173:5173 \
  -e ANTHROPIC_API_KEY=sk-... \
  jarvis-system
```

### Vercel/Netlify
```bash
cd jarvis/frontend
npm run build
# Deploy dist/ to Vercel
```

## Next Steps

1. Wire in Anthropic API key when available
2. Test voice input with local Whisper model
3. Integrate real Calendly API
4. Add database layer (PostgreSQL)
5. Implement Mailgun email integration
6. Set up monitoring + alerting
7. Deploy to production (Vercel + Railway)

---

**Last Updated:** April 2026
**Status:** MVP Complete - Ready for Integration
