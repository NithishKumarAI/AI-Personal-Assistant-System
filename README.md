# AI Diary Assistant - `gemini-local`

`gemini-local` is the local runtime branch for running the app with cloud AI APIs. It uses Groq Whisper for transcription, Gemini for cleanup and diary generation, and Notion for storage.

Use this branch if you want to test the cloud AI workflow locally with a `.env` file.

## Who Should Use This Branch?

- Developers running the app from a local machine
- Reviewers testing Gemini and Groq integrations
- Users who want `.env` based setup
- Anyone who wants a lighter local setup than `ollama-private`

## Runtime Workflow

```text
voice or text input
  -> Groq Whisper transcription
  -> Gemini cleanup via fallback router
  -> Notion Daily Logs database
  -> Gemini diary generation
  -> Notion Daily Diary database
```

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
| `DATABASE_ID` | Yes | Notion Daily Logs database |
| `DAILY_DIARY_DATABASE_ID` | Yes | Notion Daily Diary database |

The Gemini router tries `PRIMARY_MODEL`, `SECONDARY_MODEL`, and `TERTIARY_MODEL` in order.

## Runtime Notes

- Audio is captured with Streamlit and sent to Groq Whisper.
- Gemini handles journal cleanup and diary generation.
- Notion stores both daily logs and generated diary entries.
- Dates are generated with the Asia/Kolkata timezone.
- This branch uses local `.env` configuration.
- This branch is intended for local execution.

## Limitations

- Uses cloud AI services.
- Requires Groq, Gemini, and Notion credentials.
- Notion is cloud storage.
- Does not use local Whisper or Ollama.
- Not the public deployment branch.

## Troubleshooting

| Issue | Check |
|---|---|
| Missing config | Copy `.env.example` to `.env` and fill required values |
| Transcription failed | Check `GROQ_API_KEY` and browser microphone permission |
| Gemini fallback failed | Check model names, quota, and `GEMINI_API_KEY` |
| Notion error | Check database IDs, property names, and integration sharing |
| No diary found | Save logs first, then generate the diary |

## Back to Main

See the project landing page on [`main`](../../tree/main).
