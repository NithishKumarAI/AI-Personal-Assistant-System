# AI Diary Assistant — `ollama-private`

Privacy-focused local runtime: **local Whisper**, **Ollama (Llama 3)**, **Notion** storage only.

**Full guide:** [`ollama-private/README.md`](https://github.com/NithishKumarAI/AI-Personal-Assistant-System/blob/ollama-private/README.md)

## Quick Start

```bash
git checkout ollama-private
pip install torch && pip install -r requirements.txt
copy .env.example .env
ollama serve && ollama pull llama3
streamlit run app.py
```

Set `FFMPEG_PATH` on Windows if `ffmpeg` is not on PATH. See the branch README for Ollama, FFmpeg, and troubleshooting details.

[Back to main README](README.md)
