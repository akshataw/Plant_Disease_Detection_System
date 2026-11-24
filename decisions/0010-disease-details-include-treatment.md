# 0010 — Disease details include prevention/treatment (deviation from synopsis)
**Status:** Accepted · **Date:** 2026-10-28

## Context
Synopsis lists "Treatment recommendation" as **out of scope**, but the user wants the system to
"give the disease details" and explicitly chose to include prevention/treatment in Phase 1.

## Decision
Static knowledge base `backend/app/data/diseases.json`, keyed by class label, with fields:
`crop`, `disease`, `is_healthy`, `pathogen`, `description`, `symptoms[]`, `causes[]`,
`prevention[]`, `treatment[]`. Returned with every prediction and via `/api/v1/diseases`.
The UI shows a disclaimer that guidance is general and a local agronomist should be consulted.

## Consequences
- More useful output for farmers; documented scope deviation.
- Content is general guidance, not region-specific chemical dosages.
- JSON can migrate to a DB table / multilingual content later (Phase 3).
