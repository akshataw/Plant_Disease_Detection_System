# 0005 — PostgreSQL + SQLAlchemy/Alembic; synopsis schema with small additions
**Status:** Accepted · **Date:** 2026-10-28

## Context
Synopsis defines `User`, `Image`, `Prediction` tables (section 7) and requires storing prediction history.

## Decision
- **PostgreSQL 16** container with a named volume `pgdata`.
- ORM: Flask-SQLAlchemy; migrations: Flask-Migrate (Alembic).
- Tables follow the synopsis (`users`, `images`, `predictions`) with these **additions**:
  - `predictions.model_version` (VARCHAR) — which model produced the result.
  - `predictions.top_k` (JSON) — top-3 labels + confidences for later analysis/UI.
  - `predictions.disease_label` (canonical class label) alongside the human-readable `disease_name`.
  - `images.original_filename`, `images.content_type`.
- Passwords stored as bcrypt hashes (column `password_hash`).

## Consequences
- Production-like, concurrent-safe storage; tests use SQLite in-memory for speed.
- Additions are backwards compatible with the synopsis ER diagram.
