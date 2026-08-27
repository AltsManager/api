import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import EntityType


class EntityCreate(BaseModel):
    name: str
    entity_type: EntityType
    tax_id: str | None = None
    formation_date: date | None = None
    jurisdiction: str | None = None
    notes: str | None = None


class EntityUpdate(BaseModel):
    name: str | None = None
    entity_type: EntityType | None = None
    tax_id: str | None = None
    formation_date: date | None = None
    jurisdiction: str | None = None
    notes: str | None = None


class EntityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    entity_type: EntityType
    tax_id: str | None
    formation_date: date | None
    jurisdiction: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
