from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import (
    Counterparty,
    Document,
    Entity,
    Investment,
    InvestmentCounterparty,
    Ownership,
    Transaction,
    User,
)
from app.models.enums import (
    AssetType,
    CounterpartyRole,
    CounterpartyType,
    DocumentType,
    EntityType,
    TransactionType,
    UserRole,
)


def test_core_ledger_round_trip(db_session):
    user = User(
        email="admin@example.com", hashed_password="x", full_name="Admin", role=UserRole.ADMIN
    )
    entity = Entity(name="Smith Family Trust", entity_type=EntityType.TRUST)
    counterparty = Counterparty(
        name="Acme Fund Management", counterparty_type=CounterpartyType.FUND_MANAGER
    )
    investment = Investment(
        name="Acme Ventures Fund III",
        asset_type=AssetType.VC_FUND_LP,
        acquisition_date=date(2024, 1, 15),
        initial_investment_amount=250_000,
        type_attributes={"commitment": 500_000},
    )
    db_session.add_all([user, entity, counterparty, investment])
    db_session.flush()

    investment_counterparty = InvestmentCounterparty(
        investment_id=investment.id,
        counterparty_id=counterparty.id,
        role=CounterpartyRole.FUND_MANAGER,
    )
    ownership = Ownership(
        entity_id=entity.id,
        investment_id=investment.id,
        effective_date=date(2024, 1, 15),
        percentage=100,
    )
    transaction = Transaction(
        investment_id=investment.id,
        entity_id=entity.id,
        transaction_type=TransactionType.CONTRIBUTION,
        transaction_date=date(2024, 1, 15),
        amount=250_000,
    )
    db_session.add_all([investment_counterparty, ownership, transaction])
    db_session.flush()

    document = Document(
        filename="k1_2024.pdf",
        storage_key="documents/k1_2024.pdf",
        content_type="application/pdf",
        size_bytes=1024,
        doc_type=DocumentType.K1,
        tax_year=2024,
        entity_id=entity.id,
        investment_id=investment.id,
        uploaded_by=user.id,
    )
    db_session.add(document)
    db_session.flush()

    db_session.refresh(investment)
    assert investment.id is not None
    assert ownership.investment_id == investment.id
    assert transaction.entity_id == entity.id
    assert investment_counterparty.role == CounterpartyRole.FUND_MANAGER
    assert document.entity_id == entity.id and document.investment_id == investment.id


def test_investment_type_attributes_jsonb_round_trip(db_session):
    safe = Investment(
        name="Startup SAFE",
        asset_type=AssetType.SAFE_NOTE,
        acquisition_date=date(2024, 3, 1),
        initial_investment_amount=50_000,
        type_attributes={"valuation_cap": 5_000_000, "discount": 0.2},
    )
    crypto = Investment(
        name="BTC holding",
        asset_type=AssetType.CRYPTO,
        acquisition_date=date(2024, 3, 1),
        initial_investment_amount=50_000,
        type_attributes={"ticker": "BTC", "quantity": "1.5", "wallet": "cold-storage-1"},
    )
    db_session.add_all([safe, crypto])
    db_session.flush()
    db_session.expire_all()

    reloaded_safe = db_session.get(Investment, safe.id)
    reloaded_crypto = db_session.get(Investment, crypto.id)

    assert reloaded_safe.type_attributes == {"valuation_cap": 5_000_000, "discount": 0.2}
    assert reloaded_crypto.type_attributes == {
        "ticker": "BTC",
        "quantity": "1.5",
        "wallet": "cold-storage-1",
    }


def test_document_requires_a_linked_record(db_session):
    user = User(
        email="staff@example.com", hashed_password="x", full_name="Staff", role=UserRole.STAFF
    )
    db_session.add(user)
    db_session.flush()

    orphan_document = Document(
        filename="orphan.pdf",
        storage_key="documents/orphan.pdf",
        content_type="application/pdf",
        size_bytes=1,
        doc_type=DocumentType.OTHER,
        uploaded_by=user.id,
    )
    db_session.add(orphan_document)
    with pytest.raises(IntegrityError):
        db_session.flush()
