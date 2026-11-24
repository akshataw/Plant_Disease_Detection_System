# 0014 — Train v1 locally on CPU by feature extraction (amends 0003)
**Status:** Accepted · **Date:** 2026-10-28

## Context
ADR 0003 planned training on a Colab GPU. The user asked the assistant to train the model directly; the
assistant cannot operate Colab, and the machine is CPU-only (12 cores, ~8 GB RAM). End-to-end fine-tuning
of MobileNetV2 on 43k images would take hours per epoch on this CPU.

## Decision
- `ml/scripts/train_local_cpu.py` runs inside the **backend image** (TensorFlow 2.19 — identical to serving,
  so no version skew) with `tensorflow-datasets`, `scikit-learn`, `matplotlib` installed ad hoc under pip
  constraints that pin the image's existing packages.
- Method: frozen ImageNet MobileNetV2 runs **once** over every image → cached 1280-d features
  (`ml/.data/features_*.npz`, gitignored) → train Dropout + Dense(38) head → reassemble the end-to-end model
  (`Rescaling → MobileNetV2 → GAP → Dropout → Dense`) and verify it matches the head on real test images.
- Same split (TFDS `train[:80%]/[80%:90%]/[90%:]`), same input contract and file names as the notebook.
- Reports (`metrics.json`, `classification_report.txt`, `confusion_matrix.png`, `training_log.txt`) → `ml/reports/`.

## Consequences
- Training takes minutes on CPU; the exported model is a drop-in `plant_disease_v1.keras`.
- No augmentation or backbone fine-tuning → somewhat lower accuracy and robustness than the Colab notebook
  path. The notebook stays as the upgrade path (e.g. `plant_disease_v2`), tracked as a Phase 2 task.
