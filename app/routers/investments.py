import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.deps import CurrentUser, DbSession, Limit, Offset, require_role
from app.core.exceptions import NotFoundError
from app.crud import counterparty as counterparty_crud
from app.crud import entity as entity_crud
from app.crud import investment as investment_crud
from app.crud import transaction as transaction_crud
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import Page
from app.schemas.document import DocTypeForm, DocumentRead, NotesForm, TaxYearForm, UploadedFile
from app.schemas.investment import InvestmentCreate, InvestmentRead, InvestmentUpdate
from app.schemas.investment_attributes import validate_type_attributes
from app.schemas.investment_counterparty import (
    InvestmentCounterpartyCreate,
    InvestmentCounterpartyRead,
)
from app.schemas.ownership import OwnershipCreate, OwnershipRead
from app.schemas.transaction import TransactionCreate, TransactionRead
from app.services.documents import save_uploaded_document

router = APIRouter(prefix="/api/v1/investments", tags=["investments"])

WriteAccess = Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.STAFF))]
DeleteAccess = Annotated[User, Depends(require_role(UserRole.ADMIN))]


def _get_or_404(db: DbSession, investment_id: uuid.UUID):
    investment = investment_crud.get_investment(db, investment_id)
    if investment is None:
        raise NotFoundError("Investment", investment_id)
    return investment


def _require_entity(db: DbSession, entity_id: uuid.UUID) -> None:
    if entity_crud.get_entity(db, entity_id) is None:
        raise NotFoundError("Entity", entity_id)


def _require_counterparty(db: DbSession, counterparty_id: uuid.UUID) -> None:
    if counterparty_crud.get_counterparty(db, counterparty_id) is None:
        raise NotFoundError("Counterparty", counterparty_id)


@router.get("", response_model=Page[InvestmentRead])
def list_investments(db: DbSession, _: CurrentUser, limit: Limit = 50, offset: Offset = 0):
    items, total = investment_crud.list_investments(db, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=InvestmentRead, status_code=status.HTTP_201_CREATED)
def create_investment(data: InvestmentCreate, db: DbSession, _: WriteAccess):
    return investment_crud.create_investment(db, **data.model_dump())


@router.get("/{investment_id}", response_model=InvestmentRead)
def get_investment(investment_id: uuid.UUID, db: DbSession, _: CurrentUser):
    return _get_or_404(db, investment_id)


@router.patch("/{investment_id}", response_model=InvestmentRead)
def update_investment(
    investment_id: uuid.UUID, data: InvestmentUpdate, db: DbSession, _: WriteAccess
):
    investment = _get_or_404(db, investment_id)
    fields = data.model_dump(exclude_unset=True)
    if "type_attributes" in fields:
        effective_asset_type = fields.get("asset_type", investment.asset_type)
        fields["type_attributes"] = validate_type_attributes(
            effective_asset_type, fields["type_attributes"]
        )
    return investment_crud.update_investment(db, investment, **fields)


@router.delete("/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investment(investment_id: uuid.UUID, db: DbSession, _: DeleteAccess):
    investment = _get_or_404(db, investment_id)
    investment_crud.delete_investment(db, investment)


@router.get("/{investment_id}/ownerships", response_model=Page[OwnershipRead])
def list_investment_ownerships(
    investment_id: uuid.UUID, db: DbSession, _: CurrentUser, limit: Limit = 50, offset: Offset = 0
):
    _get_or_404(db, investment_id)
    items, total = investment_crud.list_investment_ownerships(db, investment_id, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "/{investment_id}/ownerships", response_model=OwnershipRead, status_code=status.HTTP_201_CREATED
)
def create_investment_ownership(
    investment_id: uuid.UUID, data: OwnershipCreate, db: DbSession, _: WriteAccess
):
    _get_or_404(db, investment_id)
    _require_entity(db, data.entity_id)
    return investment_crud.create_ownership(db, investment_id=investment_id, **data.model_dump())


@router.get("/{investment_id}/transactions", response_model=Page[TransactionRead])
def list_investment_transactions(
    investment_id: uuid.UUID, db: DbSession, _: CurrentUser, limit: Limit = 50, offset: Offset = 0
):
    _get_or_404(db, investment_id)
    items, total = investment_crud.list_investment_transactions(db, investment_id, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "/{investment_id}/transactions",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_investment_transaction(
    investment_id: uuid.UUID, data: TransactionCreate, db: DbSession, _: WriteAccess
):
    _get_or_404(db, investment_id)
    _require_entity(db, data.entity_id)
    if data.counterparty_id is not None:
        _require_counterparty(db, data.counterparty_id)
    return transaction_crud.create_transaction(db, investment_id=investment_id, **data.model_dump())


@router.get("/{investment_id}/counterparties", response_model=Page[InvestmentCounterpartyRead])
def list_investment_counterparties(
    investment_id: uuid.UUID, db: DbSession, _: CurrentUser, limit: Limit = 50, offset: Offset = 0
):
    _get_or_404(db, investment_id)
    items, total = investment_crud.list_investment_counterparties(db, investment_id, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "/{investment_id}/counterparties",
    response_model=InvestmentCounterpartyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_investment_counterparty(
    investment_id: uuid.UUID, data: InvestmentCounterpartyCreate, db: DbSession, _: WriteAccess
):
    _get_or_404(db, investment_id)
    _require_counterparty(db, data.counterparty_id)
    return investment_crud.create_investment_counterparty(
        db, investment_id=investment_id, **data.model_dump()
    )


@router.get("/{investment_id}/documents", response_model=Page[DocumentRead])
def list_investment_documents(
    investment_id: uuid.UUID, db: DbSession, _: CurrentUser, limit: Limit = 50, offset: Offset = 0
):
    _get_or_404(db, investment_id)
    items, total = investment_crud.list_investment_documents(db, investment_id, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post(
    "/{investment_id}/documents", response_model=DocumentRead, status_code=status.HTTP_201_CREATED
)
def upload_investment_document(
    investment_id: uuid.UUID,
    db: DbSession,
    current_user: WriteAccess,
    file: UploadedFile,
    doc_type: DocTypeForm,
    tax_year: TaxYearForm = None,
    notes: NotesForm = None,
):
    _get_or_404(db, investment_id)
    return save_uploaded_document(
        db,
        file=file,
        doc_type=doc_type,
        tax_year=tax_year,
        entity_id=None,
        investment_id=investment_id,
        transaction_id=None,
        notes=notes,
        uploaded_by=current_user.id,
    )
