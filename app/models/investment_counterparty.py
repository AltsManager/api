import uuid

from sqlalchemy import ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import CounterpartyRole
from app.models.mixins import IDMixin
from app.models.types import str_enum


class InvestmentCounterparty(IDMixin, Base):
    __tablename__ = "investment_counterparty"

    investment_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("investment.id"), index=True)
    counterparty_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("counterparty.id"), index=True
    )
    role: Mapped[CounterpartyRole] = mapped_column(str_enum(CounterpartyRole))
    notes: Mapped[str | None] = mapped_column(Text)
