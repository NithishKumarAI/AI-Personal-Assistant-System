# AI Diary Assistant - `ollama-private`

`ollama-private` is the local/private inference branch. It replaces Gemini with Ollama and replaces Groq Whisper with local Whisper. Notion is still used for storing logs and generated diary entries.

Use this branch when you want AI inference and transcription to run on your machine.

## Who Is This Branch For?

- Users who prefer local LLM inference
- Developers testing an offline-first AI workflow
- Users who do not want journal text sent to Gemini or Groq
- Anyone comfortable installing Ollama, Whisper dependencies, and FFmpeg

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
- Persistence still uses Notion, which is a cloud service.

## Setup

Install Ollama and pull the model:

```bash
ollama pull llama3
```

Set up the Python app:

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

Run the app:

```bash
streamlit run app.py
```

## Environment Variables

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `NOTION_API_KEY` | Yes | None | Notion integration |
| `DATABASE_ID` | Yes | None | Daily Logs database |
| `DAILY_DIARY_DATABASE_ID` | Yes | None | Daily Diary database |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | No | `llama3` | Cleanup and diary model |
| `WHISPER_MODEL` | No | `base` | Local Whisper model |
| `FFMPEG_PATH` | No | None | Optional FFmpeg path |

## Runtime Architecture Notes

- `core/voice.py` records microphone audio with `sounddevice`.
- Audio is saved to `temp_audio.wav`.
- Local Whisper transcribes the audio file.
- `core/llm.py` sends cleanup prompts to Ollama `/api/generate`.
- `rag/diary_generator.py` sends diary prompts to Ollama.
- `core/notion.py` writes logs and generated diaries to Notion.

## Dependencies

- Ollama
- `llama3` model
- FFmpeg
- PyTorch
- Working microphone
- Python packages from `requirements.txt`

## Limitations and Tradeoffs

- Notion remains cloud storage.
- Ollama must be running separately.
- Local Whisper setup depends on FFmpeg and PyTorch.
- Recording depends on local microphone permissions.
- No Gemini fallback routing is implemented in this branch.
- The Dockerfile exists on this branch, but it does not install or run Ollama, FFmpeg, or PyTorch automatically.
- Kubernetes manifests and GCP deployment are not currently implemented.

## Troubleshooting

| Issue | Check |
|---|---|
| Missing config | Confirm `.env` contains Notion variables |
| Ollama unavailable | Start Ollama and pull the configured model |
| Whisper fails | Check FFmpeg, PyTorch, and `WHISPER_MODEL` |
| Recording fails | Check OS microphone permissions |
| Notion error | Check database IDs, property names, and integration sharing |
| Empty diary | Save logs for today before generating a diary |

## Main Branch

Return to the project landing page on [`main`](../../tree/main).
