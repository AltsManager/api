import enum


class UserRole(enum.StrEnum):
    ADMIN = "admin"
    STAFF = "staff"
    VIEWER = "viewer"


class EntityType(enum.StrEnum):
    INDIVIDUAL = "individual"
    TRUST = "trust"
    LLC = "llc"
    PARTNERSHIP = "partnership"
    CORPORATION = "corporation"
    JOINT = "joint"


class CounterpartyType(enum.StrEnum):
    INDIVIDUAL = "individual"
    LAW_FIRM = "law_firm"
    ACCOUNTING_FIRM = "accounting_firm"
    FUND_MANAGER = "fund_manager"
    SPONSOR = "sponsor"
    BROKER = "broker"
    OTHER = "other"


class CounterpartyRole(enum.StrEnum):
    FUND_MANAGER = "fund_manager"
    SPONSOR = "sponsor"
    LEGAL_COUNSEL = "legal_counsel"
    ACCOUNTANT = "accountant"
    AUDITOR = "auditor"
    BROKER = "broker"
    OTHER = "other"


class AssetType(enum.StrEnum):
    PRIVATE_STOCK = "private_stock"
    SAFE_NOTE = "safe_note"
    CONVERTIBLE_NOTE = "convertible_note"
    REAL_PROPERTY = "real_property"
    LLC_INTEREST = "llc_interest"
    PE_FUND = "pe_fund"
    VC_FUND_LP = "vc_fund_lp"
    CRYPTO = "crypto"
    ARTWORK = "artwork"
    OTHER = "other"


class InvestmentStatus(enum.StrEnum):
    ACTIVE = "active"
    EXITED = "exited"
    WRITTEN_OFF = "written_off"


class ValuationSource(enum.StrEnum):
    MANUAL = "manual"
    THIRD_PARTY = "third_party"
    MARK = "mark"


class OwnershipType(enum.StrEnum):
    DIRECT = "direct"
    INDIRECT = "indirect"


class TransactionType(enum.StrEnum):
    CAPITAL_CALL = "capital_call"
    CONTRIBUTION = "contribution"
    DISTRIBUTION = "distribution"
    PURCHASE = "purchase"
    SALE = "sale"
    VALUATION_UPDATE = "valuation_update"
    FEE = "fee"
    TRANSFER = "transfer"


class DocumentType(enum.StrEnum):
    K1 = "k1"
    SUBSCRIPTION_AGREEMENT = "subscription_agreement"
    SAFE_NOTE = "safe_note"
    OPERATING_AGREEMENT = "operating_agreement"
    CAPITAL_CALL_NOTICE = "capital_call_notice"
    STATEMENT = "statement"
    TAX_FORM = "tax_form"
    VALUATION_REPORT = "valuation_report"
    OTHER = "other"


class DocumentStatus(enum.StrEnum):
    PENDING_REVIEW = "pending_review"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    ARCHIVED = "archived"
