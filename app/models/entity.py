from datetime import date

from sqlalchemy import Date, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import EntityType
from app.models.mixins import IDMixin, TimestampMixin
from app.models.types import str_enum


class Entity(IDMixin, TimestampMixin, Base):
    __tablename__ = "entity"

    name: Mapped[str] = mapped_column(String(255))
    entity_type: Mapped[EntityType] = mapped_column(str_enum(EntityType))
    tax_id: Mapped[str | None] = mapped_column(String(50))
    formation_date: Mapped[date | None] = mapped_column(Date)
    jurisdiction: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)
