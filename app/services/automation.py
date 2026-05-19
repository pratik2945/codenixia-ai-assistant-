import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings
from app.database import export_leads_csv, insert_automation_log, insert_lead


def process_lead_submission(
    name: str,
    email: str,
    phone: str | None = None,
    company: str | None = None,
    message: str | None = None,
    source: str = "web_form",
) -> dict:
    """Automation workflow: Lead capture → DB storage → CSV export → Email notification."""
    lead_id = insert_lead(name, email, phone, company, message, source)
    payload = {"lead_id": lead_id, "name": name, "email": email}

    try:
        csv_path = export_leads_csv()
        insert_automation_log("csv_export", json.dumps({"path": str(csv_path)}), "success")
    except Exception as exc:
        insert_automation_log("csv_export", json.dumps({"error": str(exc)}), "failed")

    email_status = "skipped"
    if settings.email_enabled:
        try:
            _send_lead_notification(name, email, phone, company, message, lead_id)
            email_status = "success"
            insert_automation_log("email_notification", json.dumps(payload), "success")
        except Exception as exc:
            email_status = "failed"
            insert_automation_log(
                "email_notification",
                json.dumps({**payload, "error": str(exc)}),
                "failed",
            )
    else:
        insert_automation_log(
            "email_notification",
            json.dumps({**payload, "reason": "SMTP not configured"}),
            "skipped",
        )

    return {
        "lead_id": lead_id,
        "csv_exported": True,
        "email_status": email_status,
    }


def _send_lead_notification(
    name: str,
    email: str,
    phone: str | None,
    company: str | None,
    message: str | None,
    lead_id: int,
) -> None:
    subject = f"New Lead Captured — {name} (#{lead_id})"
    body = f"""
    <h2>New Lead Submission</h2>
    <p><strong>ID:</strong> {lead_id}</p>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Phone:</strong> {phone or 'N/A'}</p>
    <p><strong>Company:</strong> {company or 'N/A'}</p>
    <p><strong>Message:</strong> {message or 'N/A'}</p>
    <hr>
    <p><em>Automated notification from Codenixia AI Business Assistant</em></p>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_user
    msg["To"] = settings.notify_email
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_user, settings.notify_email, msg.as_string())


def log_chat_automation(session_id: str, user_message: str, reply: str, provider: str) -> None:
    insert_automation_log(
        "chat_response",
        json.dumps({
            "session_id": session_id,
            "user_message": user_message[:200],
            "provider": provider,
        }),
        "success",
    )
