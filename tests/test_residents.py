def test_create_resident(client):
    resp = client.post(
        "/residents",
        json={"full_name": "Ravi Kumar", "email": "ravi@example.com", "phone": "123"},
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "ravi@example.com"


def test_duplicate_email_conflicts(client, resident_id):
    resp = client.post(
        "/residents", json={"full_name": "Someone Else", "email": "asha@example.com"}
    )
    assert resp.status_code == 409


def test_invalid_email_rejected(client):
    resp = client.post("/residents", json={"full_name": "X", "email": "not-an-email"})
    assert resp.status_code == 422


def test_update_and_delete_resident(client, resident_id):
    upd = client.patch(f"/residents/{resident_id}", json={"phone": "999"})
    assert upd.status_code == 200
    assert upd.json()["phone"] == "999"

    assert client.delete(f"/residents/{resident_id}").status_code == 204
    assert client.get(f"/residents/{resident_id}").status_code == 404
