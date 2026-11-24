# ML — training & model artefacts

## Train the real model (Google Colab, free GPU)
1. Open `notebooks/train_plantvillage_colab.ipynb` in Colab (*File → Upload notebook*).
2. *Runtime → Change runtime type → T4 GPU*, then *Run all* (~30–45 min).
   Data comes from TensorFlow Datasets `plant_village` — no Kaggle account needed.
3. The final cell downloads:
   - `plant_disease_v1.keras`, `class_names.json` → copy to `backend/models/`
   - `metrics.json`, `classification_report.txt`, `confusion_matrix.png` → copy to `ml/reports/`
4. Point the backend at the new model in `.env`:
   ```
   MODEL_PATH=/app/models/plant_disease_v1.keras
   ```
   then `docker compose up -d backend` (recreates the container) and check
   `curl localhost:8080/api/v1/health` → `"model_version": "plant_disease_v1"`.

## Train locally on CPU (no GPU needed — ADR 0014)
Feature extraction with the frozen backbone + trained softmax head. Runs in the backend image (TF 2.19):
```
# ml/ is mounted at /work (writable); the compose /ml mount is read-only.
# tensorflow-metadata<1.17 keeps protobuf 5 (required by TF 2.19).
docker compose run --rm --no-deps -v ./ml:/work --entrypoint sh backend -c \
  'pip freeze > /tmp/c.txt && pip install --user -q -c /tmp/c.txt tensorflow-datasets "tensorflow-metadata<1.17" \
     importlib_resources scikit-learn matplotlib \
   && python -u /work/scripts/train_local_cpu.py --data-dir /work/.data --reports-out /work/reports' \
  2>&1 | tee ml/reports/training_log.txt
```
The dataset and cached features go to `ml/.data/` (gitignored), so reruns skip download/extraction.
Outputs: `backend/models/plant_disease_v1.keras`, `class_names.json`, and reports in `ml/reports/`.

## Model contract (must hold for any future model — ADR 0003 / 0011)
- Input: `(None, H, W, 3)` float32, **raw 0–255 RGB**. Any normalisation is a layer inside the model.
- Output: softmax over N classes; `class_names.json` is a JSON list of N labels in output order.
- Labels follow PlantVillage `Crop___Disease` naming; the knowledge base matches them after
  normalisation (ADR 0012), so TFDS and Kaggle variants both work.
- TensorFlow version: backend uses **2.19** — train with the same version when possible.

## Dummy model (local development)
`scripts/make_dummy_model.py` writes an untrained `plant_disease_dummy.keras` with the same contract so the
whole stack runs before training. Predictions are random; the UI shows a "Demo model" warning.
```
docker compose run --rm --no-deps --entrypoint python backend /ml/scripts/make_dummy_model.py --out /app/models
```
