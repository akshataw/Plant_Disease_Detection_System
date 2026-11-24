# 0012 — Normalised label matching between model classes and knowledge base
**Status:** Accepted · **Date:** 2026-10-28

## Context
PlantVillage class names differ between sources: TFDS uses `Corn___Common_rust`, `Cherry___healthy`;
Kaggle uses `Corn_(maize)___Common_rust_`, `Cherry_(including_sour)___healthy`. The training notebook exports
whatever names the dataset provides into `class_names.json`.

## Decision
`services/disease_info.normalize_label()` lower-cases, removes parenthesised text and collapses non-alphanumerics
to `_`. Knowledge base keys (Kaggle-style) and model labels are both normalised before lookup. A test asserts all
38 TFDS labels and all KB keys resolve, and that normalisation keeps the 38 entries distinct.
Unknown labels fall back to a name parsed from the label with empty detail lists.

## Consequences
- Either dataset source works without editing the knowledge base.
- Supersedes the CLAUDE.md rule "keys must match exactly".
