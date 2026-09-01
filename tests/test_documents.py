import io
import uuid


def _create_entity(client, name="Doc Test Entity"):
    return client.post("/api/v1/entities", json={"name": name, "entity_type": "trust"}).json()["id"]


def _create_investment(client, name="Doc Test Investment"):
    return client.post(
        "/api/v1/investments",
        json={
            "name": name,
            "asset_type": "safe_note",
            "acquisition_date": "2024-03-01",
            "initial_investment_amount": 50000,
        },
    ).json()["id"]


def _upload(
    client,
    url,
    *,
    doc_type="k1",
    tax_year=None,
    notes=None,
    filename="k1.pdf",
    content=b"%PDF-1.4 fake k1",
    **extra_data,
):
    data = {"doc_type": doc_type}
    if tax_year is not None:
        data["tax_year"] = str(tax_year)
    if notes is not None:
        data["notes"] = notes
    data.update(extra_data)
    files = {"file": (filename, io.BytesIO(content), "application/pdf")}
    return client.post(url, data=data, files=files)


def test_upload_document_for_entity(admin_client):
    entity_id = _create_entity(admin_client)
    response = _upload(
        admin_client, "/api/v1/documents", doc_type="k1", tax_year=2024, entity_id=entity_id
    )
    assert response.status_code == 201
    body = response.json()
    assert body["filename"] == "k1.pdf"
    assert body["doc_type"] == "k1"
    assert body["tax_year"] == 2024
    assert body["status"] == "pending_review"
    assert body["entity_id"] == entity_id
    assert "storage_key" not in body


def test_upload_document_requires_at_least_one_link(admin_client):
    response = _upload(admin_client, "/api/v1/documents", doc_type="other")
    assert response.status_code == 400


def test_upload_document_with_unknown_entity_404s(admin_client):
    response = _upload(
        admin_client, "/api/v1/documents", doc_type="other", entity_id=str(uuid.uuid4())
    )
    assert response.status_code == 404


def test_download_document_returns_uploaded_bytes(admin_client):
    entity_id = _create_entity(admin_client)
    content = b"%PDF-1.4 the actual k1 content"
    document_id = _upload(
        admin_client, "/api/v1/documents", entity_id=entity_id, content=content
    ).json()["id"]

    response = admin_client.get(f"/api/v1/documents/{document_id}/download")
    assert response.status_code == 200
    assert response.content == content
    assert "k1.pdf" in response.headers["content-disposition"]


def test_list_documents_filters_by_doc_type_and_entity(admin_client):
    entity_id = _create_entity(admin_client)
    _upload(admin_client, "/api/v1/documents", doc_type="k1", entity_id=entity_id)
    _upload(admin_client, "/api/v1/documents", doc_type="statement", entity_id=entity_id)

    response = admin_client.get(
        "/api/v1/documents", params={"entity_id": entity_id, "doc_type": "k1"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["doc_type"] == "k1"


def test_update_document_status_workflow(admin_client):
    entity_id = _create_entity(admin_client)
    document_id = _upload(admin_client, "/api/v1/documents", entity_id=entity_id).json()["id"]

    response = admin_client.patch(f"/api/v1/documents/{document_id}", json={"status": "approved"})
    assert response.status_code == 200
    assert response.json()["status"] == "approved"


def test_viewer_cannot_upload_document(viewer_client):
    response = _upload(
        viewer_client, "/api/v1/documents", entity_id=str(uuid.uuid4()), doc_type="other"
    )
    assert response.status_code == 403


def test_upload_document_nested_under_investment(admin_client):
    investment_id = _create_investment(admin_client)
    response = _upload(
        admin_client, f"/api/v1/investments/{investment_id}/documents", doc_type="statement"
    )
    assert response.status_code == 201
    assert response.json()["investment_id"] == investment_id

    list_response = admin_client.get(f"/api/v1/investments/{investment_id}/documents")
    assert list_response.json()["total"] == 1


def test_upload_document_nested_under_entity(admin_client):
    entity_id = _create_entity(admin_client)
    response = _upload(
        admin_client, f"/api/v1/entities/{entity_id}/documents", doc_type="tax_form"
    )
    assert response.status_code == 201
    assert response.json()["entity_id"] == entity_id

    list_response = admin_client.get(f"/api/v1/entities/{entity_id}/documents")
    assert list_response.json()["total"] == 1
