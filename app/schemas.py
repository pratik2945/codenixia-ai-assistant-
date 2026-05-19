from pydantic import BaseModel, EmailStr, Field


class LeadCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str | None = Field(None, max_length=20)
    company: str | None = Field(None, max_length=100)
    message: str | None = Field(None, max_length=1000)
    source: str = "web_form"


class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    company: str | None
    message: str | None
    source: str
    created_at: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default="default")


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    provider: str


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    email_automation: bool
