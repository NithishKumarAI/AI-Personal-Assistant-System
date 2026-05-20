# `main` branch - production deployment

This branch is the recruiter-facing deployment target and should always remain stable, reproducible, and demo-ready.

## Intended use

- Public deployment and portfolio showcase.
- Cloud inference with Gemini and Groq APIs.
- Container-first operation via Docker/Kubernetes.
- Uses non-sensitive demo Notion databases.

## Stack

- Frontend/API: Streamlit (`app.py`)
- LLM providers: Gemini API + Groq API
- Storage: Notion Daily Logs + Daily Diary databases (demo workspace)
- Runtime: Docker image, optionally Kubernetes

## Setup

```bash
git checkout main
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy env\.env.main.example .env
streamlit run app.py
```

## Required environment variables

- `NOTION_API_KEY`
- `DATABASE_ID`
- `DAILY_DIARY_DATABASE_ID`
- `GEMINI_API_KEY`
- `GROQ_API_KEY`

## Deployment notes

- Build image from root `Dockerfile`.
- Publish tagged images (`vX.Y.Z` and `sha-<short-commit>`).
- Deploy only signed/tagged release commits from `main`.
