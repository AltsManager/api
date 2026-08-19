import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import OwnershipType
from app.models.mixins import IDMixin
from app.models.types import str_enum


class Ownership(IDMixin, Base):
    __tablename__ = "ownership"

    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("entity.id"), index=True)
    investment_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("investment.id"), index=True)
    effective_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    percentage: Mapped[float | None] = mapped_column(Numeric(9, 6))
    units: Mapped[float | None] = mapped_column(Numeric(24, 8))
    ownership_type: Mapped[OwnershipType] = mapped_column(
        str_enum(OwnershipType), default=OwnershipType.DIRECT
    )
    notes: Mapped[str | None] = mapped_column(Text)
