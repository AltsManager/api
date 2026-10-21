import os
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import NotFoundError, ValidationError
from app.crud import document as document_crud
from app.crud import entity as entity_crud
from app.crud import investment as investment_crud
from app.crud import transaction as transaction_crud
from app.models.document import Document
from app.models.enums import DocumentType
from app.services.storage import get_storage_backend


def validate_document_links(
    db: Session,
    entity_id: uuid.UUID | None,
    investment_id: uuid.UUID | None,
    transaction_id: uuid.UUID | None,
) -> None:
    if entity_id is None and investment_id is None and transaction_id is None:
        raise ValidationError(
            "At least one of entity_id, investment_id, or transaction_id is required"
        )
    if entity_id is not None and entity_crud.get_entity(db, entity_id) is None:
        raise NotFoundError("Entity", entity_id)
    if investment_id is not None and investment_crud.get_investment(db, investment_id) is None:
        raise NotFoundError("Investment", investment_id)
    if transaction_id is not None and transaction_crud.get_transaction(db, transaction_id) is None:
        raise NotFoundError("Transaction", transaction_id)


def save_uploaded_document(
    db: Session,
    *,
    file: UploadFile,
    doc_type: DocumentType,
    tax_year: int | None,
    entity_id: uuid.UUID | None,
    investment_id: uuid.UUID | None,
    transaction_id: uuid.UUID | None,
    notes: str | None,
    uploaded_by: uuid.UUID,
) -> Document:
    validate_document_links(db, entity_id, investment_id, transaction_id)

    settings = get_settings()
    content_type = file.content_type or "application/octet-stream"
    if content_type not in settings.allowed_document_content_type_list:
        raise ValidationError(f"Unsupported file type: {content_type}")

    size_bytes = file.size
    if size_bytes is None:
        file.file.seek(0, os.SEEK_END)
        size_bytes = file.file.tell()
        file.file.seek(0)
    if size_bytes > settings.max_upload_size_bytes:
        raise ValidationError(
            f"File exceeds maximum upload size of {settings.max_upload_size_bytes} bytes"
        )

    filename = Path(file.filename or "upload").name
    storage_key = f"{uuid.uuid4().hex}/{filename}"
    get_storage_backend().save(file.file, storage_key, content_type)

    return document_crud.create_document(
        db,
        filename=filename,
        storage_key=storage_key,
        content_type=content_type,
        size_bytes=size_bytes,
        doc_type=doc_type,
        tax_year=tax_year,
        entity_id=entity_id,
        investment_id=investment_id,
        transaction_id=transaction_id,
        uploaded_by=uploaded_by,
        notes=notes,
    )
