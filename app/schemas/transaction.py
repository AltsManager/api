import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import TransactionType


class TransactionCreate(BaseModel):
    entity_id: uuid.UUID
    transaction_type: TransactionType
    transaction_date: date
    amount: float
    currency: str = "USD"
    units_delta: float | None = None
    price_per_unit: float | None = None
    counterparty_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    notes: str | None = None


class TransactionUpdate(BaseModel):
    transaction_type: TransactionType | None = None
    transaction_date: date | None = None
    amount: float | None = None
    currency: str | None = None
    units_delta: float | None = None
    price_per_unit: float | None = None
    counterparty_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    notes: str | None = None


class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    investment_id: uuid.UUID
    entity_id: uuid.UUID
    transaction_type: TransactionType
    transaction_date: date
    amount: float
    currency: str
    units_delta: float | None
    price_per_unit: float | None
    counterparty_id: uuid.UUID | None
    document_id: uuid.UUID | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
