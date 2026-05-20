# AI Diary Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Orchestration-Kubernetes-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Production-grade, multi-branch AI diary system demonstrating cloud and local inference architectures, voice capture, Notion persistence, and deployment-ready DevOps practices.

## Why this repository

- Portfolio-quality AI engineering project with real deployment workflows.
- Branch strategy designed for both public demo and privacy-first local usage.
- Clean environment separation to prevent accidental key leakage.
- Recruiter-friendly documentation and architecture walkthroughs.

## Branch strategy

| Branch | Positioning | LLM/STT stack | Storage |
|---|---|---|---|
| `main` | Public production deployment | Gemini + Groq APIs | Demo Notion databases |
| `local-ollama` (legacy: `local-llm`) | Fully local, privacy-focused | Ollama Llama 3 + local Whisper | Private Notion databases |
| `local-gemini` (legacy: `gemini-local`) | Local app, cloud LLM | Gemini API (+ optional Groq) | Private Notion databases |

Branch-specific readme documents:

- `docs/branches/README.main.md`
- `docs/branches/README.local-ollama.md`
- `docs/branches/README.local-gemini.md`

## Quick start

```bash
git clone https://github.com/<your-username>/AI-Personal-Assistant-System.git
cd AI-Personal-Assistant-System
git checkout local-ollama

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

copy env\.env.local-ollama.example .env
streamlit run app.py
```

## Architecture and docs

- Platform architecture: `docs/architecture/overview.md`
- Setup and environment model: `docs/setup/setup.md`
- Docker docs: `docs/deployment/docker/README.md`
- Kubernetes docs: `docs/deployment/kubernetes/README.md`
- Branch operations guide: `docs/operations/branching-and-release.md`

## Screenshots

Add images before sharing publicly:

- `docs/screenshots/dashboard-home.png`
- `docs/screenshots/voice-capture.png`
- `docs/screenshots/diary-output.png`
- `docs/screenshots/k8s-deployment.png`

## Recommended repository layout

```text
.
├─ app.py
├─ core/
├─ rag/
├─ docs/
│  ├─ architecture/
│  ├─ branches/
│  ├─ deployment/
│  │  ├─ docker/
│  │  └─ kubernetes/
│  ├─ operations/
│  ├─ setup/
│  └─ screenshots/
├─ env/
│  ├─ .env.main.example
│  ├─ .env.local-ollama.example
│  └─ .env.local-gemini.example
├─ Dockerfile
├─ .dockerignore
├─ .env.example
└─ README.md
```

## Security and secret hygiene

- Never commit `.env`, `*.pem`, `*.key`, or `secrets.toml`.
- Commit only template files from `env/*.example`.
- Rotate keys immediately if exposed in commits or logs.
- Use separate API keys and Notion databases per branch/environment.

## License

MIT - see `LICENSE`.
