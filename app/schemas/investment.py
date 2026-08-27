import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.models.enums import AssetType, InvestmentStatus, ValuationSource
from app.schemas.investment_attributes import validate_type_attributes


class InvestmentCreate(BaseModel):
    name: str
    asset_type: AssetType
    status: InvestmentStatus = InvestmentStatus.ACTIVE
    acquisition_date: date
    initial_investment_amount: float
    currency: str = "USD"
    current_valuation: float | None = None
    valuation_date: date | None = None
    valuation_source: ValuationSource | None = None
    type_attributes: dict = {}
    notes: str | None = None

    @model_validator(mode="after")
    def _validate_type_attributes(self) -> "InvestmentCreate":
        self.type_attributes = validate_type_attributes(self.asset_type, self.type_attributes)
        return self


class InvestmentUpdate(BaseModel):
    name: str | None = None
    asset_type: AssetType | None = None
    status: InvestmentStatus | None = None
    acquisition_date: date | None = None
    initial_investment_amount: float | None = None
    currency: str | None = None
    current_valuation: float | None = None
    valuation_date: date | None = None
    valuation_source: ValuationSource | None = None
    type_attributes: dict | None = None
    notes: str | None = None


class InvestmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    asset_type: AssetType
    status: InvestmentStatus
    acquisition_date: date
    initial_investment_amount: float
    currency: str
    current_valuation: float | None
    valuation_date: date | None
    valuation_source: ValuationSource | None
    type_attributes: dict
    notes: str | None
    created_at: datetime
    updated_at: datetime
