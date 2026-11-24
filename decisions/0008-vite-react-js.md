# 0008 — Vite + React + JavaScript, plain CSS
**Status:** Accepted · **Date:** 2026-10-28

## Context
Synopsis: React, HTML, CSS, JavaScript; simple, user-friendly, responsive UI.

## Decision
- Vite + React 18 + plain JavaScript (no TypeScript), React Router for pages.
- Plain CSS (one global stylesheet with CSS variables + responsive media queries); no UI framework.
- API client in `src/api/client.js` using `fetch`, base path `/api/v1` (same origin via nginx → no CORS in prod).
- Dev: `npm run dev` with Vite proxy `/api` → `localhost:5000`.

## Consequences
- Matches synopsis exactly, minimal dependencies.
- Can adopt TypeScript or a component library in a later phase if the UI grows.
