"""
Codenixia AI Business Assistant — Streamlit UI
Uses built-in Python backend directly (no separate FastAPI server required).
"""
import os
import sys
import uuid
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")


def _apply_streamlit_secrets():
    """Streamlit Cloud stores keys in st.secrets — copy into os.environ."""
    try:
        for key, value in st.secrets.items():
            if isinstance(value, str) and value:
                os.environ.setdefault(key, value)
    except Exception:
        pass


_apply_streamlit_secrets()

# Optional: set USE_EXTERNAL_API=true and API_BASE_URL=https://your-api.onrender.com
USE_EXTERNAL_API = os.getenv("USE_EXTERNAL_API", "false").lower() in ("1", "true", "yes")
API_BASE = os.getenv("API_BASE_URL", "").rstrip("/")

_backend_ready = False


@st.cache_resource
def _init_backend():
    from app.database import init_db

    init_db()
    return True


_init_backend()


def _get(path: str):
    from app.config import settings
    from app.database import export_leads_csv, get_all_leads, get_automation_logs, get_chat_logs
    from app.services.lead_service import get_dashboard_stats

    if path == "/health":
        from app.services.chat_service import get_last_llm_error

        has_key = settings.has_llm_key
        return {
            "status": "healthy",
            "llm_provider": settings.llm_provider,
            "email_automation": settings.email_enabled,
            "llm_configured": has_key,
            "llm_error": get_last_llm_error(),
        }
    if path == "/api/leads":
        return get_all_leads()
    if path.startswith("/api/leads/export"):
        p = export_leads_csv()
        return {"success": True, "path": str(p)}
    if path.startswith("/api/chat/logs"):
        limit = 50
        if "limit=" in path:
            limit = int(path.split("limit=")[1])
        return get_chat_logs(limit=limit)
    if path.startswith("/api/automation/logs"):
        limit = 50
        if "limit=" in path:
            limit = int(path.split("limit=")[1])
        return get_automation_logs(limit=limit)
    if path == "/api/dashboard/stats":
        return get_dashboard_stats()
    return None


def _post(path: str, data: dict):
    from app.services.lead_service import handle_chat, submit_lead

    if path == "/api/chat":
        return handle_chat(data["message"], data.get("session_id", "default"))
    if path == "/api/leads":
        result = submit_lead(
            name=data["name"],
            email=data["email"],
            phone=data.get("phone"),
            company=data.get("company"),
            message=data.get("message"),
            source=data.get("source", "web_form"),
        )
        return {"success": True, **result}
    return None


def api_get(path: str):
    if USE_EXTERNAL_API and API_BASE:
        import requests

        try:
            r = requests.get(f"{API_BASE}{path}", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            st.warning(f"External API unavailable, using built-in backend. ({exc})")
    return _get(path)


def api_post(path: str, data: dict):
    if USE_EXTERNAL_API and API_BASE:
        import requests

        try:
            r = requests.post(f"{API_BASE}{path}", json=data, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            st.warning(f"External API unavailable, using built-in backend. ({exc})")
    return _post(path, data)


st.set_page_config(
    page_title="Codenixia AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-header { font-size: 2rem; font-weight: 700; color: #1E3A5F; }
    .sub-header { color: #64748B; margin-bottom: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=64)
    st.title("Codenixia AI")
    st.caption("Business Automation Assistant")
    page = st.radio(
        "Navigate",
        ["💬 AI Chatbot", "📋 Lead Capture", "📊 Admin Dashboard"],
        label_visibility="collapsed",
    )
    st.divider()
    health = api_get("/health")
    if health:
        st.success("App connected")
        if not health.get("llm_configured"):
            st.warning("No API key — add GEMINI_API_KEY in `.env` or Streamlit Secrets")
        elif health.get("llm_error"):
            st.warning("API key invalid or expired — create a new key at aistudio.google.com")
            st.caption(health.get("llm_error", "")[:80])
        else:
            st.caption(f"AI: {health.get('llm_provider', 'N/A')} active")
        st.caption(f"Email: {'on' if health.get('email_automation') else 'off'}")

if page == "💬 AI Chatbot":
    st.markdown('<p class="main-header">AI Business Assistant</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Ask about Codenixia programs, AI/LLM topics, or automation workflows.</p>',
        unsafe_allow_html=True,
    )

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Type your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = api_post(
                    "/api/chat",
                    {"message": prompt, "session_id": st.session_state.session_id},
                )
            if result:
                reply = result.get("reply", "Sorry, I could not generate a response.")
                provider = result.get("provider", "unknown")
                st.write(reply)
                st.caption(f"Powered by: {provider}")
                if provider == "fallback":
                    st.info(
                        "Using built-in answers. For full AI replies, set a valid **GEMINI_API_KEY** "
                        "in `.env` (local) or Streamlit Secrets (cloud), then restart."
                    )
                st.session_state.messages.append({"role": "assistant", "content": reply})

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.rerun()

elif page == "📋 Lead Capture":
    st.markdown('<p class="main-header">Lead Capture Form</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Submit your details and our team will reach out to you.</p>',
        unsafe_allow_html=True,
    )

    with st.form("lead_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *", placeholder="John Doe")
            email = st.text_input("Email *", placeholder="john@example.com")
            phone = st.text_input("Phone", placeholder="+91 9876543210")
        with col2:
            company = st.text_input("Company / College", placeholder="ABC University")
            message = st.text_area("Message", placeholder="I'm interested in the AI internship program...")

        submitted = st.form_submit_button("Submit Lead", type="primary", use_container_width=True)

        if submitted:
            if not name or not email:
                st.error("Name and Email are required.")
            elif "@" not in email:
                st.error("Please enter a valid email address.")
            else:
                result = api_post(
                    "/api/leads",
                    {
                        "name": name,
                        "email": email,
                        "phone": phone or None,
                        "company": company or None,
                        "message": message or None,
                    },
                )
                if result and result.get("success"):
                    st.success(f"Thank you, {name}! Your details have been submitted (Lead #{result.get('lead_id')}).")
                    st.info(
                        f"Automation: CSV exported | Email: {result.get('email_status', 'N/A')}"
                    )

elif page == "📊 Admin Dashboard":
    st.markdown('<p class="main-header">Admin Dashboard</p>', unsafe_allow_html=True)

    admin_pw = os.getenv("ADMIN_PASSWORD", "admin123")
    password = st.text_input("Admin Password", type="password")

    if password != admin_pw:
        st.warning("Enter the admin password to view dashboard data.")
    else:
        stats = api_get("/api/dashboard/stats")
        if stats:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Leads", stats.get("total_leads", 0))
            c2.metric("Chat Messages", stats.get("total_chat_messages", 0))
            c3.metric("Automations Run", stats.get("total_automations", 0))

        st.divider()

        tab1, tab2, tab3 = st.tabs(["Leads", "Chat Logs", "Automation Logs"])

        with tab1:
            leads = api_get("/api/leads")
            if leads:
                st.dataframe(pd.DataFrame(leads), use_container_width=True)
                if st.button("Export to CSV"):
                    export = api_get("/api/leads/export")
                    if export:
                        st.success(f"Exported to: {export.get('path')}")

        with tab2:
            logs = api_get("/api/chat/logs?limit=50")
            if logs:
                st.dataframe(pd.DataFrame(logs), use_container_width=True)

        with tab3:
            auto_logs = api_get("/api/automation/logs?limit=50")
            if auto_logs:
                st.dataframe(pd.DataFrame(auto_logs), use_container_width=True)
