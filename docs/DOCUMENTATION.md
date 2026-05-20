# Codenixia AI Business Assistant — Project Documentation

**Version:** 1.0.0  
**Project:** Codenixia AI/LLM/Automation Internship — Round 1 Assessment  
**Title:** AI-Powered Business Automation Assistant

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Project Objectives](#2-project-objectives)
3. [Features & Modules](#3-features--modules)
4. [Technology Stack](#4-technology-stack)
5. [System Architecture](#5-system-architecture)
6. [Project Structure](#6-project-structure)
7. [Installation & Setup](#7-installation--setup)
8. [Configuration](#8-configuration)
9. [User Guide](#9-user-guide)
10. [API Reference](#10-api-reference)
11. [Database Schema](#11-database-schema)
12. [Automation Workflows](#12-automation-workflows)
13. [AI / LLM Integration](#13-ai--llm-integration)
14. [Deployment Guide](#14-deployment-guide)
15. [Assessment Submission Checklist](#15-assessment-submission-checklist)
16. [Troubleshooting](#16-troubleshooting)
17. [Future Enhancements](#17-future-enhancements)

---

## 1. Introduction

The **Codenixia AI Business Assistant** is a full-stack web application that combines an AI-powered chatbot, lead capture system, automation workflows, and an admin dashboard. It is designed to demonstrate skills in LLM integration, business automation, system design, and cloud deployment.

The application helps prospective students and clients learn about Codenixia programs while capturing leads and automating follow-up actions such as data logging and email notifications.

---

## 2. Project Objectives

| Objective | How It Is Met |
|-----------|----------------|
| AI/LLM integration | Gemini or OpenAI API with contextual system prompt |
| Lead management | Web form with validation and SQLite storage |
| Automation | Lead → DB → CSV export → optional email |
| Admin visibility | Dashboard for leads, chats, and automation logs |
| Deployment | Streamlit Cloud / Render / Docker support |
| Documentation | README, architecture diagrams, and this file |

---

## 3. Features & Modules

### 3.1 AI Chatbot

- Interactive chat interface (Streamlit)
- Answers questions about Codenixia, AI, Python, LLMs, automation, and deployment
- Conversation history stored per session in SQLite
- Providers: **Google Gemini** (primary) or **OpenAI GPT**
- Built-in FAQ fallback when API key is missing or invalid

### 3.2 Lead Capture System

- Form fields: Name*, Email*, Phone, Company/College, Message
- Client-side and server-side validation
- Success confirmation with lead ID and automation status

### 3.3 Data Storage

- **SQLite** database at `data/leads.db`
- Tables: `leads`, `chat_logs`, `automation_logs`
- Automatic **CSV export** to `data/leads_export.csv` on each lead submission

### 3.4 Automation Workflow

On every lead submission:

1. Validate input  
2. Insert record into `leads` table  
3. Export all leads to CSV  
4. Send SMTP email notification (if configured)  
5. Log automation event with status (`success` / `failed` / `skipped`)

On every chat message:

1. Log user message  
2. Generate AI (or fallback) response  
3. Log assistant message  
4. Log automation event  

### 3.5 Admin Dashboard

- Password-protected (`ADMIN_PASSWORD`)
- Metrics: total leads, chat messages, automations run
- Tabs: Leads table, Chat logs, Automation logs
- CSV export trigger

### 3.6 REST API (Optional)

- FastAPI backend for programmatic access
- Swagger UI at `/docs`
- Not required for normal Streamlit usage (built-in backend mode)

---

## 4. Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| Web UI | Streamlit |
| REST API | FastAPI + Uvicorn |
| Database | SQLite |
| AI/LLM | Google Gemini API, OpenAI API |
| Data export | CSV (stdlib) |
| Email | SMTP (smtplib) |
| Config | python-dotenv, pydantic-settings |
| Deployment | Docker, Render, Streamlit Community Cloud |

---

## 5. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER (Browser / Mobile)                  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT UI (frontend/streamlit_app.py)        │
│   Pages: AI Chatbot | Lead Capture | Admin Dashboard         │
└─────────────────────────────┬───────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │   Built-in backend (default)   │  Optional: HTTP
              ▼                               ▼
┌─────────────────────────┐       ┌─────────────────────────┐
│      SERVICE LAYER       │       │   FastAPI (app/main)    │
│  chat_service.py         │       │   REST endpoints        │
│  lead_service.py         │       └─────────────────────────┘
│  automation.py           │
└─────────────┬───────────┘
              │
    ┌─────────┼─────────┬──────────────┐
    ▼         ▼         ▼              ▼
┌────────┐ ┌────┐ ┌─────────┐  ┌──────────┐
│ SQLite │ │CSV │ │ Gemini/ │  │   SMTP   │
│   DB   │ │file│ │ OpenAI  │  │  Email   │
└────────┘ └────┘ └─────────┘  └──────────┘
```

For detailed Mermaid diagrams, see [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## 6. Project Structure

```
codenixia-ai-assistant/
│
├── app/                          # Backend application
│   ├── __init__.py
│   ├── main.py                   # FastAPI routes
│   ├── config.py                 # Settings from .env
│   ├── database.py               # SQLite CRUD
│   ├── schemas.py                # Pydantic request/response models
│   └── services/
│       ├── chat_service.py       # LLM + fallback logic
│       ├── lead_service.py       # Chat & lead orchestration
│       └── automation.py         # CSV export, email, logging
│
├── frontend/
│   └── streamlit_app.py          # Main user interface
│
├── docs/
│   ├── DOCUMENTATION.md          # This file
│   └── ARCHITECTURE.md           # Architecture diagrams
│
├── data/                         # Runtime data (gitignored)
│   ├── leads.db                  # SQLite database
│   └── leads_export.csv          # Exported leads
│
├── .streamlit/
│   └── config.toml               # Streamlit settings
│
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container build
├── render.yaml                   # Render.com config
├── start.sh                      # Docker entrypoint (API + UI)
├── run_local.ps1                 # Windows local launcher
├── DEPLOY.md                     # Quick deploy guide
└── README.md                     # Project overview
```

---

## 7. Installation & Setup

### 7.1 Prerequisites

- Python 3.12 or higher  
- Git  
- Internet connection (for LLM APIs and deployment)  
- Gemini or OpenAI API key (recommended)

### 7.2 Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/codenixia-ai-assistant.git
cd codenixia-ai-assistant
```

### 7.3 Create Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 7.4 Environment File

```powershell
copy .env.example .env
```

Edit `.env` and add your API keys (see [Configuration](#8-configuration)).

> **Important:** Save `.env` as **UTF-8** encoding. UTF-16 files cause `embedded null character` errors.

---

## 8. Configuration

### 8.1 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLM_PROVIDER` | No | `gemini` | `gemini` or `openai` |
| `GEMINI_API_KEY` | Yes* | — | Google AI Studio API key |
| `OPENAI_API_KEY` | Yes* | — | OpenAI API key (alternative) |
| `ADMIN_PASSWORD` | No | `admin123` | Admin dashboard password |
| `SMTP_HOST` | No | `smtp.gmail.com` | SMTP server for email |
| `SMTP_PORT` | No | `587` | SMTP port |
| `SMTP_USER` | No | — | Sender email address |
| `SMTP_PASSWORD` | No | — | App password / SMTP password |
| `NOTIFY_EMAIL` | No | — | Recipient for lead alerts |
| `USE_EXTERNAL_API` | No | `false` | Use remote FastAPI instead of built-in |
| `API_BASE_URL` | No | — | External API URL (if enabled) |

\* At least one of `GEMINI_API_KEY` or `OPENAI_API_KEY` is required for full AI responses.

### 8.2 Get a Gemini API Key

1. Visit [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)  
2. Sign in with Google  
3. Click **Create API key**  
4. Paste into `.env`:

```env
GEMINI_API_KEY=your_key_here
LLM_PROVIDER=gemini
```

### 8.3 Gmail SMTP (Optional)

For Gmail, use an [App Password](https://myaccount.google.com/apppasswords):

```env
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_16_char_app_password
NOTIFY_EMAIL=your@gmail.com
```

---

## 9. User Guide

### 9.1 Running Locally

**Option A — Streamlit only (recommended):**

```powershell
.\venv\Scripts\streamlit.exe run frontend/streamlit_app.py
```

Open: **http://localhost:8501**

**Option B — Streamlit + FastAPI:**

Terminal 1:

```powershell
.\venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

Terminal 2:

```powershell
.\venv\Scripts\streamlit.exe run frontend/streamlit_app.py
```

API docs: **http://localhost:8000/docs**

**Option C — Windows script:**

```powershell
.\run_local.ps1
```

### 9.2 AI Chatbot Page

1. Select **AI Chatbot** in the sidebar  
2. Type a question (e.g. "What is the Codenixia internship?")  
3. Press Enter  
4. Check footer: `Powered by: gemini` = real AI; `fallback` = built-in answers  

### 9.3 Lead Capture Page

1. Select **Lead Capture**  
2. Fill required fields (Name, Email)  
3. Click **Submit Lead**  
4. Note lead ID and automation status  

### 9.4 Admin Dashboard

1. Select **Admin Dashboard**  
2. Enter admin password (default: `admin123`)  
3. View metrics and tables  
4. Use **Export to CSV** under Leads tab  

---

## 10. API Reference

Base URL (local): `http://localhost:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health check |
| `POST` | `/api/chat` | Send chat message |
| `POST` | `/api/leads` | Create new lead |
| `GET` | `/api/leads` | List all leads |
| `GET` | `/api/leads/export` | Export leads to CSV |
| `GET` | `/api/chat/logs?limit=100` | Chat history |
| `GET` | `/api/automation/logs?limit=50` | Automation logs |
| `GET` | `/api/dashboard/stats` | Dashboard statistics |

### 10.1 POST /api/chat

**Request:**

```json
{
  "message": "What is FastAPI?",
  "session_id": "user-session-001"
}
```

**Response:**

```json
{
  "reply": "FastAPI is a modern Python web framework...",
  "session_id": "user-session-001",
  "provider": "gemini"
}
```

### 10.2 POST /api/leads

**Request:**

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+91 9876543210",
  "company": "ABC College",
  "message": "Interested in AI internship",
  "source": "web_form"
}
```

**Response:**

```json
{
  "success": true,
  "lead_id": 1,
  "csv_exported": true,
  "email_status": "success"
}
```

---

## 11. Database Schema

### 11.1 Table: `leads`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Full name |
| email | TEXT | Email address |
| phone | TEXT | Phone (optional) |
| company | TEXT | Company/college (optional) |
| message | TEXT | User message (optional) |
| source | TEXT | Default: `web_form` |
| created_at | TEXT | ISO 8601 UTC timestamp |

### 11.2 Table: `chat_logs`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| session_id | TEXT | Chat session identifier |
| role | TEXT | `user` or `assistant` |
| content | TEXT | Message text |
| created_at | TEXT | ISO 8601 UTC timestamp |

### 11.3 Table: `automation_logs`

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| event_type | TEXT | e.g. `csv_export`, `email_notification`, `chat_response` |
| payload | TEXT | JSON details |
| status | TEXT | `success`, `failed`, or `skipped` |
| created_at | TEXT | ISO 8601 UTC timestamp |

---

## 12. Automation Workflows

### 12.1 Lead Submission Flow

```
User submits form
       │
       ▼
Validate name & email
       │
       ▼
INSERT into leads table
       │
       ├──► Export data/leads_export.csv
       │
       ├──► Send email (if SMTP configured)
       │
       └──► INSERT automation_logs
       │
       ▼
Return success + lead_id + statuses
```

### 12.2 Chat Flow

```
User sends message
       │
       ▼
Log to chat_logs (user)
       │
       ▼
Call Gemini/OpenAI (or fallback FAQ)
       │
       ▼
Log to chat_logs (assistant)
       │
       ▼
Log automation event
       │
       ▼
Return reply + provider name
```

---

## 13. AI / LLM Integration

### 13.1 System Prompt

The assistant is instructed to act as **Codenixia AI Business Assistant**, answering questions about internships, Python, FastAPI, Streamlit, LLMs, automation, and deployment in a professional tone.

### 13.2 Provider Selection

1. If `LLM_PROVIDER=openai` and key exists → OpenAI `gpt-4o-mini`  
2. Else if `GEMINI_API_KEY` exists → Gemini (`gemini-2.0-flash`, with fallbacks)  
3. Else if OpenAI key exists → OpenAI  
4. Else → Built-in FAQ fallback  

### 13.3 Verifying AI Is Active

- Sidebar shows: **AI: gemini active**  
- Chat caption: **Powered by: gemini**  
- If you see **fallback**, check API key in `.env` or Streamlit Secrets  

---

## 14. Deployment Guide

### 14.1 Streamlit Community Cloud (Recommended — One Public Link)

1. Push code to GitHub  
2. Go to [share.streamlit.io](https://share.streamlit.io)  
3. **New app** → select repo  
4. Main file: `frontend/streamlit_app.py`  
5. Add Secrets:

```toml
GEMINI_API_KEY = "your_key"
LLM_PROVIDER = "gemini"
ADMIN_PASSWORD = "your_secure_password"
```

6. Deploy → copy `https://your-app.streamlit.app`  

See also: [DEPLOY.md](../DEPLOY.md)

### 14.2 Render (Docker)

1. Connect GitHub repo on [render.com](https://render.com)  
2. Use `render.yaml` or Docker runtime  
3. Set environment variables in dashboard  
4. Deploy  

### 14.3 Docker (Local)

```bash
docker build -t codenixia-assistant .
docker run -p 8501:8501 -p 8000:8000 --env-file .env codenixia-assistant
```

---

## 15. Assessment Submission Checklist

| Deliverable | Status | Notes |
|-------------|--------|-------|
| GitHub repository link | ☐ | Public or accessible to reviewers |
| Live hosted project link | ☐ | `https://....streamlit.app` |
| 5–7 minute demo video | ☐ | Show chat, leads, admin, live URL on mobile |
| Architecture diagram | ☐ | `docs/ARCHITECTURE.md` |
| README / documentation | ☐ | README.md + this file |

### Suggested Demo Video Outline

1. Introduction (30 sec)  
2. Live URL on mobile (30 sec)  
3. AI chatbot demo (1.5 min)  
4. Lead form + automation (1 min)  
5. Admin dashboard (1 min)  
6. Architecture walkthrough (1 min)  
7. GitHub + tech stack (30 sec)  

---

## 16. Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Generic chat replies only | Invalid/expired API key | Create new key at Google AI Studio |
| `embedded null character` | `.env` saved as UTF-16 | Re-save `.env` as UTF-8 |
| `localhost:8000` connection error | Old code calling API | Use latest `streamlit_app.py` (built-in backend) |
| `Powered by: fallback` | No valid LLM key | Set `GEMINI_API_KEY` and restart |
| Email `skipped` | SMTP not configured | Add SMTP variables to `.env` |
| Admin won't open | Wrong password | Check `ADMIN_PASSWORD` in `.env` |
| Streamlit Cloud no AI | Secrets missing | Add keys in app Secrets, reboot |

---

## 17. Future Enhancements

- LangChain agents with tool calling  
- Vector database (RAG) for course document Q&A  
- WhatsApp / Telegram lead notifications  
- JWT authentication for admin API  
- PostgreSQL for production scale  
- Multi-language chatbot support  

---

## Author & License

**Project:** Codenixia AI Business Assistant — Round 1 Assessment  
**License:** MIT  

For architecture diagrams: [ARCHITECTURE.md](./ARCHITECTURE.md)  
For quick deployment: [DEPLOY.md](../DEPLOY.md)  
For overview: [README.md](../README.md)
