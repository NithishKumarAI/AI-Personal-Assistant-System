# AI Diary Assistant

A polished Streamlit portfolio application that turns short voice or text notes into structured daily journal entries, stores them in Notion, and generates a readable daily diary using a Gemini multi-model fallback router.

## What It Demonstrates

- Voice-to-text capture with Groq Whisper
- AI text cleanup through Gemini fallback routing
- Notion API integration for log and diary persistence
- Automated daily diary generation from saved activity logs
- Runtime model visibility in the UI
- Lightweight deployment-friendly Streamlit architecture

## Architecture

```text
Voice or text input
        |
        v
Groq Whisper transcription
        |
        v
Gemini fallback router
        |
        v
Cleaned journal entry
        |
        v
Notion activity database
        |
        v
Daily diary generation
        |
        v
Notion diary database
```

## Project Structure

```text
app.py                  Streamlit frontend
core/voice.py           Groq Whisper transcription
core/model_router.py    Gemini fallback routing
core/llm.py             Journal cleanup prompt
core/notion.py          Notion write operations
core/diary_service.py   Daily diary orchestration
rag/fetch_data.py       Notion read operations
rag/diary_generator.py  Diary generation prompt
rag/combine_logs.py     Log aggregation helper
auto_diary.py           CLI entry point for diary generation
```

## Environment Variables

Create a `.env` file locally with:

```text
GROQ_API_KEY=
GEMINI_API_KEY=
PRIMARY_MODEL=
SECONDARY_MODEL=
TERTIARY_MODEL=
NOTION_API_KEY=
DATABASE_ID=
DAILY_DIARY_DATABASE_ID=
```

The app keeps configuration outside the codebase so it remains suitable for local development and Streamlit Cloud deployment.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Voice recording depends on local microphone access. Hosted demos may need to run in text-only mode unless the deployment environment supports server-side audio capture.
