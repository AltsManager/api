def test_create_list_update_delete_counterparty(admin_client):
    create_response = admin_client.post(
        "/api/v1/counterparties",
        json={"name": "Acme Fund Management", "counterparty_type": "fund_manager"},
    )
    assert create_response.status_code == 201
    counterparty_id = create_response.json()["id"]

    list_response = admin_client.get("/api/v1/counterparties")
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    update_response = admin_client.patch(
        f"/api/v1/counterparties/{counterparty_id}", json={"email": "contact@acme.example"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["email"] == "contact@acme.example"

    delete_response = admin_client.delete(f"/api/v1/counterparties/{counterparty_id}")
    assert delete_response.status_code == 204
    assert admin_client.get(f"/api/v1/counterparties/{counterparty_id}").status_code == 404
