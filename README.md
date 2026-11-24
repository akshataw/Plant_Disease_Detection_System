# LeafScan — Plant Disease Detection System

Upload a photo of a plant leaf → a CNN (MobileNetV2 transfer learning on PlantVillage, 38 classes / 14 crops)
predicts the disease → the app shows confidence, alternatives, symptoms, causes, prevention and treatment,
and stores the result in the user's history.

Built from `../ProjectSynopsis/` · progress in [`tasks.md`](tasks.md) · decisions in [`decisions/`](decisions/README.md).

## Architecture
```
Internet ──HTTPS──> ngrok ──> nginx (frontend container, 127.0.0.1:8080)
                                ├─ /       → React build (Vite, JS)
                                └─ /api/*  → backend: Flask + gunicorn + TensorFlow (MobileNetV2)
                                               ├─ PostgreSQL 16 (volume pgdata)
                                               └─ uploads volume (EXIF-stripped JPEGs)
```

| Folder | Contents |
|--------|----------|
| `frontend/` | React app, `nginx.conf`, multi-stage Dockerfile |
| `backend/` | Flask app (`app/api` blueprints, `app/services`, `app/ml` predictor), migrations, tests |
| `ml/` | Colab training notebook, dummy model script, reports |
| `docs/` | [API reference](docs/api.md) |
| `decisions/` | Architecture Decision Records |

## Quick start
Prerequisites: Docker with the compose plugin.

```bash
cp .env.example .env            # then set POSTGRES_PASSWORD and JWT_SECRET_KEY to long random values:
python3 -c "import secrets; print(secrets.token_hex(32))"

# Model: backend/models/plant_disease_v1.keras (trained, 96.4% test accuracy — gitignored, so on a fresh
# clone retrain with ml/README.md, or use the demo model: MODEL_PATH=/app/models/plant_disease_dummy.keras
# after running make_dummy_model.py)
docker compose build backend

docker compose up -d --build
curl localhost:8080/api/v1/health
```
Open **http://localhost:8080**, sign up, upload a leaf photo.

> Port 8080 is used because port 80 on this machine is taken by another project (ddev-router).
> Change `HTTP_PORT` in `.env` if needed. The port is bound to 127.0.0.1 only.

### Public HTTPS URL with ngrok
1. Create a free account at https://dashboard.ngrok.com and copy your authtoken.
2. Put it in `.env` → `NGROK_AUTHTOKEN=...` (optionally `NGROK_DOMAIN=` your free static domain).
3. `docker compose --profile public up -d`
4. Get the URL: `docker compose logs ngrok | grep -o 'url=https[^ ]*'` (or open http://localhost:4040).

Free-tier ngrok shows a one-time browser warning page before the app.

### Model
`plant_disease_v1` — MobileNetV2 features + softmax head, **96.39% test accuracy** on PlantVillage
(reports in `ml/reports/`). Retrain locally on CPU (~20 min first run) or on Colab — see [`ml/README.md`](ml/README.md).
To install a newly trained model:
Copy `plant_disease_v1.keras` + `class_names.json` into `backend/models/`, set
`MODEL_PATH=/app/models/plant_disease_v1.keras` in `.env`, then `docker compose up -d backend`.

## Development
```bash
# Backend tests (21 tests, SQLite + fake predictor; no model needed)
docker compose run --rm --no-deps -v ./backend:/app --entrypoint pytest backend

# Frontend
cd frontend && npm install && npm test && npm run dev     # dev server proxies /api → localhost:5000

# New DB migration after changing models
docker compose run --rm -v ./backend:/app --entrypoint flask backend --app wsgi db migrate -m "describe change"
```

## Security notes
- Secrets live only in `.env` (gitignored, `chmod 600`); never commit it.
- Passwords hashed with bcrypt; JWT access (30 min) + refresh (7 days) tokens.
- Uploads validated (type, size, decodability, decompression-bomb guard) and re-encoded to strip EXIF/GPS data.
- Users can only access their own predictions and images (others get 404).
- nginx sends CSP, X-Frame-Options, nosniff, Referrer-Policy; host ports bound to localhost; HTTPS via ngrok.

## Roadmap
Phase 1 (MVP) is implemented. Phase 2: Grad-CAM, rejection threshold, rate limiting, profile management, CI.
Phase 3: camera/PWA, multilingual, weather-based risk, PlantDoc fine-tuning, model versioning. See `tasks.md`.

Disease guidance is general information; always confirm with a local agricultural expert.
