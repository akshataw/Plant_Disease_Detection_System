# 0007 — ngrok container for public HTTPS
**Status:** Accepted · **Date:** 2026-10-28

## Context
Synopsis requires HTTPS/SSL. User wants the webapp exposed with ngrok.

## Decision
Run ngrok as a compose service tunnelling to `frontend:80`. Authtoken from `.env`
(`NGROK_AUTHTOKEN`); optional static domain via `NGROK_DOMAIN`. Inspector UI exposed on host `4040`.
TLS terminates at ngrok; internal traffic is plain HTTP on the private compose network.

## Consequences
- Public HTTPS URL without managing certificates.
- Free tier URLs change on restart unless a static domain is configured.
- The `ngrok` service is put behind a compose profile (`public`) so local dev works without a token:
  `docker compose --profile public up`.
