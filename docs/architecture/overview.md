# Architecture Overview

## High-level flow

```text
User Input (voice/text)
   -> Transcription layer (local Whisper or branch-specific STT)
   -> Prompt cleanup / normalization
   -> LLM inference (Gemini/Groq or Ollama)
   -> Notion persistence (Daily Logs DB)
   -> Diary generation pipeline (rag/*)
   -> Notion persistence (Daily Diary DB)
```

## Core modules

- `app.py`: Streamlit UI, user interactions, orchestration entrypoint.
- `core/voice.py`: microphone capture + local transcription.
- `core/llm.py`: branch-specific LLM cleanup/inference connector.
- `core/notion.py`: Notion API write/update operations.
- `core/diary_service.py`: end-to-end generation workflow.
- `rag/*`: log retrieval and diary synthesis helpers.

## Branch architecture differences

- `main`: cloud-first architecture, deployment-oriented, public demo data.
- `local-ollama`: local inference with Ollama + Whisper for privacy.
- `local-gemini`: local runtime with Gemini API for simpler setup.

## Production posture checklist

- Separate credentials per environment.
- Branch-based release channels.
- Docker image immutability by tag + digest.
- Kubernetes config separated from app source.
- Documentation kept versioned with code.
