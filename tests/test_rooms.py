def test_create_room(client, property_id):
    resp = client.post(
        f"/properties/{property_id}/rooms",
        json={"number": "201", "monthly_rent": 650.0, "capacity": 2},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["number"] == "201"
    assert data["capacity"] == 2
    assert data["property_id"] == property_id


def test_duplicate_room_number_conflicts(client, property_id):
    body = {"number": "301", "monthly_rent": 400.0}
    assert client.post(f"/properties/{property_id}/rooms", json=body).status_code == 201
    assert client.post(f"/properties/{property_id}/rooms", json=body).status_code == 409


def test_create_room_on_missing_property_404(client):
    resp = client.post(
        "/properties/9999/rooms", json={"number": "1", "monthly_rent": 100.0}
    )
    assert resp.status_code == 404


def test_list_rooms(client, property_id, room_id):
    resp = client.get(f"/properties/{property_id}/rooms")
    assert resp.status_code == 200
    assert [r["id"] for r in resp.json()] == [room_id]


def test_get_update_delete_room(client, room_id):
    assert client.get(f"/rooms/{room_id}").status_code == 200

    upd = client.patch(f"/rooms/{room_id}", json={"monthly_rent": 555.5})
    assert upd.status_code == 200
    assert upd.json()["monthly_rent"] == 555.5

    assert client.delete(f"/rooms/{room_id}").status_code == 204
    assert client.get(f"/rooms/{room_id}").status_code == 404


def test_negative_rent_rejected(client, property_id):
    resp = client.post(
        f"/properties/{property_id}/rooms",
        json={"number": "9", "monthly_rent": -10},
    )
    assert resp.status_code == 422
