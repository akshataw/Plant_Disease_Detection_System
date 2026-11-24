# 0001 — Record decisions as ADRs
**Status:** Accepted · **Date:** 2026-10-28

## Context
The project will be built over multiple phases and sessions. Context (why a library, why a schema
field) gets lost between sessions, especially when working with an AI assistant whose context resets.

## Decision
Keep lightweight ADRs in `decisions/`, an index in `decisions/README.md`, and task progress in
`tasks.md`. `CLAUDE.md` tells any assistant to read these first.

## Consequences
- Small overhead per decision; large savings when resuming work.
- Decisions are append-only; changes are new ADRs that supersede old ones.
