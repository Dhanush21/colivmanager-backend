# colivmanager-backend

Backend API for a **co-living manager** — manage co-living properties, their
rooms, residents, leases (room assignments), and rent payments.

Built with [FastAPI](https://fastapi.tiangolo.com/) and
[SQLAlchemy](https://www.sqlalchemy.org/), packaged as a container and
deployed to Google Cloud Run (see [`docs/adr`](docs/adr) for the architecture
decisions behind these choices).

## Domain

```
Property 1──* Room 1──* Lease *──1 Resident
                          Lease 1──* Payment
```

- **Property** — a co-living building (name, address, city).
- **Room** — belongs to a property; has a number, monthly rent, and a
  `capacity` (how many residents may occupy it at once).
- **Resident** — a person (unique email).
- **Lease** — places a resident in a room for a date range. A room cannot hold
  more overlapping **active** leases than its capacity.
- **Payment** — rent collected against a lease for a given month
  (`period`, `YYYY-MM`); one payment per period per lease.

## API

Interactive docs are served at `/docs` (Swagger UI) and `/redoc` when running.

| Method | Path | Description |
| ------ | ---- | ----------- |
| GET | `/ping`, `/health` | Liveness / readiness probes |
| POST / GET | `/properties` | Create / list properties |
| GET / PATCH / DELETE | `/properties/{id}` | Fetch / update / delete a property |
| POST / GET | `/properties/{id}/rooms` | Create / list rooms in a property |
| GET / PATCH / DELETE | `/rooms/{id}` | Fetch / update / delete a room |
| POST / GET | `/residents` | Create / list residents |
| GET / PATCH / DELETE | `/residents/{id}` | Fetch / update / delete a resident |
| POST / GET | `/leases` | Create / list leases (filter by `resident_id`, `room_id`, `status_filter`) |
| GET | `/leases/{id}` | Fetch a lease |
| POST | `/leases/{id}/end` | End a lease (optional `end_date` query param) |
| POST / GET | `/leases/{id}/payments` | Record / list rent payments |

## Configuration

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `DATABASE_URL` | `sqlite:///./colivmanager.db` | SQLAlchemy database URL. Set a managed Postgres URL in production. |

Tables are created automatically on startup. For production schema changes,
adopt a migration tool such as Alembic.

## Local development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

# Run the API (http://localhost:8080)
uvicorn app.main:app --reload --port 8080

# Run the tests
pytest
```

## Docker

```bash
docker build -t colivmanager-backend .
docker run -p 8080:8080 colivmanager-backend
```

## Notes / next steps

- **Authentication** is not yet implemented; the Cloud Run service currently
  runs with `--allow-unauthenticated`. Add auth before storing real data.
- **Persistence**: the default SQLite file is ephemeral on Cloud Run. Point
  `DATABASE_URL` at a managed database for durable storage.
