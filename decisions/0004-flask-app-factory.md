# 0004 — Flask app factory + blueprints, API versioned under `/api/v1`
**Status:** Accepted · **Date:** 2026-10-28

## Context
Synopsis specifies a Flask REST backend with modules: auth, upload/preprocessing, detection,
history. Later phases will add features.

## Decision
- `create_app(config)` factory in `backend/app/__init__.py`; extensions in `extensions.py`.
- One blueprint per feature: `health`, `auth`, `predict`, `history`, `diseases`, all under `/api/v1`.
- Business logic in `services/`, ML in `ml/`, routes stay thin.
- Served by **gunicorn** in the container (not the Flask dev server).

## Consequences
- New features = new blueprint + service; existing routes untouched.
- Testable: tests build an app with `TestingConfig` (SQLite in-memory, fake predictor).
- A breaking API change can ship as `/api/v2` alongside v1.
