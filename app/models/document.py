import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import DocumentStatus, DocumentType
from app.models.mixins import IDMixin
from app.models.types import str_enum


class Document(IDMixin, Base):
    __tablename__ = "document"
    __table_args__ = (
        CheckConstraint(
            "entity_id IS NOT NULL OR investment_id IS NOT NULL OR transaction_id IS NOT NULL",
            name="ck_document_has_linked_record",
        ),
    )

    filename: Mapped[str] = mapped_column(String(255))
    storage_key: Mapped[str] = mapped_column(String(512))
    content_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int] = mapped_column(Integer)
    doc_type: Mapped[DocumentType] = mapped_column(str_enum(DocumentType))
    tax_year: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[DocumentStatus] = mapped_column(
        str_enum(DocumentStatus), default=DocumentStatus.PENDING_REVIEW
    )
    entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("entity.id"))
    investment_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("investment.id"))
    transaction_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("transaction.id"))
    uploaded_by: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id"))
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    notes: Mapped[str | None] = mapped_column(Text)
