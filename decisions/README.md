# Decision Log (ADRs)

Every significant decision is recorded here as an Architecture Decision Record so that any
future session (human or AI) can recover *why* things are the way they are without re-reading
the whole history.

## Conventions
- File name: `NNNN-kebab-title.md`, numbered sequentially, never renumbered.
- Sections: **Status** (Proposed / Accepted / Superseded by NNNN), **Date**, **Context**, **Decision**, **Consequences**.
- To change a decision, add a new ADR and mark the old one `Superseded by NNNN` — don't rewrite history.
- Add a row to the index below for every new ADR.

## Index
| # | Title | Status |
|---|-------|--------|
| 0001 | [Record decisions as ADRs](0001-record-decisions-as-adrs.md) | Accepted |
| 0002 | [PlantVillage 38-class dataset](0002-plantvillage-dataset.md) | Accepted |
| 0003 | [Transfer learning (MobileNetV2) on Colab GPU + dummy model for dev](0003-transfer-learning-colab.md) | Accepted |
| 0004 | [Flask app factory + blueprints, `/api/v1`](0004-flask-app-factory.md) | Accepted |
| 0005 | [PostgreSQL + SQLAlchemy/Alembic, synopsis schema + additions](0005-postgresql-schema.md) | Accepted |
| 0006 | [Docker compose topology, Python 3.11 container](0006-docker-compose-topology.md) | Accepted |
| 0007 | [ngrok container for public HTTPS](0007-ngrok-public-https.md) | Accepted |
| 0008 | [Vite + React + JavaScript, plain CSS](0008-vite-react-js.md) | Accepted |
| 0009 | [JWT (access + refresh) + bcrypt in Phase 1](0009-jwt-auth-phase1.md) | Accepted |
| 0010 | [Disease details include prevention/treatment](0010-disease-details-include-treatment.md) | Accepted |
| 0011 | [Phase-wise roadmap & Predictor interface](0011-phased-roadmap-predictor-interface.md) | Accepted |
| 0012 | [Normalised label matching (TFDS/Kaggle names)](0012-label-normalisation.md) | Accepted |
| 0013 | [Port 8080 on localhost, user-level compose, dependency upgrades](0013-local-port-and-dev-environment.md) | Accepted |
| 0014 | [Local CPU training via feature extraction (amends 0003)](0014-local-cpu-training-feature-extraction.md) | Accepted |
| 0015 | [Automated code review hook + project code-reviewer subagent](0015-automated-code-review-hook.md) | Accepted |
| 0016 | [Centre-crop non-square images before inference (amends 0003)](0016-centre-crop-before-inference.md) | Accepted |
