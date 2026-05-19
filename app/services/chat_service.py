from app.config import settings

SYSTEM_PROMPT = """You are Codenixia AI Business Assistant."""

def _fallback_response(message: str) -> str:
    lower = message.lower()
    if any(w in lower for w in ["internship", "program", "course", "codenixia"]):
        return "Codenixia offers AI/LLM/Automation Internship Programs. Submit your details in the Lead Form!"
    if any(w in lower for w in ["hello", "hi", "hey"]):
        return "Hello! I am the Codenixia AI Assistant. How can I help you?"
    return "Thanks for your question! I can help with Codenixia programs and AI topics."

def generate_reply(message: str, history: list[dict] | None = None) -> tuple[str, str]:
    provider = settings.llm_provider.lower()
    if provider == "gemini" and settings.gemini_api_key:
        try:
            return _gemini_reply(message, history), "gemini"
        except Exception:
            pass
    if settings.openai_api_key:
        try:
            return _openai_reply(message, history), "openai"
        except Exception:
            pass
    return _fallback_response(message), "fallback"

def _gemini_reply(message: str, history: list[dict] | None = None) -> str:
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    chat_history = []
    if history:
        for msg in history[-10:]:
            role = "user" if msg["role"] == "user" else "model"
            chat_history.append({"role": role, "parts": [msg["content"]]})
    chat = model.start_chat(history=chat_history)
    response = chat.send_message(f"{SYSTEM_PROMPT}\n\nUser: {message}")
    return response.text.strip()

def _openai_reply(message: str, history: list[dict] | None = None) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})
    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages, max_tokens=500)
    return response.choices[0].message.content.strip()
