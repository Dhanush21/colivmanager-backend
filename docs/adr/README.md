# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the
`colivmanager-backend` service.

An ADR captures a single significant architectural decision, the context that
led to it, and its consequences. Recording them keeps the reasoning behind the
system available to future contributors.

## Index

| ADR | Title | Status |
| --- | ----- | ------ |
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-use-fastapi-on-cloud-run.md) | Use FastAPI deployed to Google Cloud Run | Accepted |

## Conventions

- Files are named `NNNN-title-in-kebab-case.md`, numbered sequentially.
- Copy [`template.md`](template.md) to start a new record.
- Once accepted, an ADR is immutable. To change a decision, write a new ADR
  that supersedes the old one and update the status of both.

## Statuses

- **Proposed** – under discussion.
- **Accepted** – the decision is in effect.
- **Superseded** – replaced by a later ADR (link to it).
- **Deprecated** – no longer relevant.
