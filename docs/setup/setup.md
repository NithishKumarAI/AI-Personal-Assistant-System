# Setup Guide

## 1) Clone and choose branch

```bash
git clone https://github.com/<your-username>/AI-Personal-Assistant-System.git
cd AI-Personal-Assistant-System
git checkout <main|local-ollama|local-gemini>
```

## 2) Python environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

For `local-ollama`, install `torch` before Whisper usage:

```bash
pip install torch
```

## 3) Configure environment

Copy the matching template:

- `main` -> `copy env\.env.main.example .env`
- `local-ollama` -> `copy env\.env.local-ollama.example .env`
- `local-gemini` -> `copy env\.env.local-gemini.example .env`

## 4) API key setup

- Notion integration token: `NOTION_API_KEY`
- Daily logs database id: `DATABASE_ID`
- Daily diary database id: `DAILY_DIARY_DATABASE_ID`
- Gemini API key: `GEMINI_API_KEY` (branch-dependent)
- Groq API key: `GROQ_API_KEY` (branch-dependent)

## 5) Run app

```bash
streamlit run app.py
```

## 6) Optional automation run

```bash
python auto_diary.py
```

## Notion schema requirements

Daily Logs DB:

- `Content` (Title)
- `Date` (Date)
- `Time` (Rich text)

Daily Diary DB:

- `Diary` (Title)
- `Date` (Date)

Property names are case-sensitive.
