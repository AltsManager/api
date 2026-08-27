import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.deps import CurrentUser, DbSession, Limit, Offset, require_role
from app.core.exceptions import NotFoundError
from app.crud import counterparty as counterparty_crud
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import Page
from app.schemas.counterparty import CounterpartyCreate, CounterpartyRead, CounterpartyUpdate

router = APIRouter(prefix="/api/v1/counterparties", tags=["counterparties"])

WriteAccess = Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.STAFF))]
DeleteAccess = Annotated[User, Depends(require_role(UserRole.ADMIN))]


def _get_or_404(db: DbSession, counterparty_id: uuid.UUID):
    counterparty = counterparty_crud.get_counterparty(db, counterparty_id)
    if counterparty is None:
        raise NotFoundError("Counterparty", counterparty_id)
    return counterparty


@router.get("", response_model=Page[CounterpartyRead])
def list_counterparties(db: DbSession, _: CurrentUser, limit: Limit = 50, offset: Offset = 0):
    items, total = counterparty_crud.list_counterparties(db, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=CounterpartyRead, status_code=status.HTTP_201_CREATED)
def create_counterparty(data: CounterpartyCreate, db: DbSession, _: WriteAccess):
    return counterparty_crud.create_counterparty(db, **data.model_dump())


@router.get("/{counterparty_id}", response_model=CounterpartyRead)
def get_counterparty(counterparty_id: uuid.UUID, db: DbSession, _: CurrentUser):
    return _get_or_404(db, counterparty_id)


@router.patch("/{counterparty_id}", response_model=CounterpartyRead)
def update_counterparty(
    counterparty_id: uuid.UUID, data: CounterpartyUpdate, db: DbSession, _: WriteAccess
):
    counterparty = _get_or_404(db, counterparty_id)
    fields = data.model_dump(exclude_unset=True)
    return counterparty_crud.update_counterparty(db, counterparty, **fields)


@router.delete("/{counterparty_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_counterparty(counterparty_id: uuid.UUID, db: DbSession, _: DeleteAccess):
    counterparty = _get_or_404(db, counterparty_id)
    counterparty_crud.delete_counterparty(db, counterparty)
