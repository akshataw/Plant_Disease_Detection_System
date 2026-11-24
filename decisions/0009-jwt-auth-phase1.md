# 0009 — JWT (access + refresh) + bcrypt, in Phase 1
**Status:** Accepted · **Date:** 2026-10-28

## Context
Synopsis puts user authentication in scope (JWT, bcrypt). User chose to build it in Phase 1 so
every prediction is tied to a user from day one.

## Decision
- Flask-JWT-Extended; short-lived access token (30 min) + refresh token (7 days), sent in the
  `Authorization: Bearer` header.
- Frontend stores tokens in `localStorage` and refreshes transparently on 401.
- Passwords hashed with Flask-Bcrypt; email unique and lower-cased; minimum password length 8.
- All predict/history/image endpoints require a valid access token and enforce ownership.

## Consequences
- Simple and stateless. `localStorage` is XSS-exposed — mitigated by strict CSP headers in nginx and no
  `dangerouslySetInnerHTML`. Phase 2 may move to httpOnly cookies + CSRF and add token revocation.
