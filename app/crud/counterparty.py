from sqlalchemy.orm import Session

from app.crud import base
from app.models.counterparty import Counterparty


def create_counterparty(db: Session, **fields):
    return base.create(db, Counterparty, **fields)


def get_counterparty(db: Session, counterparty_id) -> Counterparty | None:
    return db.get(Counterparty, counterparty_id)


def list_counterparties(db: Session, limit: int, offset: int):
    return base.list_paginated(db, Counterparty, limit, offset)


def update_counterparty(db: Session, counterparty: Counterparty, **fields):
    return base.update(db, counterparty, **fields)


def delete_counterparty(db: Session, counterparty: Counterparty) -> None:
    base.delete(db, counterparty)
