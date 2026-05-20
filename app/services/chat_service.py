import logging
import os

from app.config import settings


def _gemini_key() -> str:
    return (os.getenv("GEMINI_API_KEY") or settings.gemini_api_key or "").strip()


def _openai_key() -> str:
    return (os.getenv("OPENAI_API_KEY") or settings.openai_api_key or "").strip()


def _groq_key() -> str:
    return (os.getenv("GROQ_API_KEY") or settings.groq_api_key or "").strip()


def _llm_provider() -> str:
    return (os.getenv("LLM_PROVIDER") or settings.llm_provider or "gemini").lower()


def _has_llm_key() -> bool:
    if _llm_provider() == "openai":
        return bool(_openai_key())
    if _llm_provider() == "groq":
        return bool(_groq_key())
    return bool(_gemini_key()) or bool(_openai_key()) or bool(_groq_key())

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are Codenixia AI Business Assistant for Codenixia's AI/LLM/Automation Internship Program.

Answer questions clearly about:
- Codenixia courses, internships, assessments, and career paths in AI
- Python, FastAPI, Streamlit, LLMs, automation, LangChain, deployment
- Business use cases for AI assistants, lead capture, and workflows

Be helpful, accurate, and concise (2-4 short paragraphs max).
If unsure, say so and suggest using the Lead Capture form to contact the team.
"""

# Used when no valid API key or API call fails
FAQ_ANSWERS: list[tuple[list[str], str]] = [
    (
        ["hello", "hi", "hey", "good morning", "namaste"],
        "Hello! I'm the Codenixia AI Assistant. Ask me about our AI/LLM/Automation internship, "
        "Python, LLMs, or how to apply. You can also submit your details in the Lead Capture form.",
    ),
    (
        ["internship", "program", "course", "codenixia", "assessment", "round"],
        "Codenixia offers a hands-on AI/LLM/Automation Internship focused on building real projects: "
        "chatbots, lead systems, automation workflows, SQLite storage, admin dashboards, and cloud deployment. "
        "Round-1 assessment includes an AI business assistant with GitHub repo, live link, demo video, and architecture diagram. "
        "Deadline and details are shared by the Codenixia team—use the Lead Form if you want follow-up.",
    ),
    (
        ["python", "fastapi", "streamlit", "flask", "django"],
        "Python is the main language for this stack. FastAPI powers the REST backend, Streamlit builds the UI quickly, "
        "and together they are ideal for AI demos and internships. You'll integrate LLM APIs, store data in SQLite, "
        "and deploy to platforms like Render or Streamlit Cloud.",
    ),
    (
        ["llm", "gpt", "gemini", "openai", "langchain", "ai", "machine learning", "ml"],
        "LLMs (Large Language Models) like Gemini and GPT generate human-like text from prompts. "
        "In this project, the chatbot sends your question to an LLM API with a system prompt so answers stay on-topic. "
        "LangChain can add memory, tools, and RAG. For the assessment, a direct API integration is enough.",
    ),
    (
        ["automation", "workflow", "email", "smtp", "lead"],
        "Automation means actions triggered without manual work—for example: form submit → save to database → export CSV → send email. "
        "This project implements lead-capture automation and logs each step in the admin dashboard.",
    ),
    (
        ["deploy", "deployment", "host", "render", "streamlit cloud", "live", "github"],
        "Deploy by pushing code to GitHub, then use Streamlit Community Cloud (free) for the UI link, "
        "or Render/Docker for full-stack hosting. Your live URL must be public HTTPS so reviewers can open it on mobile.",
    ),
    (
        ["sqlite", "database", "mongodb", "storage", "csv"],
        "This project uses SQLite for leads, chat logs, and automation logs—simple and perfect for assessments. "
        "Leads are also exported to CSV automatically after each submission.",
    ),
    (
        ["price", "cost", "fee", "salary", "paid", "stipend"],
        "For fees, stipend, or enrollment details, please submit the Lead Capture form with your contact info. "
        "The Codenixia team will respond directly.",
    ),
    (
        ["deadline", "submit", "timeline", "when"],
        "Check the official Codenixia email for release and submission deadlines. "
        "Typical Round-1 window is ~48 hours from task release. Submit GitHub link, live URL, demo video, and README.",
    ),
    (
        ["docker", "api", "rest", "architecture"],
        "Architecture: Streamlit UI → service layer → SQLite; optional FastAPI REST API; LLM provider (Gemini/OpenAI); "
        "automation for leads. See docs/ARCHITECTURE.md in the project for diagrams.",
    ),
]

_last_llm_error: str | None = None


def get_last_llm_error() -> str | None:
    return _last_llm_error


def _set_error(msg: str) -> None:
    global _last_llm_error
    _last_llm_error = msg
    logger.warning("LLM error: %s", msg)


def _fallback_response(message: str) -> str:
    lower = message.lower()
    for keywords, answer in FAQ_ANSWERS:
        if any(kw in lower for kw in keywords):
            return answer

    if _last_llm_error:
        return (
            f"I'd answer with AI, but the LLM API isn't available right now ({_last_llm_error}). "
            "Please add a valid GEMINI_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY in `.env` (local) or Streamlit Secrets (cloud), "
            "then restart the app.\n\n"
            "Meanwhile: Codenixia's internship covers Python, LLM APIs, automation, and deployment. "
            "Try asking about 'internship', 'Python', 'deployment', or 'automation' for built-in help."
        )

    return (
        "I can help with Codenixia's AI internship, Python, LLMs, automation, and deployment. "
        "Try questions like: 'What is the Codenixia internship?', 'How do I deploy?', or 'What is LangChain?' "
        "For a full AI-powered answer, set a valid GEMINI_API_KEY in your environment."
    )


def generate_reply(message: str, history: list[dict] | None = None) -> tuple[str, str]:
    global _last_llm_error
    _last_llm_error = None

    if not _has_llm_key():
        _set_error("No API key configured")
        return _fallback_response(message), "fallback"

    provider = _llm_provider()

    if provider == "openai" and _openai_key():
        try:
            return _openai_reply(message, history), "openai"
        except Exception as exc:
            _set_error(str(exc))

    if provider == "groq" and _groq_key():
        try:
            return _groq_reply(message, history), "groq"
        except Exception as exc:
            _set_error(str(exc))

    if _gemini_key():
        try:
            return _gemini_reply(message, history), "gemini"
        except Exception as exc:
            _set_error(str(exc))

    if _openai_key() and provider != "openai":
        try:
            return _openai_reply(message, history), "openai"
        except Exception as exc:
            _set_error(str(exc))

    if _groq_key() and provider != "groq":
        try:
            return _groq_reply(message, history), "groq"
        except Exception as exc:
            _set_error(str(exc))

    return _fallback_response(message), "fallback"


def _gemini_reply(message: str, history: list[dict] | None = None) -> str:
    # Try new SDK first, then legacy
    try:
        return _gemini_reply_new_sdk(message, history)
    except ImportError:
        pass
    except Exception as exc:
        if "API key" in str(exc) or "API_KEY" in str(exc):
            raise
        logger.debug("new genai sdk failed: %s", exc)

    import google.generativeai as genai

    genai.configure(api_key=_gemini_key())
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-latest"]
    last_exc = None
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name, system_instruction=SYSTEM_PROMPT)
            chat_history = []
            if history:
                for msg in history[-10:]:
                    role = "user" if msg["role"] == "user" else "model"
                    chat_history.append({"role": role, "parts": [msg["content"]]})
            chat = model.start_chat(history=chat_history)
            response = chat.send_message(message)
            return response.text.strip()
        except Exception as exc:
            last_exc = exc
            continue
    raise last_exc or RuntimeError("All Gemini models failed")


def _gemini_reply_new_sdk(message: str, history: list[dict] | None = None) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=_gemini_key())
    contents = []
    if history:
        for msg in history[-10:]:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=800,
        ),
    )
    return response.text.strip()


def _openai_reply(message: str, history: list[dict] | None = None) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=_openai_key())
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for msg in history[-10:]:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def _groq_reply(message: str, history: list[dict] | None = None) -> str:
    from openai import OpenAI

    client = OpenAI(
        api_key=_groq_key(),
        base_url="https://api.groq.com/openai/v1",
    )
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for msg in history[-10:]:
            role = "user" if msg["role"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=800,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
