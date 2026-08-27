import uuid


def _create_entity(client, name="Test Entity"):
    return client.post("/api/v1/entities", json={"name": name, "entity_type": "trust"}).json()["id"]


def _create_counterparty(client, name="Test Fund Manager"):
    response = client.post(
        "/api/v1/counterparties", json={"name": name, "counterparty_type": "fund_manager"}
    )
    return response.json()["id"]


def _create_investment(client, asset_type="safe_note", type_attributes=None):
    return client.post(
        "/api/v1/investments",
        json={
            "name": "Startup SAFE",
            "asset_type": asset_type,
            "acquisition_date": "2024-03-01",
            "initial_investment_amount": 50000,
            "type_attributes": type_attributes or {},
        },
    )


def test_create_investment_with_valid_type_attributes(admin_client):
    response = _create_investment(
        admin_client, "safe_note", {"valuation_cap": 5_000_000, "discount_rate": 0.2}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["type_attributes"] == {"valuation_cap": 5_000_000, "discount_rate": 0.2}


def test_create_investment_rejects_unknown_type_attribute_fields(admin_client):
    response = _create_investment(admin_client, "safe_note", {"not_a_real_field": 123})
    assert response.status_code == 422


def test_create_investment_rejects_fields_from_a_different_asset_type(admin_client):
    response = _create_investment(admin_client, "safe_note", {"ticker": "BTC"})
    assert response.status_code == 422


def test_update_investment_type_attributes_uses_existing_asset_type(admin_client):
    investment_id = _create_investment(admin_client, "crypto", {"ticker": "BTC"}).json()["id"]
    response = admin_client.patch(
        f"/api/v1/investments/{investment_id}",
        json={"type_attributes": {"ticker": "ETH", "quantity": 2.5}},
    )
    assert response.status_code == 200
    assert response.json()["type_attributes"] == {"ticker": "ETH", "quantity": 2.5}


def test_create_investment_ownership(admin_client):
    investment_id = _create_investment(admin_client).json()["id"]
    entity_id = _create_entity(admin_client)

    response = admin_client.post(
        f"/api/v1/investments/{investment_id}/ownerships",
        json={"entity_id": entity_id, "effective_date": "2024-03-01", "percentage": 100},
    )
    assert response.status_code == 201
    assert response.json()["entity_id"] == entity_id

    entity_ownerships = admin_client.get(f"/api/v1/entities/{entity_id}/ownerships")
    assert entity_ownerships.json()["total"] == 1


def test_create_ownership_with_unknown_entity_404s(admin_client):
    investment_id = _create_investment(admin_client).json()["id"]
    response = admin_client.post(
        f"/api/v1/investments/{investment_id}/ownerships",
        json={"entity_id": str(uuid.uuid4()), "effective_date": "2024-03-01", "percentage": 100},
    )
    assert response.status_code == 404


def test_create_investment_transaction(admin_client):
    investment_id = _create_investment(admin_client).json()["id"]
    entity_id = _create_entity(admin_client)

    response = admin_client.post(
        f"/api/v1/investments/{investment_id}/transactions",
        json={
            "entity_id": entity_id,
            "transaction_type": "contribution",
            "transaction_date": "2024-03-01",
            "amount": 50000,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["investment_id"] == investment_id
    assert body["entity_id"] == entity_id


def test_create_investment_counterparty_link(admin_client):
    investment_id = _create_investment(admin_client).json()["id"]
    counterparty_id = _create_counterparty(admin_client)

    response = admin_client.post(
        f"/api/v1/investments/{investment_id}/counterparties",
        json={"counterparty_id": counterparty_id, "role": "fund_manager"},
    )
    assert response.status_code == 201
    assert response.json()["counterparty_id"] == counterparty_id

    list_response = admin_client.get(f"/api/v1/investments/{investment_id}/counterparties")
    assert list_response.json()["total"] == 1
