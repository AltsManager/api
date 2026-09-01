from typing import Any

from sqlalchemy.orm import Session

from app.crud import base
from app.models.document import Document


def create_document(db: Session, **fields):
    return base.create(db, Document, **fields)


def get_document(db: Session, document_id) -> Document | None:
    return db.get(Document, document_id)


def list_documents(db: Session, limit: int, offset: int, *filters: Any):
    return base.list_paginated(db, Document, limit, offset, *filters)


def update_document(db: Session, document: Document, **fields):
    return base.update(db, document, **fields)
