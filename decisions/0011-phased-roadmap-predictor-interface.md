# 0011 — Phase-wise roadmap & Predictor interface for extensibility
**Status:** Accepted · **Date:** 2026-10-28

## Context
User wants phase-wise development so more features can be added later without rewrites.

## Decision
- Phases: **0** foundation, **1** MVP (synopsis in-scope + details), **2** quality & insight
  (Grad-CAM, rejection threshold, rate limiting, profile mgmt, CI), **3** future scope
  (camera/PWA, multilingual, weather, PlantDoc, model versioning, feedback). Tracked in `tasks.md`.
- ML is behind an abstract `Predictor` (`backend/app/ml/base.py`) with
  `predict(pil_image, top_k) -> list[{label, confidence}]` and a `version` property.
  `ml/registry.py` builds the predictor from config (`MODEL_TYPE`, `MODEL_PATH`), so new backends
  (TFLite, ensembles, A/B) plug in without touching routes.
- Features are isolated blueprints; knowledge base isolated behind `services/disease_info.py`.

## Consequences
- Each phase is shippable on its own.
- Slight upfront abstraction cost in Phase 1.
