from typing import Any

from sqlalchemy.orm import Session

from app.crud import base
from app.models.transaction import Transaction


def create_transaction(db: Session, **fields):
    return base.create(db, Transaction, **fields)


def get_transaction(db: Session, transaction_id) -> Transaction | None:
    return db.get(Transaction, transaction_id)


def list_transactions(db: Session, limit: int, offset: int, *filters: Any):
    return base.list_paginated(db, Transaction, limit, offset, *filters)


def update_transaction(db: Session, transaction: Transaction, **fields):
    return base.update(db, transaction, **fields)
