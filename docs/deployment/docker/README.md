# Docker Deployment Guide

## Build image

```bash
docker build -t ai-diary-platform:latest .
```

## Run container

```bash
docker run --rm -p 8080:8080 --env-file .env ai-diary-platform:latest
```

## Recommended production practices

- Pin base image versions and rebuild regularly for security updates.
- Use immutable tags in CI (`vX.Y.Z`, commit SHA).
- Scan image with Trivy/Grype in CI.
- Keep secrets out of image; pass via runtime secret store.
- Set health checks and resource limits for container runtime.

## Suggested CI pipeline stages

1. `lint-and-test`
2. `build-image`
3. `security-scan`
4. `push-registry`
5. `deploy-main`
