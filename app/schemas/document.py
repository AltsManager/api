import uuid
from datetime import datetime
from typing import Annotated

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, ConfigDict

from app.models.enums import DocumentStatus, DocumentType

UploadedFile = Annotated[UploadFile, File()]
DocTypeForm = Annotated[DocumentType, Form()]
TaxYearForm = Annotated[int | None, Form()]
NotesForm = Annotated[str | None, Form()]


class DocumentUpdate(BaseModel):
    doc_type: DocumentType | None = None
    tax_year: int | None = None
    status: DocumentStatus | None = None
    notes: str | None = None


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    content_type: str
    size_bytes: int
    doc_type: DocumentType
    tax_year: int | None
    status: DocumentStatus
    entity_id: uuid.UUID | None
    investment_id: uuid.UUID | None
    transaction_id: uuid.UUID | None
    uploaded_by: uuid.UUID
    uploaded_at: datetime
    notes: str | None
