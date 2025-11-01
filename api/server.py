"""
FastAPI REST API Server for WhatsApp Bot
"""
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.session_manager import SessionManager
from core.optimizer import SpeedOptimizer

app = FastAPI(title="WhatsApp Bot API", version="2.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session manager (global)
session_manager = None
job_queue = {}


class SendRequest(BaseModel):
    numbers: List[str]
    message: str
    sessions: Optional[int] = 1
    priority: Optional[str] = "normal"  # normal, high, urgent
    webhook_url: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str
    status: str
    total_numbers: int
    estimated_time: str


def estimate_time(total_numbers, sessions):
    """Estimate completion time"""
    numbers_per_session = total_numbers / sessions if sessions > 0 else total_numbers
    
    if numbers_per_session <= 50:
        avg_delay = 8
    elif numbers_per_session <= 200:
        avg_delay = 5
    else:
        avg_delay = 3
    
    total_seconds = numbers_per_session * avg_delay
    breaks = (numbers_per_session // 50) * 45
    total_seconds += breaks
    
    minutes = int(total_seconds / 60)
    return f"~{minutes} minutes"


@app.on_event("startup")
async def startup():
    """Initialize sessions on startup"""
    global session_manager
    session_manager = SessionManager()
    try:
        await session_manager.load_all_sessions()
        print(f"API started with {len(session_manager.active_sessions)} sessions")
    except Exception as e:
        print(f"Warning: Could not load sessions on startup: {e}")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    global session_manager
    if session_manager:
        await session_manager.close_all()


@app.post("/send", response_model=JobResponse)
async def send_messages(request: SendRequest, background_tasks: BackgroundTasks):
    """
    Queue messages for sending
    
    Priority levels:
    - urgent: Immediate, max speed
    - high: Fast, minimal delays
    - normal: Balanced speed/safety
    """
    
    global session_manager
    
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    
    job_id = str(uuid.uuid4())
    
    # Create job
    job = {
        'id': job_id,
        'numbers': request.numbers,
        'message': request.message,
        'sessions': request.sessions,
        'priority': request.priority,
        'status': 'queued',
        'created_at': datetime.now(),
        'results': []
    }
    
    job_queue[job_id] = job
    
    # Queue background task
    background_tasks.add_task(
        process_job,
        job_id,
        request.webhook_url
    )
    
    return JobResponse(
        job_id=job_id,
        status="queued",
        total_numbers=len(request.numbers),
        estimated_time=estimate_time(len(request.numbers), request.sessions)
    )


@app.get("/job/{job_id}")
async def get_job_status(job_id: str):
    """Get job status and results"""
    
    if job_id not in job_queue:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_queue[job_id]
    sent = sum(1 for r in job['results'] if r.get('status') == 'sent')
    failed = sum(1 for r in job['results'] if r.get('status') == 'failed')
    
    return {
        'job_id': job_id,
        'status': job['status'],
        'total': len(job['numbers']),
        'sent': sent,
        'failed': failed,
        'progress': f"{len(job['results'])}/{len(job['numbers'])}",
        'results': job['results'][-10:]  # Last 10 results
    }


@app.get("/sessions")
async def get_sessions():
    """List all active sessions"""
    
    global session_manager
    
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    
    sessions = []
    for name, session in session_manager.active_sessions.items():
        sessions.append({
            'name': name,
            'health': session.get('health_score', 100),
            'messages_sent': session.get('messages_sent', 0),
            'status': 'active'
        })
    
    return {'sessions': sessions, 'total': len(sessions)}


@app.post("/session/add")
async def add_session(name: str = "default", headless: bool = True):
    """Add new WhatsApp session"""
    
    global session_manager
    
    if not session_manager:
        session_manager = SessionManager()
    
    try:
        session = await session_manager.create_session(name, headless=headless)
        return {'status': 'success', 'session': name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/session/{name}")
async def remove_session(name: str):
    """Remove session"""
    
    global session_manager
    
    if not session_manager:
        raise HTTPException(status_code=500, detail="Session manager not initialized")
    
    if name in session_manager.active_sessions:
        await session_manager.close_session(name)
        return {'status': 'success', 'message': f'Session {name} removed'}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global session_manager
    
    return {
        'status': 'healthy',
        'sessions': len(session_manager.active_sessions) if session_manager else 0,
        'jobs_queued': len([j for j in job_queue.values() if j['status'] == 'queued']),
        'jobs_processing': len([j for j in job_queue.values() if j['status'] == 'processing'])
    }


async def process_job(job_id: str, webhook_url: Optional[str]):
    """
    Background job processor
    """
    global session_manager
    
    job = job_queue[job_id]
    job['status'] = 'processing'
    
    try:
        # Ensure we have sessions
        if not session_manager:
            session_manager = SessionManager()
        
        if not session_manager.active_sessions:
            await session_manager.create_session("default", headless=True)
        
        # Get optimizer based on priority
        if job['priority'] == 'urgent':
            optimizer = SpeedOptimizer(max_parallel=5)
        elif job['priority'] == 'high':
            optimizer = SpeedOptimizer(max_parallel=3)
        else:
            optimizer = SpeedOptimizer(max_parallel=2)
        
        # Distribute and send
        distribution = await session_manager.distribute_load(job['numbers'])
        results = await optimizer.parallel_send(distribution, job['message'])
        
        job['results'] = results
        job['status'] = 'completed'
        
        # Send webhook if provided
        if webhook_url:
            try:
                import requests
                requests.post(webhook_url, json={
                    'job_id': job_id,
                    'status': 'completed',
                    'results': results
                }, timeout=10)
            except Exception as e:
                print(f"Failed to send webhook: {e}")
            
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)
        print(f"Job {job_id} failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

