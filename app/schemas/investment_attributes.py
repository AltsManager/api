"""Per-asset-type validation for `Investment.type_attributes`.

Common investment fields (name, status, acquisition_date, amounts, ...) are real
columns on `investment`. `type_attributes` holds only the fields specific to a
given `asset_type`, stored as JSONB. Each asset type gets its own Pydantic model
here (extra fields forbidden), keyed by `AssetType` in `ASSET_TYPE_ATTRIBUTE_MODELS`
and applied via `validate_type_attributes` -- this is the discriminated-union
validation described in the plan, adapted to a top-level `asset_type` column
rather than a discriminator field embedded inside the JSONB itself.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.enums import AssetType


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PrivateStockAttributes(_StrictModel):
    company_name: str | None = None
    share_class: str | None = None
    num_shares: float | None = None
    price_per_share: float | None = None
    round_name: str | None = None


class SafeNoteAttributes(_StrictModel):
    valuation_cap: float | None = None
    discount_rate: float | None = None
    is_post_money: bool | None = None


class ConvertibleNoteAttributes(_StrictModel):
    principal_amount: float | None = None
    interest_rate: float | None = None
    maturity_date: date | None = None
    valuation_cap: float | None = None
    discount_rate: float | None = None


class RealPropertyAttributes(_StrictModel):
    address: str | None = None
    property_type: str | None = None
    square_footage: float | None = None
    ownership_structure: str | None = None


class LlcInterestAttributes(_StrictModel):
    llc_name: str | None = None
    units: float | None = None
    operating_agreement_ref: str | None = None


class PeFundAttributes(_StrictModel):
    fund_name: str | None = None
    commitment_amount: float | None = None
    vintage_year: int | None = None
    called_to_date: float | None = None


class VcFundLpAttributes(_StrictModel):
    fund_name: str | None = None
    commitment_amount: float | None = None
    vintage_year: int | None = None
    called_to_date: float | None = None


class CryptoAttributes(_StrictModel):
    ticker: str | None = None
    quantity: float | None = None
    wallet_or_custodian: str | None = None


class ArtworkAttributes(_StrictModel):
    artist: str | None = None
    title: str | None = None
    medium: str | None = None
    appraisal_source: str | None = None


class OtherAttributes(_StrictModel):
    model_config = ConfigDict(extra="allow")


ASSET_TYPE_ATTRIBUTE_MODELS: dict[AssetType, type[BaseModel]] = {
    AssetType.PRIVATE_STOCK: PrivateStockAttributes,
    AssetType.SAFE_NOTE: SafeNoteAttributes,
    AssetType.CONVERTIBLE_NOTE: ConvertibleNoteAttributes,
    AssetType.REAL_PROPERTY: RealPropertyAttributes,
    AssetType.LLC_INTEREST: LlcInterestAttributes,
    AssetType.PE_FUND: PeFundAttributes,
    AssetType.VC_FUND_LP: VcFundLpAttributes,
    AssetType.CRYPTO: CryptoAttributes,
    AssetType.ARTWORK: ArtworkAttributes,
    AssetType.OTHER: OtherAttributes,
}


def validate_type_attributes(asset_type: AssetType, type_attributes: dict) -> dict:
    model_cls = ASSET_TYPE_ATTRIBUTE_MODELS[asset_type]
    return model_cls.model_validate(type_attributes).model_dump(exclude_none=True)
