"""Shared pytest fixtures.

Each test runs against a fresh in-memory SQLite database so cases stay
isolated and never touch a real file. The app's ``get_db`` dependency is
overridden to use the test session factory.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # one shared in-memory connection
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def property_id(client):
    resp = client.post(
        "/properties",
        json={"name": "Maple House", "address": "1 Main St", "city": "Bengaluru"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.fixture()
def room_id(client, property_id):
    resp = client.post(
        f"/properties/{property_id}/rooms",
        json={"number": "101", "monthly_rent": 500.0, "capacity": 1},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.fixture()
def resident_id(client):
    resp = client.post(
        "/residents",
        json={"full_name": "Asha Rao", "email": "asha@example.com"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]
