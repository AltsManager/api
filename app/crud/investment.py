from sqlalchemy.orm import Session

from app.crud import base
from app.models.document import Document
from app.models.investment import Investment
from app.models.investment_counterparty import InvestmentCounterparty
from app.models.ownership import Ownership
from app.models.transaction import Transaction


def create_investment(db: Session, **fields):
    return base.create(db, Investment, **fields)


def get_investment(db: Session, investment_id) -> Investment | None:
    return db.get(Investment, investment_id)


def list_investments(db: Session, limit: int, offset: int):
    return base.list_paginated(db, Investment, limit, offset)


def update_investment(db: Session, investment: Investment, **fields):
    return base.update(db, investment, **fields)


def delete_investment(db: Session, investment: Investment) -> None:
    base.delete(db, investment)


def list_investment_ownerships(db: Session, investment_id, limit: int, offset: int):
    return base.list_paginated(
        db, Ownership, limit, offset, Ownership.investment_id == investment_id
    )


def create_ownership(db: Session, **fields):
    return base.create(db, Ownership, **fields)


def list_investment_counterparties(db: Session, investment_id, limit: int, offset: int):
    return base.list_paginated(
        db,
        InvestmentCounterparty,
        limit,
        offset,
        InvestmentCounterparty.investment_id == investment_id,
    )


def create_investment_counterparty(db: Session, **fields):
    return base.create(db, InvestmentCounterparty, **fields)


def list_investment_transactions(db: Session, investment_id, limit: int, offset: int):
    return base.list_paginated(
        db, Transaction, limit, offset, Transaction.investment_id == investment_id
    )


def list_investment_documents(db: Session, investment_id, limit: int, offset: int):
    return base.list_paginated(
        db, Document, limit, offset, Document.investment_id == investment_id
    )
