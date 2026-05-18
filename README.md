# AI Diary Assistant — Local Gemini (`gemini-local`)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/Gemini-Fallback-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Groq](https://img.shields.io/badge/Groq-Whisper-F55036)](https://groq.com/)
[![Notion](https://img.shields.io/badge/Notion-API-000000?logo=notion&logoColor=white)](https://developers.notion.com/)

**Clone-and-run** branch for developers: same cloud AI stack as the live demo (Groq + Gemini), configured with a local **`.env`** file. Not intended for Streamlit Cloud deployment.

> **Branch guide:** [`main`](../../tree/main) = hosted recruiter demo (Streamlit Secrets), **`gemini-local`** = this branch, [`local-llm`](../../tree/local-llm) = offline Ollama + local Whisper.

---

## Screenshots

| Today's entry | Past diaries |
|---------------|--------------|
| _Add `docs/screenshots/gemini-today.png`_ | _Add `docs/screenshots/gemini-past.png`_ |

---

## Features

- Browser voice capture → **Groq Whisper** transcription
- **Gemini fallback router** with three models:
  - `gemini-2.5-flash-preview`
  - `gemini-2.5-flash`
  - `gemini-2.5-flash-lite`
- Notion-backed activity logs and daily diary generation
- Visible **model attribution** after each save

---

## Architecture

```text
Voice / text (app.py)
        │
        ▼
core/voice.py ──────────► Groq Whisper API
        │
        ▼
core/llm.py ────────────► core/model_router.py (Gemini fallback)
        │
        ▼
core/notion.py ─────────► Daily Logs DB
        │
        ▼
core/diary_service.py ──► rag/* (fetch, combine, generate) ──► Daily Diary DB
```

### Execution flow

1. Record or type a journal note.
2. Transcribe audio with Groq (if using voice).
3. Clean text with Gemini (first available model in the fallback chain).
4. Save to **Daily Logs** with Python-generated `Date` and `Time`.
5. **Generate Diary** aggregates today's logs and writes/updates **Daily Diary**.

---

## Quick start

```bash
git clone https://github.com/NithishKumarAI/AI-Personal-Assistant-System.git
cd AI-Personal-Assistant-System
git checkout gemini-local

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
# Edit .env with your keys

streamlit run app.py
```

---

## Notion database setup

Create two databases and **share each** with your integration.

### Daily Logs DB

| Property | Type |
|----------|------|
| `Content` | **Title** |
| `Date` | **Date** |
| `Time` | **Rich text** |

### Daily Diary DB

| Property | Type |
|----------|------|
| `Diary` | **Title** |
| `Date` | **Date** |

Property names are **case-sensitive** and must match exactly.

---

## Environment variables (`.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for Whisper |
| `GEMINI_API_KEY` | Yes | Google AI Studio / Gemini key |
| `PRIMARY_MODEL` | Yes* | First fallback model |
| `SECONDARY_MODEL` | Recommended | Second fallback |
| `TERTIARY_MODEL` | Recommended | Third fallback |
| `NOTION_API_KEY` | Yes | Notion integration token |
| `DATABASE_ID` | Yes | Daily Logs database ID |
| `DAILY_DIARY_DATABASE_ID` | Yes | Daily Diary database ID |

\*At least one of the three model variables must be set.

Defaults in [`.env.example`](.env.example) match the intended fallback chain.

---

## Project structure

```text
app.py
core/config.py          .env loader
core/validation.py        Startup checks
core/voice.py           Groq transcription
core/model_router.py      Gemini fallback
core/llm.py               Entry cleanup
core/notion.py            Notion writes
core/diary_service.py     Diary workflow
rag/fetch_data.py         Notion reads
rag/combine_logs.py
rag/diary_generator.py
auto_diary.py             CLI diary generator
```

---

## CLI

```bash
python auto_diary.py
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Missing configuration on startup | Copy `.env.example` → `.env`; fill every required key |
| Transcription failed | Verify `GROQ_API_KEY`; check microphone permission in the browser |
| All Gemini models failed | Confirm model names in Google AI Studio; check quota |
| Notion errors | Verify database IDs; confirm property names match schema |
| `ModuleNotFoundError` | Activate venv; run `pip install -r requirements.txt` |

---

## License

MIT — see [LICENSE](LICENSE).
