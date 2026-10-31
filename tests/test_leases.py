import pytest


@pytest.fixture()
def second_resident(client):
    resp = client.post(
        "/residents", json={"full_name": "Bo Li", "email": "bo@example.com"}
    )
    return resp.json()["id"]


def test_create_lease_defaults_rent_to_room(client, room_id, resident_id):
    resp = client.post(
        "/leases",
        json={
            "room_id": room_id,
            "resident_id": resident_id,
            "start_date": "2026-01-01",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["monthly_rent"] == 500.0  # inherited from the room
    assert data["status"] == "active"


def test_create_lease_explicit_rent(client, room_id, resident_id):
    resp = client.post(
        "/leases",
        json={
            "room_id": room_id,
            "resident_id": resident_id,
            "start_date": "2026-01-01",
            "monthly_rent": 450.0,
        },
    )
    assert resp.json()["monthly_rent"] == 450.0


def test_lease_missing_room_or_resident_404(client, room_id, resident_id):
    assert (
        client.post(
            "/leases",
            json={"room_id": 9999, "resident_id": resident_id, "start_date": "2026-01-01"},
        ).status_code
        == 404
    )
    assert (
        client.post(
            "/leases",
            json={"room_id": room_id, "resident_id": 9999, "start_date": "2026-01-01"},
        ).status_code
        == 404
    )


def test_end_date_before_start_rejected(client, room_id, resident_id):
    resp = client.post(
        "/leases",
        json={
            "room_id": room_id,
            "resident_id": resident_id,
            "start_date": "2026-06-01",
            "end_date": "2026-05-01",
        },
    )
    assert resp.status_code == 422


def test_capacity_one_blocks_overlapping_lease(
    client, room_id, resident_id, second_resident
):
    first = client.post(
        "/leases",
        json={"room_id": room_id, "resident_id": resident_id, "start_date": "2026-01-01"},
    )
    assert first.status_code == 201

    # Room capacity is 1, so an overlapping lease must be rejected.
    clash = client.post(
        "/leases",
        json={
            "room_id": room_id,
            "resident_id": second_resident,
            "start_date": "2026-02-01",
        },
    )
    assert clash.status_code == 409


def test_non_overlapping_lease_allowed_after_end(
    client, room_id, resident_id, second_resident
):
    first = client.post(
        "/leases",
        json={
            "room_id": room_id,
            "resident_id": resident_id,
            "start_date": "2026-01-01",
            "end_date": "2026-03-31",
        },
    ).json()

    # Ending leaves the room free; a later, non-overlapping lease is fine.
    client.post(f"/leases/{first['id']}/end", params={"end_date": "2026-03-31"})
    later = client.post(
        "/leases",
        json={
            "room_id": room_id,
            "resident_id": second_resident,
            "start_date": "2026-04-01",
        },
    )
    assert later.status_code == 201


def test_capacity_two_allows_two_concurrent(client, property_id, resident_id, second_resident):
    shared = client.post(
        f"/properties/{property_id}/rooms",
        json={"number": "shared", "monthly_rent": 300.0, "capacity": 2},
    ).json()["id"]

    a = client.post(
        "/leases",
        json={"room_id": shared, "resident_id": resident_id, "start_date": "2026-01-01"},
    )
    b = client.post(
        "/leases",
        json={"room_id": shared, "resident_id": second_resident, "start_date": "2026-01-01"},
    )
    assert a.status_code == 201
    assert b.status_code == 201


def test_end_lease_and_double_end(client, room_id, resident_id):
    lease = client.post(
        "/leases",
        json={"room_id": room_id, "resident_id": resident_id, "start_date": "2026-01-01"},
    ).json()

    ended = client.post(f"/leases/{lease['id']}/end", params={"end_date": "2026-06-30"})
    assert ended.status_code == 200
    assert ended.json()["status"] == "ended"
    assert ended.json()["end_date"] == "2026-06-30"

    # Ending an already-ended lease conflicts.
    assert client.post(f"/leases/{lease['id']}/end").status_code == 409


def test_list_leases_filtered(client, room_id, resident_id):
    client.post(
        "/leases",
        json={"room_id": room_id, "resident_id": resident_id, "start_date": "2026-01-01"},
    )
    resp = client.get("/leases", params={"resident_id": resident_id})
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert client.get("/leases", params={"resident_id": 9999}).json() == []
