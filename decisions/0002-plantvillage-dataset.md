# 0002 — PlantVillage 38-class dataset
**Status:** Accepted · **Date:** 2026-10-28

## Context
The synopsis requires a high-accuracy leaf-disease classifier but names no dataset.

## Decision
Use **PlantVillage** (~54k images, 14 crops, 38 classes including healthy classes), loaded via
TensorFlow Datasets (`plant_village`) or Kaggle. Class names follow the canonical
`Crop___Disease` format (e.g. `Tomato___Late_blight`), stored in `class_names.json` next to the model.

## Consequences
- Well-known benchmark; transfer learning typically reaches >95% test accuracy.
- Images are lab-style (single leaf, plain background) → weaker on real field photos.
  Mitigation planned in Phase 3 (PlantDoc fine-tune) and Phase 2 (low-confidence rejection).
- The knowledge base (`backend/app/data/diseases.json`) is keyed by these exact class labels.
