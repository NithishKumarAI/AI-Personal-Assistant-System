# AI Diary Assistant - `ollama-private`

`ollama-private` is the privacy-focused local runtime branch. It uses local Whisper for transcription and Ollama + Llama3 for journal cleanup and diary generation. Notion is still used for storage.

Use this branch if you want transcription and AI inference to run on your machine instead of sending journal text to Gemini or Groq.

## Who Should Use This Branch?

- Users who prefer local AI inference
- Developers testing offline-first AI workflows
- Users comfortable installing Ollama, Whisper dependencies, FFmpeg, and PyTorch
- Anyone who wants to keep AI processing local while still using Notion for persistence

## Runtime Workflow

```text
microphone recording or text input
  -> local Whisper transcription
  -> Ollama cleanup
  -> Notion Daily Logs database
  -> Ollama diary generation
  -> Notion Daily Diary database
```

Cloud boundary:

- AI inference runs locally through Ollama.
- Speech transcription runs locally through Whisper.
- Notion remains cloud storage.

## Setup

Install Ollama and pull the default model:

```bash
ollama pull llama3
```

Set up the app:

```bash
git clone https://github.com/NithishKumarAI/AI-Personal-Assistant-System.git
cd AI-Personal-Assistant-System
git checkout ollama-private

python -m venv .venv
.venv\Scripts\activate

pip install torch
pip install -r requirements.txt
copy .env.example .env
```

Start Ollama if needed:

```bash
ollama serve
```

Run Streamlit:

```bash
streamlit run app.py
```

## Environment Variables

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `NOTION_API_KEY` | Yes | None | Notion integration |
| `DATABASE_ID` | Yes | None | Notion Daily Logs database |
| `DAILY_DIARY_DATABASE_ID` | Yes | None | Notion Daily Diary database |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | No | `llama3` | Cleanup and diary model |
| `WHISPER_MODEL` | No | `base` | Local Whisper model |
| `FFMPEG_PATH` | No | None | Optional FFmpeg path |

## Runtime Notes

- `sounddevice` records local microphone audio.
- Whisper transcribes `temp_audio.wav` locally.
- Ollama handles cleanup and diary generation through `/api/generate`.
- Notion stores logs and generated diaries.
- The branch is local-first, but not fully offline because Notion is external storage.

## Dependencies

- Ollama
- Llama3 model
- FFmpeg
- PyTorch
- Working microphone
- Python packages from `requirements.txt`

## Limitations

- Notion remains cloud storage.
- Ollama must be running separately.
- Local transcription depends on FFmpeg, PyTorch, and Whisper model availability.
- Recording depends on local microphone permissions.
- Gemini fallback routing is not used on this branch.
- This branch focuses on local private inference.

## Troubleshooting

| Issue | Check |
|---|---|
| Missing config | Confirm `.env` contains Notion variables |
| Ollama unavailable | Start Ollama and pull the configured model |
| Whisper fails | Check FFmpeg, PyTorch, and `WHISPER_MODEL` |
| Recording fails | Check OS microphone permissions |
| Notion error | Check database IDs, property names, and integration sharing |
| Empty diary | Save logs for today before generating a diary |

## Back to Main

See the project landing page on [`main`](../../tree/main).
