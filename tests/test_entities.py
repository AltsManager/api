import uuid


def test_create_and_get_entity(admin_client):
    create_response = admin_client.post(
        "/api/v1/entities", json={"name": "Smith Family Trust", "entity_type": "trust"}
    )
    assert create_response.status_code == 201
    entity_id = create_response.json()["id"]

    get_response = admin_client.get(f"/api/v1/entities/{entity_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Smith Family Trust"


def test_list_entities_paginated(admin_client):
    for i in range(3):
        admin_client.post(
            "/api/v1/entities", json={"name": f"Entity {i}", "entity_type": "llc"}
        )
    response = admin_client.get("/api/v1/entities", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["limit"] == 2


def test_update_entity(admin_client):
    entity_id = admin_client.post(
        "/api/v1/entities", json={"name": "Old Name", "entity_type": "llc"}
    ).json()["id"]
    response = admin_client.patch(f"/api/v1/entities/{entity_id}", json={"name": "New Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    assert response.json()["entity_type"] == "llc"


def test_delete_entity_requires_admin(staff_client, admin_client):
    entity_id = admin_client.post(
        "/api/v1/entities", json={"name": "To Delete", "entity_type": "llc"}
    ).json()["id"]

    forbidden = staff_client.delete(f"/api/v1/entities/{entity_id}")
    assert forbidden.status_code == 403

    allowed = admin_client.delete(f"/api/v1/entities/{entity_id}")
    assert allowed.status_code == 204
    assert admin_client.get(f"/api/v1/entities/{entity_id}").status_code == 404


def test_viewer_cannot_create_entity(viewer_client):
    response = viewer_client.post(
        "/api/v1/entities", json={"name": "Nope", "entity_type": "llc"}
    )
    assert response.status_code == 403


def test_get_nonexistent_entity_404(admin_client):
    response = admin_client.get(f"/api/v1/entities/{uuid.uuid4()}")
    assert response.status_code == 404


def test_list_entity_ownerships_empty(admin_client):
    entity_id = admin_client.post(
        "/api/v1/entities", json={"name": "No Ownerships", "entity_type": "llc"}
    ).json()["id"]
    response = admin_client.get(f"/api/v1/entities/{entity_id}/ownerships")
    assert response.status_code == 200
    assert response.json()["items"] == []
