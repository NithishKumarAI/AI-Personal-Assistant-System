# AI Diary Assistant — Deployment Showcase (`main`)

[![Streamlit](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/cloud)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/Gemini-Fallback-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Notion](https://img.shields.io/badge/Notion-API-000000?logo=notion&logoColor=white)](https://developers.notion.com/)

Recruiter-facing **live demo** of a voice-to-diary workflow: browser audio → Groq Whisper → Gemini text cleanup (multi-model fallback) → Notion storage → automated daily diary generation.

> **Branch guide:** use **`main`** for the hosted demo, [`gemini-local`](../../tree/gemini-local) to clone and run with `.env`, and [`local-llm`](../../tree/local-llm) for fully offline Ollama + local Whisper.

---

## Screenshots

| Today's entry | Past diaries |
|---------------|--------------|
| _Add `docs/screenshots/main-today.png`_ | _Add `docs/screenshots/main-past.png`_ |

---

## What this branch demonstrates

- **Product engineering:** Streamlit UI with clear capture → clean → save → summarize flow
- **Reliability:** Gemini model fallback chain with visible model attribution
- **Integrations:** Groq speech-to-text, Notion CRUD, REST error handling
- **Deployment hygiene:** Streamlit Secrets (no committed credentials), demo-only data guidance

---

## Architecture

```text
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit UI (app.py)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
  core/voice.py        core/llm.py         rag/fetch_data.py
  Groq Whisper         Gemini router       Notion queries
         │                   │                   │
         └─────────┬─────────┴─────────┬─────────┘
                   ▼                   ▼
            core/notion.py      core/diary_service.py
            (write logs/diary)  (aggregate + generate)
                   │
                   ▼
            Notion API (demo databases)
```

### Execution flow

1. **Capture** — User records audio in the browser or types text.
2. **Transcribe** — Audio file is sent to Groq (`whisper-large-v3-turbo`).
3. **Clean** — Raw text is normalized by Gemini via `core/model_router.py` fallback.
4. **Save log** — Cleaned entry is stored in the **Daily Logs** Notion database with Python-generated date/time.
5. **Generate diary** — All of today's logs are fetched, combined, summarized by Gemini, and written to the **Daily Diary** database (create or update).

---

## Project structure

```text
app.py                      Streamlit frontend
core/
  config.py                 Streamlit Secrets loader
  validation.py             Startup configuration checks
  voice.py                  Groq transcription
  model_router.py           Gemini fallback routing
  llm.py                    Entry cleanup prompt
  notion.py                 Notion writes
  diary_service.py          Diary orchestration
rag/
  fetch_data.py             Notion reads
  combine_logs.py           Log aggregation
  diary_generator.py        Diary prompt
.streamlit/
  config.toml               Theme
  secrets.toml.example      Secrets template
auto_diary.py               CLI: generate today's diary
```

---

## Notion database setup

Create **two** full-page databases and share each with your Notion integration.

### Daily Logs DB

| Property | Type | Notes |
|----------|------|-------|
| `Content` | **Title** | Main log text (case-sensitive) |
| `Date` | **Date** | ISO date from Python |
| `Time` | **Rich text** | Time string from Python |

### Daily Diary DB

| Property | Type | Notes |
|----------|------|-------|
| `Diary` | **Title** | Generated diary body (case-sensitive) |
| `Date` | **Date** | Diary date |

Property names must match **exactly** (Notion is case-sensitive).

---

## Configuration (Streamlit Secrets)

This branch reads configuration from **`st.secrets` only** (not `.env` in production).

| Secret | Purpose |
|--------|---------|
| `GROQ_API_KEY` | Whisper transcription |
| `GEMINI_API_KEY` | Gemini client |
| `PRIMARY_MODEL` | First fallback model |
| `SECONDARY_MODEL` | Second fallback model |
| `TERTIARY_MODEL` | Third fallback model |
| `NOTION_API_KEY` | Notion integration token |
| `DATABASE_ID` | Daily Logs database ID |
| `DAILY_DIARY_DATABASE_ID` | Daily Diary database ID |

See [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example).

### Streamlit Cloud deployment

1. Push the `main` branch to GitHub.
2. [Streamlit Cloud](https://streamlit.io/cloud) → **New app** → select this repo and `main`.
3. Set **Main file** to `app.py`.
4. Open **Secrets** and paste TOML from `secrets.toml.example` with real values.
5. Use **demo Notion databases** only — do not connect personal journals to the public demo.

---

## Run locally (deployment parity)

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# Edit secrets.toml with your keys

streamlit run app.py
```

---

## CLI — generate diary

```bash
python auto_diary.py
```

---

## Troubleshooting

| Issue | Likely cause | Fix |
|-------|----------------|-----|
| App stops at startup | Missing secrets | Fill all keys in Streamlit Secrets / `secrets.toml` |
| Transcription failed | Invalid `GROQ_API_KEY` or network | Verify Groq dashboard; check Cloud outbound access |
| All Gemini models failed | Quota, model name, or API key | Confirm model IDs; try fallback order |
| Notion 400/404 | Wrong database ID or property names | Re-check schema tables above; share DB with integration |
| Title truncated warning | Entry > 2000 chars | Notion title limit; split long logs |

---

## License

MIT — see [LICENSE](LICENSE).
