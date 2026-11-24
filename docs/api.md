# REST API — `/api/v1`

All responses are JSON. Errors: `{"error": "message"}` with an appropriate 4xx/5xx status.
Authenticated endpoints need `Authorization: Bearer <access_token>`.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | – | `{status, database, model_loaded, model_version}` (503 if DB down) |
| POST | `/auth/register` | – | Body `{first_name, last_name, email, password (8 chars – 72 bytes UTF-8)}` → 201 `{access_token, refresh_token, user}`; 400 invalid/non-string fields; 409 if email exists |
| POST | `/auth/login` | – | Body `{email, password}` → `{access_token, refresh_token, user}`; 400 malformed body (not a JSON object / non-string fields); 401 on bad credentials |
| POST | `/auth/refresh` | refresh token | → `{access_token}` |
| GET | `/auth/me` | ✔ | Current user |
| POST | `/predict` | ✔ | `multipart/form-data` field `image` (JPG incl. phone MPO/PNG/WEBP, ≤10 MB, ≥32 px, ≤40 MP) → 201 prediction (below). 400 invalid image, 413 too large, 503 model not loaded |
| GET | `/history?page=1&per_page=10` | ✔ | Own predictions, newest first (`per_page` ≤ 50) → `{items, page, per_page, total, pages}` |
| GET | `/history/<id>` | ✔ | Full prediction incl. details; 404 if not owner |
| DELETE | `/history/<id>` | ✔ | Delete prediction (+ image file if unused) → 204 |
| GET | `/images/<id>` | ✔ | Stored JPEG (EXIF stripped); 404 if not owner |
| GET | `/diseases` | – | Knowledge base summary `{items: [{label, crop, disease, is_healthy}]}` |
| GET | `/diseases/<label>` | – | Full knowledge base entry |

## Prediction object
```json
{
  "id": 12,
  "disease_label": "Tomato___Late_blight",
  "disease_name": "Tomato — Late blight",
  "confidence": 0.9731,
  "low_confidence": false,
  "is_healthy": false,
  "model_version": "plant_disease_v1",
  "prediction_date": "2026-10-28T07:43:20.123456+00:00",
  "image_id": 12,
  "image_url": "/api/v1/images/12",
  "top_k": [{"label": "Tomato___Late_blight", "name": "Tomato — Late blight", "confidence": 0.9731}, "..."],
  "details": {
    "label": "Tomato___Late_blight", "crop": "Tomato", "disease": "Late blight", "is_healthy": false,
    "pathogen": "Phytophthora infestans (oomycete)", "description": "...",
    "symptoms": ["..."], "causes": ["..."], "prevention": ["..."], "treatment": ["..."]
  }
}
```
History list items omit `top_k` and `details`.
