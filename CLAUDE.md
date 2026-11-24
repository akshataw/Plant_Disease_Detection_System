# CLAUDE.md — context guide for this project

Plant Disease Detection System: React (Vite, JS) frontend served by nginx, Flask + TensorFlow
backend, PostgreSQL, ngrok tunnel — all via docker compose. Built phase-wise.

## Read first when resuming work
1. `tasks.md` — what's done / in progress / next (update it as you work).
2. `decisions/README.md` — ADR index; read relevant ADRs before changing architecture.
3. `../ProjectSynopsis/*.pdf` — original requirements.

## Rules
- Any non-trivial decision → new ADR `decisions/NNNN-title.md` + index row. Never rewrite an accepted ADR; supersede it.
- Keep `tasks.md` checkboxes and the status log current.
- Backend routes stay thin; logic in `backend/app/services/`, ML behind `backend/app/ml/base.py::Predictor`.
- Model preprocessing lives inside the Keras model (ADR 0003): backend feeds raw 0–255 RGB 224×224.
- Model labels are matched to knowledge base keys via `normalize_label()` (ADR 0012); keep `diseases.json` at 38 entries.
- After editing source files, a hook asks you to run the `code-reviewer` subagent (ADR 0015): batch related files into one review and address BLOCKER/MAJOR findings before finishing.
- Never print or commit `.env` contents (secrets). Host ports bind to 127.0.0.1 (ADR 0013).

## Commands
- Run stack: `docker compose up -d --build` → http://localhost:8080 (add `--profile public` for ngrok)
- Backend tests: `docker compose run --rm --no-deps -v ./backend:/app --entrypoint pytest backend`
- Migrations: `docker compose run --rm -v ./backend:/app --entrypoint flask backend --app wsgi db migrate -m "msg"` (applied automatically on backend start)
- Dummy model: `docker compose run --rm --no-deps --entrypoint python backend /ml/scripts/make_dummy_model.py --out /app/models`
- Frontend: `cd frontend && npm install && npm test && npm run dev`
