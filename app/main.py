"""FastAPI application entrypoint for the co-living manager backend."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import __version__
from .config import settings
from .database import Base, engine
from .routers import leases, properties, residents, rooms


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Create tables on startup. For a real deployment this would be handled by
    # a migration tool (e.g. Alembic); create_all keeps the service runnable
    # out of the box.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Co-Living Manager API",
    version=__version__,
    summary="Manage co-living properties, rooms, residents, leases and rent.",
    lifespan=lifespan,
)

app.include_router(properties.router)
app.include_router(rooms.router)
app.include_router(residents.router)
app.include_router(leases.router)


@app.get("/ping", tags=["health"])
def ping():
    """Liveness probe."""
    return {"status": "ok"}


@app.get("/health", tags=["health"])
def health():
    """Readiness probe reporting service identity and version."""
    return {"status": "ok", "service": settings.app_name, "version": __version__}
