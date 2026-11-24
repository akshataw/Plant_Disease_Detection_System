# 0013 — Host port 8080 on localhost, user-level compose plugin, dependency upgrades
**Status:** Accepted · **Date:** 2026-10-28

## Context
- Host port 80 is already used by another project's `ddev-router` container.
- No passwordless sudo, so `apt-get install docker-compose-plugin` was not possible.
- `npm audit` flagged react-router 6 (moderate: open redirect, GHSA-wrjc-x8rr-h8h6).
- ngrok v3 has no `--web-addr` CLI flag; the official image already serves the inspector on :4040.

## Decision
- nginx published on `127.0.0.1:${HTTP_PORT:-8080}`; ngrok inspector on `127.0.0.1:4040`. Binding to localhost
  keeps the app off the LAN — public access is only via the ngrok HTTPS tunnel.
- Docker Compose v5.6.1 installed per-user in `~/.docker/cli-plugins/` from the official GitHub release
  (sha256 verified).
- Frontend uses react-router-dom 7.x (same APIs as used in v6 for this app). `npm audit` → 0 vulnerabilities.
- ngrok command runs through `/bin/sh -c` so `--url` is added only when `NGROK_DOMAIN` is set.

## Consequences
- App URL locally is http://localhost:8080 (change `HTTP_PORT` to reuse 80 if ddev is stopped).
- Compose plugin updates are manual (re-download) rather than via apt.
