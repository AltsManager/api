import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi.responses import StreamingResponse

from app.core.deps import CurrentUser, DbSession, Limit, Offset, require_role
from app.core.exceptions import NotFoundError
from app.crud import document as document_crud
from app.models.document import Document
from app.models.enums import DocumentStatus, DocumentType, UserRole
from app.models.user import User
from app.schemas.common import Page
from app.schemas.document import (
    DocTypeForm,
    DocumentRead,
    DocumentUpdate,
    NotesForm,
    TaxYearForm,
    UploadedFile,
)
from app.services.documents import save_uploaded_document
from app.services.storage import get_storage_backend

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])

WriteAccess = Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.STAFF))]
EntityIdForm = Annotated[uuid.UUID | None, Form()]
InvestmentIdForm = Annotated[uuid.UUID | None, Form()]
TransactionIdForm = Annotated[uuid.UUID | None, Form()]


def _get_or_404(db: DbSession, document_id: uuid.UUID) -> Document:
    document = document_crud.get_document(db, document_id)
    if document is None:
        raise NotFoundError("Document", document_id)
    return document


@router.post("", response_model=DocumentRead, status_code=201)
def upload_document(
    db: DbSession,
    current_user: WriteAccess,
    file: UploadedFile,
    doc_type: DocTypeForm,
    tax_year: TaxYearForm = None,
    entity_id: EntityIdForm = None,
    investment_id: InvestmentIdForm = None,
    transaction_id: TransactionIdForm = None,
    notes: NotesForm = None,
):
    return save_uploaded_document(
        db,
        file=file,
        doc_type=doc_type,
        tax_year=tax_year,
        entity_id=entity_id,
        investment_id=investment_id,
        transaction_id=transaction_id,
        notes=notes,
        uploaded_by=current_user.id,
    )


@router.get("", response_model=Page[DocumentRead])
def list_documents(
    db: DbSession,
    _: CurrentUser,
    limit: Limit = 50,
    offset: Offset = 0,
    doc_type: DocumentType | None = None,
    status: DocumentStatus | None = None,
    tax_year: int | None = None,
    entity_id: uuid.UUID | None = None,
    investment_id: uuid.UUID | None = None,
    transaction_id: uuid.UUID | None = None,
):
    filters = []
    if doc_type is not None:
        filters.append(Document.doc_type == doc_type)
    if status is not None:
        filters.append(Document.status == status)
    if tax_year is not None:
        filters.append(Document.tax_year == tax_year)
    if entity_id is not None:
        filters.append(Document.entity_id == entity_id)
    if investment_id is not None:
        filters.append(Document.investment_id == investment_id)
    if transaction_id is not None:
        filters.append(Document.transaction_id == transaction_id)

    items, total = document_crud.list_documents(db, limit, offset, *filters)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(document_id: uuid.UUID, db: DbSession, _: CurrentUser):
    return _get_or_404(db, document_id)


@router.patch("/{document_id}", response_model=DocumentRead)
def update_document(document_id: uuid.UUID, data: DocumentUpdate, db: DbSession, _: WriteAccess):
    document = _get_or_404(db, document_id)
    return document_crud.update_document(db, document, **data.model_dump(exclude_unset=True))


@router.get("/{document_id}/download")
def download_document(document_id: uuid.UUID, db: DbSession, _: CurrentUser):
    document = _get_or_404(db, document_id)
    storage = get_storage_backend()
    return StreamingResponse(
        storage.iter_bytes(document.storage_key),
        media_type=document.content_type,
        headers={"Content-Disposition": f'attachment; filename="{document.filename}"'},
    )
