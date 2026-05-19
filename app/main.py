from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import export_leads_csv, get_all_leads, get_automation_logs, get_chat_logs, init_db
from app.schemas import ChatRequest, ChatResponse, HealthResponse, LeadCreate, LeadResponse
from app.services.lead_service import get_dashboard_stats, handle_chat, submit_lead


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Codenixia AI Business Assistant",
    description="AI-powered business automation assistant with lead capture and workflows",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        llm_provider=settings.llm_provider,
        email_automation=settings.email_enabled,
    )


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        result = handle_chat(request.message, request.session_id)
        return ChatResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/leads", response_model=dict)
def create_lead(lead: LeadCreate):
    try:
        result = submit_lead(
            name=lead.name,
            email=lead.email,
            phone=lead.phone,
            company=lead.company,
            message=lead.message,
            source=lead.source,
        )
        return {"success": True, **result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/leads", response_model=list[LeadResponse])
def list_leads():
    return get_all_leads()


@app.get("/api/leads/export")
def export_leads():
    path = export_leads_csv()
    return {"success": True, "path": str(path)}


@app.get("/api/chat/logs")
def chat_logs(limit: int = 100):
    return get_chat_logs(limit=limit)


@app.get("/api/automation/logs")
def automation_logs(limit: int = 50):
    return get_automation_logs(limit=limit)


@app.get("/api/dashboard/stats")
def dashboard_stats():
    return get_dashboard_stats()
