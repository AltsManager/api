from datetime import date

from sqlalchemy import Date, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import AssetType, InvestmentStatus, ValuationSource
from app.models.mixins import IDMixin, TimestampMixin
from app.models.types import str_enum


class Investment(IDMixin, TimestampMixin, Base):
    __tablename__ = "investment"

    name: Mapped[str] = mapped_column(String(255))
    asset_type: Mapped[AssetType] = mapped_column(str_enum(AssetType))
    status: Mapped[InvestmentStatus] = mapped_column(
        str_enum(InvestmentStatus), default=InvestmentStatus.ACTIVE
    )
    acquisition_date: Mapped[date] = mapped_column(Date)
    initial_investment_amount: Mapped[float] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    current_valuation: Mapped[float | None] = mapped_column(Numeric(18, 2))
    valuation_date: Mapped[date | None] = mapped_column(Date)
    valuation_source: Mapped[ValuationSource | None] = mapped_column(str_enum(ValuationSource))
    type_attributes: Mapped[dict] = mapped_column(JSONB, default=dict)
    notes: Mapped[str | None] = mapped_column(Text)
