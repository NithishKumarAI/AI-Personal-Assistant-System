# AI Diary Assistant — `gemini-local`

Local Streamlit runtime using **Groq Whisper** (transcription) and **Gemini** (cleanup + diary generation), with **Notion** storage. Configure everything through `.env` — no deployment files on this branch.

## Features

- Same modern dashboard UI as `main` and `ollama-private`
- Browser microphone capture → Groq Whisper transcription
- Gemini cleanup with automatic model fallback
- Daily diary generation from Notion logs
- Past diary viewer with date picker
- Asia/Kolkata timezone for timestamps

## Quick Start

```bash
git clone https://github.com/NithishKumarAI/AI-Personal-Assistant-System.git
cd AI-Personal-Assistant-System
git checkout gemini-local

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Add API keys to `.env`, then:

```bash
streamlit run app.py
```

## Screenshots

See the [`main`](../../tree/main/doc/screenshots) branch for UI screenshots.

## Architecture

```text
browser mic or typed text
  -> Groq Whisper API
  -> Gemini cleanup (PRIMARY / SECONDARY / TERTIARY fallback)
  -> Notion Daily Logs
  -> Gemini diary generation
  -> Notion Daily Diary
```

**Cloud APIs:** Groq, Gemini, Notion  
**Not included:** Docker, Cloud Run, Ollama, local Whisper

## Environment Variables

| Variable | Required | Purpose |
|---|---:|---|
| `GROQ_API_KEY` | Yes | Groq Whisper transcription |
| `GEMINI_API_KEY` | Yes | Gemini API access |
| `PRIMARY_MODEL` | Yes* | First Gemini model to try |
| `SECONDARY_MODEL` | No | Fallback model |
| `TERTIARY_MODEL` | No | Fallback model |
| `NOTION_API_KEY` | Yes | Notion integration |
| `DATABASE_ID` | Yes | Daily Logs database ID |
| `DAILY_DIARY_DATABASE_ID` | Yes | Daily Diary database ID |

\*At least `PRIMARY_MODEL` must be set.

## API Keys

- Groq: [console.groq.com](https://console.groq.com)
- Gemini: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- Notion: [notion.so/my-integrations](https://www.notion.so/my-integrations)

## Troubleshooting

| Issue | What to do |
|---|---|
| Missing config | Copy `.env.example` to `.env`; restart Streamlit |
| Transcription failed | Check `GROQ_API_KEY`; allow browser mic |
| Gemini errors | Verify model names and API quota |
| Notion error | Database IDs + integration sharing |

## Other Branches

| Branch | Runtime |
|---|---|
| [`main`](../../tree/main) | Cloud Run — Gemini + Groq |
| [`ollama-private`](../../tree/ollama-private) | Local Ollama + Whisper |

See the [main README](../../tree/main) for deployment details.
