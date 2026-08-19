import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import TransactionType
from app.models.mixins import IDMixin, TimestampMixin
from app.models.types import str_enum


class Transaction(IDMixin, TimestampMixin, Base):
    __tablename__ = "transaction"

    investment_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("investment.id"), index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("entity.id"), index=True)
    transaction_type: Mapped[TransactionType] = mapped_column(str_enum(TransactionType))
    transaction_date: Mapped[date] = mapped_column(Date)
    amount: Mapped[float] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    units_delta: Mapped[float | None] = mapped_column(Numeric(24, 8))
    price_per_unit: Mapped[float | None] = mapped_column(Numeric(18, 8))
    counterparty_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, ForeignKey("counterparty.id"))
    document_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("document.id", use_alter=True, name="fk_transaction_document_id")
    )
    notes: Mapped[str | None] = mapped_column(Text)
