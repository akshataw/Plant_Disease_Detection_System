# 0006 — Docker compose topology; Python 3.11 in containers
**Status:** Accepted · **Date:** 2026-10-28

## Context
User wants the app in Docker, nginx serving the web page, and ngrok for public access.
Host Python is 3.14 (unsupported by TensorFlow). `docker compose` plugin was not installed.

## Decision
`docker-compose.yml` with four services:
| Service | Image | Role |
|---------|-------|------|
| `frontend` | multi-stage: `node:22-alpine` build → `nginx:alpine` | serves React build, proxies `/api/` → backend |
| `backend` | `python:3.11-slim` + `tensorflow-cpu` + gunicorn | Flask API + model inference |
| `db` | `postgres:16-alpine` | persistence |
| `ngrok` | `ngrok/ngrok` | public HTTPS tunnel → `frontend:80` |

- Only nginx publishes a host port (80); backend and db are internal.
- Volumes: `pgdata`, `uploads`; `backend/models/` bind-mounted read-only.
- Gunicorn uses 2 workers × threads to bound memory (each worker loads the model).
- Install the compose plugin on the host (`docker-compose-plugin`).

## Consequences
- One command (`docker compose up --build`) runs everything.
- Backend image is large (~1.5 GB) because of TensorFlow; acceptable for Phase 1.
  Possible later optimisation: TFLite runtime.
