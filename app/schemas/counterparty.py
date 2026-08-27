import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums import CounterpartyType


class CounterpartyCreate(BaseModel):
    name: str
    counterparty_type: CounterpartyType
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None


class CounterpartyUpdate(BaseModel):
    name: str | None = None
    counterparty_type: CounterpartyType | None = None
    email: EmailStr | None = None
    phone: str | None = None
    notes: str | None = None


class CounterpartyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    counterparty_type: CounterpartyType
    email: str | None
    phone: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
