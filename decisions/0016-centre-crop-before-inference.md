# 0016 — Centre-crop non-square images before inference (amends 0003)
**Status:** Accepted · **Date:** 2026-11-10

## Context
ADR 0003 says the backend "only resizes" to 224×224 and feeds raw 0–255 pixels. The model was trained
on square PlantVillage images (256×256 → 224×224), but real uploads are usually 4:3 or 16:9 phone photos.
Resizing those straight to 224×224 stretches them, distorting lesion shapes: a train/serve geometry skew
flagged by the 2026-11-10 full-app code review.

## Decision
`backend/app/ml/preprocess.py::to_model_input` uses `ImageOps.fit` (centre-crop to the target aspect
ratio, then bilinear resize) instead of a plain resize. Pixel normalisation stays inside the model
(ADR 0003 unchanged on that point).

## Consequences
- Square inputs (including all PlantVillage test images) produce exactly the same tensor as before, so
  the reported 96.39% test accuracy still applies.
- Non-square photos keep their proportions. A leaf far from the centre of a very wide photo can be
  partly cropped; users are expected to frame the leaf roughly in the middle (as the upload UI implies).
- Accuracy on real non-square phone photos has not been measured; check it when real samples are
  available (see P3.4 for real-field fine-tuning).
