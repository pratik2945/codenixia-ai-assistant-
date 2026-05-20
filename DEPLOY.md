# Deploy Live (Git + GitHub + Streamlit Cloud)

One public link — works on **phone, laptop, any browser**.

Example live URL:
`https://codenixia-assistant.streamlit.app`

---

## Step 1 — Create GitHub account

1. Go to [https://github.com](https://github.com)
2. Sign up (free)

---

## Step 2 — Push project to GitHub

Open PowerShell in your project folder:

```powershell
cd C:\Users\ASUS\codenixia-ai-assistant

git add .
git commit -m "Codenixia AI Business Assistant - Round 1"

# Create a NEW empty repo on GitHub (no README), then:
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/codenixia-ai-assistant.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

---

## Step 3 — Deploy on Streamlit Community Cloud (FREE)

1. Go to **[https://share.streamlit.io](https://share.streamlit.io)**
2. Click **Sign in** → login with **GitHub**
3. Click **New app**
4. Fill in:
   - **Repository:** `YOUR_USERNAME/codenixia-ai-assistant`
   - **Branch:** `main`
   - **Main file path:** `frontend/streamlit_app.py`
5. Click **Advanced settings** → **Secrets** → paste:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
LLM_PROVIDER = "gemini"
ADMIN_PASSWORD = "admin123"
STANDALONE = "true"
```

6. Click **Deploy**

Wait 2–5 minutes. You get a link like:

```
https://codenixia-ai-assistant-xxxxx.streamlit.app
```

**This is your LIVE HOSTED PROJECT LINK** — submit this URL to Codenixia.

---

## Step 4 — Test on mobile

1. Copy the `https://....streamlit.app` link
2. Send it to your phone (WhatsApp / email)
3. Open in Chrome/Safari
4. Test: Chatbot → Lead form → Admin (password: `admin123`)

---

## What to submit

| Item | Example |
|------|---------|
| GitHub repo | `https://github.com/YOUR_USERNAME/codenixia-ai-assistant` |
| Live link | `https://your-app.streamlit.app` |
| Demo video | Screen record showing live URL on phone + features |

---

## Get Gemini API key (optional but recommended)

1. Go to [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Create API key
3. Add to Streamlit **Secrets** as `GEMINI_API_KEY`

Without a key, the chatbot still works using built-in fallback replies.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| App crashes on start | Check Secrets are valid TOML format |
| `embedded null character` | Re-save `.env` as UTF-8 (see README) |
| Module not found `app` | Main file path must be `frontend/streamlit_app.py` |
| Admin not opening | Use password from Secrets: `ADMIN_PASSWORD` |

---

## Optional: Deploy API separately (Render)

Only needed if you set `STANDALONE=false` and want a separate FastAPI URL.

1. [render.com](https://render.com) → New Web Service → connect GitHub repo
2. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add env vars: `GEMINI_API_KEY`, `ADMIN_PASSWORD`

For Round 1, **Streamlit Cloud alone is enough** with `STANDALONE=true`.
