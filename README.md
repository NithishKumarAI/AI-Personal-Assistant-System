# AI Diary Assistant — `ollama-private`

Privacy-focused local runtime: **local Whisper** transcription, **Ollama (Llama 3)** for text cleanup and diary generation, **Notion** for storage only.

## Features

- Modern Streamlit dashboard (same UI as other branches)
- 30-second microphone recording
- Local Whisper speech-to-text
- Ollama-powered journal cleanup
- One-click daily diary generation from today's logs
- Past diary viewer with date picker
- Asia/Kolkata timezone for log timestamps

## Quick Start

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

Then complete [Full Setup](#full-setup) below and run:

```bash
streamlit run app.py
```

## Screenshots

UI screenshots are maintained on the [`main`](../../tree/main/doc/screenshots) branch:

- [Dashboard](../../tree/main/doc/screenshots/main-dashboard.png)
- [Voice recording](../../tree/main/doc/screenshots/voice-recording.png)
- [Transcription](../../tree/main/doc/screenshots/transcription-output.png)
- [Journal entry](../../tree/main/doc/screenshots/journal-entry.png)
- [Diary viewer](../../tree/main/doc/screenshots/diary-viewer.png)

## Architecture

```text
microphone or typed text
  -> local Whisper (ffmpeg required)
  -> Ollama cleanup (llama3)
  -> Notion Daily Logs
  -> Ollama diary synthesis
  -> Notion Daily Diary
```

**Local:** microphone, Whisper, Ollama  
**Cloud:** Notion storage only (no Gemini, no Groq)

## Full Setup

### 1. Install Ollama

Download and install from [https://ollama.com](https://ollama.com).

Start the server (keep this terminal open):

```bash
ollama serve
```

In another terminal, pull the default model:

```bash
ollama pull llama3
```

Verify:

```bash
ollama list
```

You should see `llama3` in the list.

### 2. Install FFmpeg (required for Whisper)

Whisper calls `ffmpeg` as a subprocess. On Windows, if `ffmpeg` is not on your PATH, set `FFMPEG_PATH` in `.env`.

1. Download an FFmpeg essentials build (for example from [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)).
2. Extract the archive.
3. Set `FFMPEG_PATH` to the folder that contains `ffmpeg.exe` (usually the `bin` folder).

Example:

```env
FFMPEG_PATH=C:\Users\you\Downloads\ffmpeg-...\bin
```

Confirm `ffmpeg.exe` exists inside that folder.

### 3. Configure `.env`

```bash
copy .env.example .env
```

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `NOTION_API_KEY` | Yes | — | Notion integration token |
| `DATABASE_ID` | Yes | — | Daily Logs database ID |
| `DAILY_DIARY_DATABASE_ID` | Yes | — | Daily Diary database ID |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | No | `llama3` | Model for cleanup and diary |
| `WHISPER_MODEL` | No | `base` | Whisper model size |
| `FFMPEG_PATH` | Yes on Windows* | — | Folder with `ffmpeg.exe` |

\*Required on Windows when `ffmpeg` is not already on PATH.

### 4. Install Python dependencies

```bash
pip install torch
pip install -r requirements.txt
```

PyTorch is required by Whisper and is installed separately because it varies by platform.

### 5. Run the app

```bash
streamlit run app.py
```

On startup, the app warns if Ollama or FFmpeg is unreachable before you record audio.

## Optional CLI

Generate today's diary without opening the UI:

```bash
python auto_diary.py
```

This runs the same logic as **Generate Diary** in the app.

## Notion Database Schema

**Daily Logs**

| Property | Type |
|---|---|
| `Content` | Title |
| `Date` | Date |
| `Time` | Rich text |

**Daily Diary**

| Property | Type |
|---|---|
| `Diary` | Title |
| `Date` | Date |

Property names are case-sensitive. Share both databases with your Notion integration.

## Troubleshooting

| Issue | What to do |
|---|---|
| **FFmpeg / WinError 2** | Set `FFMPEG_PATH` to the `bin` folder containing `ffmpeg.exe`. Restart Streamlit. |
| **Ollama unavailable** | Run `ollama serve`, then `ollama pull llama3`. Confirm `OLLAMA_BASE_URL` in `.env`. |
| **Whisper slow on first run** | First transcription downloads/loads the model; later runs are faster. |
| **Empty transcription** | Speak closer to the mic; check `temp_audio.wav` was created after recording. |
| **Recording failed** | Allow microphone access in Windows privacy settings; close other apps using the mic. |
| **Missing config** | Copy `.env.example` to `.env` and fill all Notion variables. |
| **Notion API error** | Verify database IDs, integration access, and exact property names. |
| **No diary generated** | Save at least one log for today, then click **Generate Diary**. |
| **`.env` not picked up** | Run Streamlit from the repo root, or restart after editing `.env`. |

## Project Layout

```text
app.py                 Streamlit UI
auto_diary.py          CLI diary generation
core/config.py         .env loading
core/voice.py          Mic + Whisper + ffmpeg
core/llm.py            Ollama cleanup
core/diary_service.py  Diary workflow
core/notion.py         Notion writes
core/validation.py     Startup checks
rag/                   Notion reads + diary prompt
```

## Other Branches

| Branch | Runtime |
|---|---|
| [`main`](../../tree/main) | Cloud Run deployment — Gemini + Groq |
| [`gemini-local`](../../tree/gemini-local) | Local app — Gemini + Groq via `.env` |

See the [main README](../../tree/main) for the full multi-branch overview.
