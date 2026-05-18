# AI Personal Journal — Offline Local LLM (`local-llm`)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-000000)](https://ollama.com/)
[![Whisper](https://img.shields.io/badge/Whisper-Local_STT-412991)](https://github.com/openai/whisper)
[![Notion](https://img.shields.io/badge/Notion-API-000000?logo=notion&logoColor=white)](https://developers.notion.com/)

**Privacy-first** branch: speech recognition and text processing run **entirely on your machine** via Whisper + Ollama. Only Notion sync uses the network.

> **Branch guide:** [`main`](../../tree/main) = hosted demo (Gemini + Groq), [`gemini-local`](../../tree/gemini-local) = cloud APIs with `.env`, **`local-llm`** = this offline branch.

---

## Screenshots

| Today's entry | Past diaries |
|---------------|--------------|
| _Add `docs/screenshots/local-today.png`_ | _Add `docs/screenshots/local-past.png`_ |

---

## Architecture

```text
Microphone / keyboard (app.py)
        │
        ▼
core/voice.py ──────────► Local Whisper + FFmpeg
        │
        ▼
core/llm.py ────────────► Ollama (llama3) — localhost
        │
        ▼
core/notion.py ─────────► Daily Logs DB (cloud)
        │
        ▼
core/diary_service.py ──► rag/* ──► Daily Diary DB
```

### Execution flow

1. **Record** up to 30 seconds from your machine microphone (or type text).
2. **Transcribe** with local Whisper (`WHISPER_MODEL`, default `base`).
3. **Clean** text with Ollama (`OLLAMA_MODEL`, default `llama3`).
4. **Save** to **Daily Logs** with Python-generated `Date` and `Time`.
5. **Generate Diary** combines today's logs via Ollama and writes **Daily Diary**.

---

## Prerequisites

| Tool | Purpose |
|------|---------|
| [Ollama](https://ollama.com/) | Local LLM server |
| [FFmpeg](https://ffmpeg.org/) | Required by Whisper |
| Notion integration | Cloud storage for entries |
| Microphone | Voice capture |

```bash
ollama pull llama3
```

---

## Quick start

```bash
git clone https://github.com/NithishKumarAI/AI-Personal-Assistant-System.git
cd AI-Personal-Assistant-System
git checkout local-llm

python -m venv .venv
.venv\Scripts\activate
pip install torch
pip install -r requirements.txt

copy .env.example .env
# Edit .env

streamlit run app.py
```

---

## Notion database setup

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

Property names are **case-sensitive**.

---

## Environment variables (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NOTION_API_KEY` | Yes | — | Integration token |
| `DATABASE_ID` | Yes | — | Daily Logs database ID |
| `DAILY_DIARY_DATABASE_ID` | Yes | — | Daily Diary database ID |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | No | `llama3` | Model name |
| `FFMPEG_PATH` | No | — | Folder containing `ffmpeg` binary |
| `WHISPER_MODEL` | No | `base` | Whisper model size |

---

## Project structure

```text
app.py
core/config.py
core/validation.py       Includes Ollama health check
core/voice.py            Mic + Whisper
core/llm.py              Ollama cleanup
core/notion.py
core/diary_service.py
rag/fetch_data.py
rag/combine_logs.py
rag/diary_generator.py   Ollama diary prompt
auto_diary.py
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
| Ollama warning on startup | Run `ollama serve`; `ollama pull llama3` |
| FFmpeg / Whisper error | Install FFmpeg; set `FFMPEG_PATH` if not on PATH |
| Recording failed | Allow microphone access; close other apps using the mic |
| Notion errors | Verify database IDs and exact property names |
| Slow first transcription | Whisper loads on first use — subsequent runs are faster |
| `torch` not found | `pip install torch` before other requirements |

---

## License

MIT — see [LICENSE](LICENSE).
