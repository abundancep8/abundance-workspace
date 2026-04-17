"""
JARVIS + Chief of Staff Hybrid System
FastAPI Server with WebSocket Voice Streaming & Neural Engine
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Optional
import uvicorn
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging

from chief_of_staff import ChiefOfStaff
from neural_router import NeuralRouter
from voice_handler import VoiceHandler
from service_automation import ServiceAutomation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="JARVIS Chief of Staff", version="1.0.0")

# CORS setup for mobile/web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system components
chief = ChiefOfStaff()
router = NeuralRouter()
voice = VoiceHandler()
automation = ServiceAutomation()

# Request/Response models
class TaskRequest(BaseModel):
    task_type: str  # "lead_gen", "sales", "research", "remember", "schedule"
    content: str
    context: Optional[dict] = None
    cost_budget: Optional[float] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
    cost: float
    model_used: str
    timestamp: str

class OrbState(BaseModel):
    position: tuple
    scale: float
    rotation: tuple
    color: str
    intensity: float

# WebSocket state tracking
active_connections = {}

@app.on_event("startup")
async def startup_event():
    logger.info("🤖 JARVIS Chief of Staff System Starting...")
    await chief.initialize()
    await automation.initialize()
    logger.info("✅ System initialized and ready")

@app.get("/health")
async def health_check():
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "chief_of_staff": "ready",
            "neural_router": "ready",
            "voice_handler": "ready",
            "service_automation": "ready"
        }
    }

@app.post("/task")
async def submit_task(request: TaskRequest) -> TaskResponse:
    """
    Submit a task to the JARVIS system.
    Routes to Kimi K2.5 (70%) or Claude (30%) based on cost + performance.
    """
    task_id = f"task_{datetime.now().timestamp()}"
    
    # Route task based on type and cost
    model, cost_estimate = router.route_task(
        task_type=request.task_type,
        complexity=len(request.content),
        budget=request.cost_budget
    )
    
    logger.info(f"📋 Task {task_id} routed to {model}")
    
    try:
        # Execute task
        if request.task_type == "lead_gen":
            result = await automation.generate_leads(request.content, request.context)
        elif request.task_type == "sales":
            result = await automation.sales_pipeline(request.content, request.context)
        elif request.task_type == "research":
            result = await chief.research(request.content, request.context)
        elif request.task_type == "remember":
            result = await chief.remember(request.content, request.context)
        elif request.task_type == "schedule":
            result = await automation.schedule_meeting(request.content, request.context)
        else:
            result = await chief.execute(request.task_type, request.content, request.context)
        
        # Track cost
        actual_cost = router.calculate_cost(model, len(str(result)))
        router.track_usage(task_id, model, actual_cost)
        
        return TaskResponse(
            task_id=task_id,
            status="completed",
            result=result,
            cost=actual_cost,
            model_used=model,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"❌ Task {task_id} failed: {e}")
        return TaskResponse(
            task_id=task_id,
            status="failed",
            result={"error": str(e)},
            cost=0,
            model_used=model,
            timestamp=datetime.now().isoformat()
        )

@app.websocket("/ws/voice")
async def voice_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice streaming + neural orb animation.
    Accepts audio chunks, processes voice input, returns TTS + orb state.
    """
    await websocket.accept()
    connection_id = f"conn_{datetime.now().timestamp()}"
    active_connections[connection_id] = websocket
    
    logger.info(f"🎤 Voice connection {connection_id} established")
    
    try:
        while True:
            # Receive audio chunk from frontend
            data = await websocket.receive_json()
            
            if data.get("type") == "audio":
                # Process audio input
                audio_data = data.get("audio")
                intensity = data.get("intensity", 0.5)
                
                # Transcribe audio
                text = await voice.transcribe(audio_data)
                logger.info(f"🎙️ Transcribed: {text}")
                
                # Route & execute
                task_type = "voice_command"
                result = await chief.execute(task_type, text, {"voice": True})
                
                # Generate TTS response
                tts_audio = await voice.synthesize(result.get("response", ""))
                
                # Calculate orb animation based on audio intensity
                orb_state = voice.calculate_orb_state(intensity, text)
                
                # Send response
                await websocket.send_json({
                    "type": "response",
                    "text": result.get("response"),
                    "audio": tts_audio,
                    "orb": orb_state,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    
    except Exception as e:
        logger.error(f"❌ Voice connection {connection_id} error: {e}")
    finally:
        del active_connections[connection_id]
        logger.info(f"🔌 Voice connection {connection_id} closed")

@app.get("/dashboard")
async def get_dashboard():
    """
    Real-time cost tracking + neural engine dashboard.
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "budget_status": router.get_budget_status(),
        "cost_summary": router.get_cost_summary(),
        "recent_tasks": router.get_recent_tasks(limit=10),
        "neural_patterns": chief.get_neural_patterns(),
        "automation_status": {
            "leads_queued": await automation.get_queue_status("leads"),
            "meetings_scheduled": await automation.get_meetings_count(),
            "pipeline_value": await automation.get_pipeline_value()
        }
    }

@app.get("/obsidian/search")
async def search_obsidian(query: str):
    """
    Full-text search across Obsidian vault.
    """
    results = await chief.search_vault(query)
    return {"query": query, "results": results, "count": len(results)}

@app.post("/obsidian/remember")
async def remember_to_vault(content: str, tags: list = None):
    """
    Store knowledge/decision in Obsidian vault.
    """
    note_id = await chief.remember(content, {"tags": tags or []})
    return {"note_id": note_id, "status": "remembered", "timestamp": datetime.now().isoformat()}

@app.get("/cost/budget")
async def get_budget():
    """Get current cost budget and usage."""
    return router.get_budget_status()

@app.post("/cost/alert")
async def set_budget_alert(threshold: float):
    """Set alert when budget reaches threshold."""
    router.set_alert_threshold(threshold)
    return {"alert_threshold": threshold, "status": "configured"}

if __name__ == "__main__":
    # Start server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
