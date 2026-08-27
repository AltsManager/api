import uuid

from pydantic import BaseModel, ConfigDict

from app.models.enums import CounterpartyRole


class InvestmentCounterpartyCreate(BaseModel):
    counterparty_id: uuid.UUID
    role: CounterpartyRole
    notes: str | None = None


class InvestmentCounterpartyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    investment_id: uuid.UUID
    counterparty_id: uuid.UUID
    role: CounterpartyRole
    notes: str | None
