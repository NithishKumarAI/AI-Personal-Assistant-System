# AI Diary Assistant - `gemini-local`

`gemini-local` is the local development branch for running the app with cloud AI services. It uses Groq Whisper for voice transcription, Gemini for text cleanup and diary generation, and Notion for storage.

Use this branch when you want the same AI workflow as `main`, but configured locally with a `.env` file instead of Streamlit Secrets.

## Who Is This Branch For?

- Developers running the app locally
- Users who want Gemini-based inference without deploying to Streamlit Cloud
- Reviewers who want to test the cloud API workflow from their own machine
- Anyone who wants simpler setup than `ollama-private`

## Runtime Workflow

```text
voice or text input
  -> Groq Whisper transcription
  -> Gemini cleanup via fallback router
  -> Notion Daily Logs database
  -> Gemini diary generation
  -> Notion Daily Diary database
```

Compared with `main`:

- Same Groq + Gemini + Notion runtime stack
- Uses `.env` instead of Streamlit Secrets
- Intended for local execution, not hosted demo deployment

## Setup

```bash
git clone https://github.com/NithishKumarAI/AI-Personal-Assistant-System.git
cd AI-Personal-Assistant-System
git checkout gemini-local

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
copy .env.example .env
```

Fill `.env`, then run:

```bash
streamlit run app.py
```

## Environment Variables

| Variable | Required | Purpose |
|---|---:|---|
| `GROQ_API_KEY` | Yes | Groq Whisper transcription |
| `GEMINI_API_KEY` | Yes | Gemini API access |
| `PRIMARY_MODEL` | At least one model | First Gemini model |
| `SECONDARY_MODEL` | Optional | Fallback Gemini model |
| `TERTIARY_MODEL` | Optional | Fallback Gemini model |
| `NOTION_API_KEY` | Yes | Notion integration |
| `DATABASE_ID` | Yes | Daily Logs database |
| `DAILY_DIARY_DATABASE_ID` | Yes | Daily Diary database |

The implemented router reads `PRIMARY_MODEL`, `SECONDARY_MODEL`, and `TERTIARY_MODEL` in order.

## Runtime Architecture Notes

- `core/voice.py` sends browser-recorded audio to Groq Whisper.
- `core/model_router.py` configures Gemini and tries the model fallback chain.
- `core/llm.py` handles entry cleanup prompts.
- `rag/diary_generator.py` uses the same Gemini routing path for diary generation.
- `core/notion.py` writes logs and generated diaries to Notion.

## Limitations and Tradeoffs

- Uses cloud AI services.
- Notion is cloud storage.
- Requires valid Groq, Gemini, and Notion credentials.
- Does not use local Whisper or Ollama.
- Docker and Kubernetes files are not implemented for this branch.

## Troubleshooting

| Issue | Check |
|---|---|
| Missing configuration | Copy `.env.example` to `.env` and fill required values |
| Transcription failed | Check `GROQ_API_KEY` and browser microphone permission |
| Gemini fallback failed | Check model names, quota, and `GEMINI_API_KEY` |
| Notion error | Check database IDs, property names, and integration sharing |
| No diary found | Save logs first, then run diary generation |

## Main Branch

Return to the project landing page on [`main`](../../tree/main).
