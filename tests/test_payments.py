import pytest


@pytest.fixture()
def lease_id(client, room_id, resident_id):
    resp = client.post(
        "/leases",
        json={"room_id": room_id, "resident_id": resident_id, "start_date": "2026-01-01"},
    )
    return resp.json()["id"]


def test_record_and_list_payment(client, lease_id):
    resp = client.post(
        f"/leases/{lease_id}/payments",
        json={"amount": 500.0, "period": "2026-01", "method": "upi"},
    )
    assert resp.status_code == 201
    assert resp.json()["period"] == "2026-01"
    assert resp.json()["paid_on"]  # defaulted to today

    listing = client.get(f"/leases/{lease_id}/payments")
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_duplicate_period_conflicts(client, lease_id):
    body = {"amount": 500.0, "period": "2026-02"}
    assert client.post(f"/leases/{lease_id}/payments", json=body).status_code == 201
    assert client.post(f"/leases/{lease_id}/payments", json=body).status_code == 409


def test_payment_on_missing_lease_404(client):
    resp = client.post(
        "/leases/9999/payments", json={"amount": 100.0, "period": "2026-01"}
    )
    assert resp.status_code == 404


def test_bad_period_format_rejected(client, lease_id):
    resp = client.post(
        f"/leases/{lease_id}/payments", json={"amount": 100.0, "period": "Jan-2026"}
    )
    assert resp.status_code == 422


def test_payments_ordered_by_period(client, lease_id):
    for period in ("2026-03", "2026-01", "2026-02"):
        client.post(
            f"/leases/{lease_id}/payments", json={"amount": 500.0, "period": period}
        )
    periods = [p["period"] for p in client.get(f"/leases/{lease_id}/payments").json()]
    assert periods == ["2026-01", "2026-02", "2026-03"]
