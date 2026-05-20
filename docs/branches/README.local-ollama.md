# `local-ollama` branch (legacy branch: `local-llm`)

Privacy-first local inference profile. Voice transcription and LLM processing happen on your own machine.

## Intended use

- Local/offline-first personal journaling.
- No Gemini dependency.
- Private Notion workspace integration.
- Ideal for privacy-conscious users.

## Stack

- LLM: Ollama (`llama3` by default)
- STT: local Whisper (`openai-whisper`)
- Audio: local microphone capture + FFmpeg
- Storage: private Notion Daily Logs and Daily Diary databases

## Setup

```bash
git checkout local-ollama
python -m venv .venv
.venv\Scripts\activate
pip install torch
pip install -r requirements.txt
copy env\.env.local-ollama.example .env
ollama pull llama3
streamlit run app.py
```

## Required environment variables

- `NOTION_API_KEY`
- `DATABASE_ID`
- `DAILY_DIARY_DATABASE_ID`

## Optional local model variables

- `OLLAMA_BASE_URL` (default `http://localhost:11434`)
- `OLLAMA_MODEL` (default `llama3`)
- `WHISPER_MODEL` (default `base`)
- `FFMPEG_PATH` (if ffmpeg is not on `PATH`)
