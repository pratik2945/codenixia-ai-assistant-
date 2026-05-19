from app.database import get_all_leads, get_automation_logs, get_chat_logs, insert_chat_log
from app.services.automation import log_chat_automation, process_lead_submission
from app.services.chat_service import generate_reply


def submit_lead(name: str, email: str, **kwargs) -> dict:
    return process_lead_submission(name, email, **kwargs)


def handle_chat(message: str, session_id: str) -> dict:
    history_rows = [
        row for row in get_chat_logs(limit=20)
        if row["session_id"] == session_id
    ]
    history_rows.reverse()

    history = [{"role": row["role"], "content": row["content"]} for row in history_rows]

    insert_chat_log(session_id, "user", message)
    reply, provider = generate_reply(message, history)
    insert_chat_log(session_id, "assistant", reply)
    log_chat_automation(session_id, message, reply, provider)

    return {"reply": reply, "session_id": session_id, "provider": provider}


def get_dashboard_stats() -> dict:
    leads = get_all_leads()
    chats = get_chat_logs(limit=500)
    automations = get_automation_logs(limit=100)

    return {
        "total_leads": len(leads),
        "total_chat_messages": len(chats),
        "total_automations": len(automations),
        "recent_leads": leads[:5],
        "recent_automations": automations[:5],
    }
