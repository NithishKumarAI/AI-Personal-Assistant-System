# `local-gemini` branch (legacy branch: `gemini-local`)

Local runtime profile with Gemini-based cloud inference. Designed for easier setup than local Ollama while preserving private workspace data.

## Intended use

- Run Streamlit app locally.
- Use Gemini API for language processing.
- Use private Notion databases.
- Faster setup than managing local model runtime.

## Stack

- LLM: Gemini API (optional Groq fallback)
- STT: local transcription path from repository implementation
- Storage: private Notion Daily Logs and Daily Diary databases

## Setup

```bash
git checkout local-gemini
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy env\.env.local-gemini.example .env
streamlit run app.py
```

## Required environment variables

- `NOTION_API_KEY`
- `DATABASE_ID`
- `DAILY_DIARY_DATABASE_ID`
- `GEMINI_API_KEY`

## Optional variables

- `GROQ_API_KEY`
- `GEMINI_MODEL`
