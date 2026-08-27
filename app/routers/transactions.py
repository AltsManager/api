import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DbSession, Limit, Offset, require_role
from app.core.exceptions import NotFoundError
from app.crud import transaction as transaction_crud
from app.models.enums import TransactionType, UserRole
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.common import Page
from app.schemas.transaction import TransactionRead, TransactionUpdate

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])

WriteAccess = Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.STAFF))]


@router.get("", response_model=Page[TransactionRead])
def list_transactions(
    db: DbSession,
    _: CurrentUser,
    limit: Limit = 50,
    offset: Offset = 0,
    entity_id: uuid.UUID | None = None,
    investment_id: uuid.UUID | None = None,
    transaction_type: TransactionType | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
):
    filters = []
    if entity_id is not None:
        filters.append(Transaction.entity_id == entity_id)
    if investment_id is not None:
        filters.append(Transaction.investment_id == investment_id)
    if transaction_type is not None:
        filters.append(Transaction.transaction_type == transaction_type)
    if date_from is not None:
        filters.append(Transaction.transaction_date >= date_from)
    if date_to is not None:
        filters.append(Transaction.transaction_date <= date_to)

    items, total = transaction_crud.list_transactions(db, limit, offset, *filters)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: uuid.UUID, db: DbSession, _: CurrentUser):
    transaction = transaction_crud.get_transaction(db, transaction_id)
    if transaction is None:
        raise NotFoundError("Transaction", transaction_id)
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: uuid.UUID, data: TransactionUpdate, db: DbSession, _: WriteAccess
):
    transaction = transaction_crud.get_transaction(db, transaction_id)
    if transaction is None:
        raise NotFoundError("Transaction", transaction_id)
    fields = data.model_dump(exclude_unset=True)
    return transaction_crud.update_transaction(db, transaction, **fields)
