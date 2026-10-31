"""Runtime configuration, sourced from environment variables.

Kept dependency-free (plain dataclass) so the service has no reliance on
pydantic-settings. Cloud Run injects configuration through environment
variables, which is all this needs.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "colivmanager-backend"
    # Defaults to a local SQLite file; override with a managed database URL
    # (e.g. Postgres) in production via the DATABASE_URL environment variable.
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./colivmanager.db")


settings = Settings()
