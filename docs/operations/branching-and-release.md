# Branching and Release Workflow

## Recommended branching model

- `main`: protected, production deployable, tagged releases only.
- `local-ollama`: stable local privacy profile.
- `local-gemini`: stable local cloud-API profile.
- `feature/*`: short-lived development branches.
- `hotfix/*`: emergency production fixes targeting `main`.

## Pull request rules

- Require at least one review.
- Require CI checks (lint, tests, container build).
- Require branch to be up-to-date before merge.
- Squash merge for feature branches to keep history clean.

## Deployment flow

1. Build and test on feature branch.
2. Merge to target branch (`main`, `local-ollama`, or `local-gemini`).
3. Trigger branch-specific pipeline and smoke tests.
4. For `main`, create semver release tag and deploy.

## Safe environment separation

- Maintain one `.env` template per branch profile in `env/`.
- Use separate API keys and Notion databases for each branch.
- Use branch-based secret sets in CI/CD (`MAIN_*`, `LOCAL_OLLAMA_*`, `LOCAL_GEMINI_*`).
- Never reuse production keys in local branches.
- Rotate keys quarterly and on any suspected exposure.
