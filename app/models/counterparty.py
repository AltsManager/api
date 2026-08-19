from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import CounterpartyType
from app.models.mixins import IDMixin, TimestampMixin
from app.models.types import str_enum


class Counterparty(IDMixin, TimestampMixin, Base):
    __tablename__ = "counterparty"

    name: Mapped[str] = mapped_column(String(255))
    counterparty_type: Mapped[CounterpartyType] = mapped_column(str_enum(CounterpartyType))
    email: Mapped[str | None] = mapped_column(String(320))
    phone: Mapped[str | None] = mapped_column(String(50))
    notes: Mapped[str | None] = mapped_column(Text)
