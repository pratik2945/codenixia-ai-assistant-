import os
import uuid

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

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


def api_get(endpoint: str):
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        st.error(f"API Error: {exc}")
        return None


def api_post(endpoint: str, data: dict):
    try:
        resp = requests.post(f"{API_BASE}{endpoint}", json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        st.error(f"API Error: {exc}")
        return None


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
        st.success("API Connected")
        st.caption(f"LLM: {health.get('llm_provider', 'N/A')}")
        st.caption(f"Email: {'✅' if health.get('email_automation') else '⏭️ Skipped'}")

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
                        f"Automation: CSV exported ✅ | Email notification: {result.get('email_status', 'N/A')}"
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
