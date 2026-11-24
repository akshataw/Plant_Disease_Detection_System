# Tasks — Plant Disease Detection System

Source of truth for progress. Update the checkbox and the **Status log** whenever a task changes state.
Legend: `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked (reason inline)

Related: architecture decisions live in [`decisions/`](decisions/README.md). Synopsis: `../ProjectSynopsis/`.

---

## Phase 0 — Foundation
- [x] P0.1 Read synopsis, capture requirements, agree plan with user
- [x] P0.2 Create `tasks.md`, `decisions/` (ADRs 0001–0011), `CLAUDE.md`, `README.md`
- [x] P0.3 Install docker compose plugin (user-level `~/.docker/cli-plugins`, v5.6.1, sha256 verified — no sudo available)
- [x] P0.4 Scaffold folder layout, `.gitignore`, `.env.example`
- [x] P0.5 `docker-compose.yml` with `frontend`(nginx) / `backend` / `db` / `ngrok` services
- [x] P0.6 Backend health endpoint `GET /api/v1/health` (checks DB + model loaded)
- [x] P0.7 Verify stack boots: `docker compose up --build` → `curl localhost/api/v1/health`

## Phase 1 — MVP (synopsis in-scope)
### Backend
- [x] P1.1 Flask app factory, config, extensions (SQLAlchemy, Migrate, JWT, Bcrypt)
- [x] P1.2 DB models: `User`, `Image`, `Prediction` (synopsis ER + `model_version`, `top_k`)
- [x] P1.3 Initial Alembic migration `d796fec094e7` (auto-applied on backend start)
- [x] P1.4 Auth endpoints: register / login / refresh / me (JWT + bcrypt)
- [x] P1.5 Image validation (ext, MIME, size, Pillow decode) + UUID storage on volume
- [x] P1.6 ML layer: `Predictor` interface, `KerasPredictor`, preprocessing, registry
- [x] P1.7 Dummy model generator script (runs stack before real training)
- [x] P1.8 `POST /api/v1/predict` → store Image + Prediction, return top-3 + disease details
- [x] P1.9 History: list (paginated, owner-only), detail, image fetch (owner-only)
- [x] P1.10 Disease endpoints: list + detail from knowledge base
- [x] P1.11 Knowledge base `diseases.json` for all 38 PlantVillage classes (incl. prevention/treatment)
- [x] P1.12 Pytest suite — 21 tests passing (auth, validation, EXIF strip, predict, history isolation, KB) + 2 Vitest tests

### ML
- [x] P1.13 Colab training notebook (MobileNetV2 transfer learning, PlantVillage 38 classes)
- [x] P1.14 Trained `plant_disease_v1.keras` (9.8 MB) + `class_names.json` locally on CPU via feature extraction (`ml/scripts/train_local_cpu.py`, ADR 0014) — backend now serves v1
- [x] P1.15 Test accuracy **96.39%** (macro F1 0.950) — `ml/reports/metrics.json`, `classification_report.txt`, `confusion_matrix.png`, `training_log.txt`

### Frontend
- [x] P1.16 Vite + React (JS) scaffold, API client, AuthContext, protected routes
- [x] P1.17 Pages: Login, Register, Upload (drag-drop + preview), Result, History, History detail
- [x] P1.18 Responsive CSS
- [x] P1.19 Multi-stage Dockerfile + nginx.conf (static + `/api` proxy + security headers)

### Infra / Delivery
- [x] P1.20 ngrok service in compose (public HTTPS)
- [x] P1.21 End-to-end test — API flow verified locally and over the public ngrok HTTPS URL; 6/6 real held-out PlantVillage leaves classified correctly (97–100% confidence). Browser click-through not automated (no browser in this environment)
- [x] P1.22 README walkthrough + `docs/api.md`

## Dev tooling
- [x] T.1 PostToolUse code-review hook + read-only `code-reviewer` subagent in `.claude/` (ADR 0015) — pipe-tested; live in sessions started from `DetectionSystem/`

## Phase 1R — Code-review fixes (demo hardening, 2026-11-10)
Source: full-app `code-reviewer` run (23 findings). Project is **demo-only**, so findings are ordered by
"would this break or embarrass a demo". Work top to bottom; tick each when fixed + tested.
### Must fix (break real demo inputs)
- [x] R.1 Long passwords (>72 bytes) → 500 on register/login (bcrypt 5). Reject with 400, `check_password` returns False, pin bcrypt
- [x] R.2 iPhone/Samsung "MPO" JPEGs rejected as unsupported → allow `MPO`
- [x] R.3 Decompression-bomb gap (1–2× MAX_PIXELS decoded, ~900 MB/request) → check dims before `load()`
### Should fix (robustness visible in a demo)
- [x] R.4 Non-string / non-object JSON bodies → 500 on auth; duplicate-email race → 500 (return 400 / 409)
- [x] R.5 Delete prediction: remove file only after DB commit
- [x] R.6 Frontend logs user out on transient `/auth/me` error (only clear on 401)
- [x] R.7 HistoryPage never clears `error` on page change
- [x] R.8 `pool_pre_ping` so DB restarts don't cause 500s
- [x] R.9 Migrations load the TF model needlessly (`MODEL_TYPE=none` for `db upgrade`)
- [x] R.10 Downscale stored images (≤1280 px) — smaller history pages over ngrok
- [x] R.11 Centre-crop non-square photos before resize (train/serve skew) — ADR amending 0003
### Nice to have (small)
- [x] R.12 nginx: security headers missing on `/assets/`; set `X-Forwarded-Proto $scheme`
### Resume notes (if paused)
- Phase 1R complete: R.1–R.12 fixed, follow-up `code-reviewer` pass = APPROVE_WITH_SUGGESTIONS (3 MINORs
  fixed: /auth/me retry on transient errors, HistoryPage stale-response guard, docs/api.md updated).
- Nothing in progress. Next candidates only if scope changes: the Deferred list below, then Phase 2.
- New files: `decisions/0016-centre-crop-before-inference.md`, `frontend/security-headers.conf`,
  `backend/tests/test_preprocess.py`.
### Deferred (not needed for a demo — revisit if it ever goes public)
- Rate limiting (already P2.4), login timing email-enumeration, per-user upload quota, refresh-token
  rotation, single-flight refresh, thin-route refactor of auth/history, composite history index,
  JWT secret strength check, dev-only requirements split, frontend `MAX_UPLOAD_MB` sync, extra frontend tests.

## Phase 2 — Quality & insight (planned)
- [ ] P2.1 Grad-CAM heatmap overlay on result
- [ ] P2.2 Low-confidence / "not a leaf" rejection threshold
- [ ] P2.3 Model metrics page (accuracy, confusion matrix)
- [ ] P2.4 Rate limiting (Flask-Limiter)
- [ ] P2.5 Profile update / delete account (synopsis `updateUser`, `deleteUser`)
- [ ] P2.6 Admin role & dashboard
- [ ] P2.7 GitHub Actions CI (pytest + frontend build)
- [ ] P2.8 Train `plant_disease_v2` with augmentation + backbone fine-tuning on Colab GPU (notebook ready) — improve weakest classes: Tomato Early blight (F1 0.74), Corn Gray leaf spot (0.79), Tomato Leaf mold (0.88)

## Phase 3 — Future scope (synopsis out-of-scope / future enhancements)
- [ ] P3.1 Camera capture / PWA (mobile-friendly install)
- [ ] P3.2 Multilingual knowledge base
- [ ] P3.3 Weather-based disease risk
- [ ] P3.4 Fine-tune on PlantDoc for real-field images
- [ ] P3.5 Model versioning / A-B testing via predictor registry
- [ ] P3.6 User feedback loop for relabelling

---

## Status log
| Date | Change |
|------|--------|
| 2026-10-28 | Plan approved; Phase 0 docs (tasks.md, ADRs 0001–0011, CLAUDE.md) written. |
| 2026-10-28 | Compose v5.6.1 installed user-level. Phase 1 backend, frontend, KB (38 classes), Colab notebook, docs done. Stack running on localhost:8080 with dummy model; 21 backend + 2 frontend tests pass; npm audit clean. ADRs 0012–0013 added. Open: P1.14/P1.15 (train on Colab), P1.21 (browser + ngrok check). |
| 2026-10-28 | ngrok tunnel live (public HTTPS). Model v1 trained on CPU (ADR 0014): 96.39% test accuracy, deployed; verified over public URL. Phase 1 complete. Added P2.8 (Colab fine-tune v2). |
| 2026-10-28 | Added automated code review: `.claude/settings.json` hook → `.claude/agents/code-reviewer.md` (ADR 0015). |
| 2026-11-10 | Full-app code review (23 findings). Demo-only scope agreed → Phase 1R (R.1–R.12) added; fixes implemented + re-reviewed (approved), 29 backend + 2 frontend tests pass, stack rebuilt; ADR 0016 (centre-crop). Rest deferred. |
| 2026-11-24 | Project report written: `docs/Project_Report_Plant_Disease_Detection.docx` (97 pp, 14 chapters, real screenshots/diagrams/test & latency measurements). Demo account `demo.report@example.com` holds 16 sample predictions used for screenshots. Placeholders (yellow) for student/college details remain. |
