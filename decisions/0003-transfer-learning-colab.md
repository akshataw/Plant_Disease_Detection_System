# 0003 — Transfer learning (MobileNetV2) on Colab GPU; dummy model for local dev
**Status:** Accepted · **Date:** 2026-10-28

## Context
Dev machine is CPU-only with ~8 GB RAM. Training a CNN on 54k images on CPU takes hours.
Synopsis requires a CNN (TensorFlow/Keras), low inference latency and 4 GB RAM minimum.

## Decision
- Model: **MobileNetV2** (ImageNet weights) backbone + GlobalAveragePooling + Dropout + Dense(38, softmax).
  Two stages: frozen backbone, then fine-tune top layers with a low learning rate.
- Input 224×224 RGB; preprocessing = `mobilenet_v2.preprocess_input` (scale to [-1, 1]).
  **Preprocessing is embedded in the model** (Rescaling layer) so the backend only resizes and feeds raw 0–255 pixels — prevents train/serve skew.
- Train in `ml/notebooks/train_plantvillage_colab.ipynb` on a free Colab GPU; export `.keras` + `class_names.json`.
- For local development and tests, `ml/scripts/make_dummy_model.py` creates a tiny random model with
  the same input/output contract so the full stack runs before real training.

## Consequences
- MobileNetV2 is small (~9 MB) and fast on CPU → low latency, fits memory budget.
- Model binaries are gitignored; user drops the trained file into `backend/models/`.
- Swapping to EfficientNet later only requires a new export, thanks to embedded preprocessing.
