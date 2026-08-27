def _setup_transaction(client, transaction_type="contribution", amount=50000):
    entity_id = client.post(
        "/api/v1/entities", json={"name": "Entity", "entity_type": "trust"}
    ).json()["id"]
    investment_id = client.post(
        "/api/v1/investments",
        json={
            "name": "Investment",
            "asset_type": "safe_note",
            "acquisition_date": "2024-03-01",
            "initial_investment_amount": amount,
        },
    ).json()["id"]
    transaction = client.post(
        f"/api/v1/investments/{investment_id}/transactions",
        json={
            "entity_id": entity_id,
            "transaction_type": transaction_type,
            "transaction_date": "2024-03-01",
            "amount": amount,
        },
    ).json()
    return entity_id, investment_id, transaction


def test_list_transactions_filters_by_investment(admin_client):
    _entity_id, investment_id, transaction = _setup_transaction(admin_client)
    _entity_id2, _investment_id2, _transaction2 = _setup_transaction(admin_client)

    response = admin_client.get("/api/v1/transactions", params={"investment_id": investment_id})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == transaction["id"]


def test_get_and_update_transaction(admin_client):
    _entity_id, _investment_id, transaction = _setup_transaction(admin_client)

    get_response = admin_client.get(f"/api/v1/transactions/{transaction['id']}")
    assert get_response.status_code == 200

    update_response = admin_client.patch(
        f"/api/v1/transactions/{transaction['id']}", json={"amount": 60000}
    )
    assert update_response.status_code == 200
    assert update_response.json()["amount"] == 60000


def test_list_transactions_filters_by_type(admin_client):
    _setup_transaction(admin_client, transaction_type="contribution")
    _setup_transaction(admin_client, transaction_type="distribution")

    response = admin_client.get(
        "/api/v1/transactions", params={"transaction_type": "distribution"}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["transaction_type"] == "distribution"
