# 0002. Use FastAPI deployed to Google Cloud Run

- **Status:** Accepted
- **Date:** 2026-10-29

## Context

`colivmanager-backend` provides the HTTP API for the co-living manager product.
We need a runtime that:

- exposes a JSON HTTP API with low ceremony,
- has strong Python ecosystem support and typing,
- packages as a stateless container, and
- deploys with minimal operational overhead for a small team.

The service exposes a REST API over the co-living domain (properties, rooms,
residents, leases, and rent payments), backed by a relational database through
SQLAlchemy.

## Decision

We will build the API with **FastAPI** (served by **Uvicorn**) and deploy it as
a container to **Google Cloud Run**.

- The application is packaged with a `python:3.11-slim` **Docker** image
  (`Dockerfile`) that installs `requirements.txt` and runs
  `uvicorn app.main:app` on port `8080`.
- Persistence is through **SQLAlchemy**; the database is selected at runtime via
  the `DATABASE_URL` environment variable (SQLite by default for local use, a
  managed database such as Postgres in production).
- Deployment is automated via **GitHub Actions**: on push to `main`, the image
  is built, pushed to **Google Artifact Registry**, and released to Cloud Run in
  region `asia-south1` under project `coliv-backend`.
- The Cloud Run service currently runs with `--allow-unauthenticated`.

## Consequences

- **Positive:** FastAPI gives typed request/response models, automatic OpenAPI
  docs, and async support. Cloud Run scales to zero, bills per request, and
  removes server management — a good fit for an early-stage, low-traffic
  backend. Container packaging keeps local and production environments aligned.
- **Negative / follow-up:**
  - `--allow-unauthenticated` exposes the service publicly; authentication and
    authorization must be handled in the application layer before it holds
    sensitive data.
  - The default SQLite database is ephemeral on Cloud Run; a managed database
    must back any real deployment, and schema changes should move to a
    migration tool (e.g. Alembic) rather than `create_all` on startup.
  - Cold starts are possible under scale-to-zero; revisit min-instances if
    latency becomes a concern.
  - Two workflows currently deploy to Cloud Run on push to `main`
    (`.github/workflows/ci-cd.yml` and
    `.github/workflows/cloud-run-deploy.yml`). They overlap and should be
    consolidated into a single deployment pipeline to avoid duplicate,
    racing deploys.

## Alternatives considered

- **Flask / Django** – Flask lacks first-class async and typed models; Django is
  heavier than needed for a small JSON API.
- **A traditional VM or GKE (Kubernetes)** – more control, but far more
  operational overhead than a small team needs at this stage.
- **A serverless function platform (Cloud Functions)** – viable, but Cloud Run's
  container model gives more portability and a smoother path as the app grows
  beyond a handful of endpoints.
