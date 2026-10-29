def test_create_and_get_property(client):
    resp = client.post(
        "/properties",
        json={"name": "Oak Villa", "address": "5 Park Rd", "city": "Pune"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Oak Villa"
    assert "id" in data and "created_at" in data

    got = client.get(f"/properties/{data['id']}")
    assert got.status_code == 200
    assert got.json()["city"] == "Pune"


def test_list_properties(client, property_id):
    resp = client.get("/properties")
    assert resp.status_code == 200
    assert any(p["id"] == property_id for p in resp.json())


def test_update_property(client, property_id):
    resp = client.patch(f"/properties/{property_id}", json={"city": "Mumbai"})
    assert resp.status_code == 200
    assert resp.json()["city"] == "Mumbai"
    # Untouched fields are preserved.
    assert resp.json()["name"] == "Maple House"


def test_delete_property(client, property_id):
    assert client.delete(f"/properties/{property_id}").status_code == 204
    assert client.get(f"/properties/{property_id}").status_code == 404


def test_get_missing_property_404(client):
    assert client.get("/properties/9999").status_code == 404


def test_create_property_validation_error(client):
    resp = client.post("/properties", json={"name": "", "address": "a", "city": "c"})
    assert resp.status_code == 422
