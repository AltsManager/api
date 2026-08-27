import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import OwnershipType


class OwnershipCreate(BaseModel):
    entity_id: uuid.UUID
    effective_date: date
    end_date: date | None = None
    percentage: float | None = None
    units: float | None = None
    ownership_type: OwnershipType = OwnershipType.DIRECT
    notes: str | None = None


class OwnershipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entity_id: uuid.UUID
    investment_id: uuid.UUID
    effective_date: date
    end_date: date | None
    percentage: float | None
    units: float | None
    ownership_type: OwnershipType
    notes: str | None
