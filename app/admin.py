import uuid

from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.config import get_settings
from app.core.security import verify_password
from app.crud.user import get_user_by_email
from app.db.session import SessionLocal, engine
from app.models.counterparty import Counterparty
from app.models.document import Document
from app.models.entity import Entity
from app.models.enums import UserRole
from app.models.investment import Investment
from app.models.investment_counterparty import InvestmentCounterparty
from app.models.ownership import Ownership
from app.models.transaction import Transaction
from app.models.user import User

SESSION_USER_ID_KEY = "admin_user_id"


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form.get("username"), form.get("password")
        if not email or not password:
            return False

        with SessionLocal() as db:
            user = get_user_by_email(db, str(email))
            if (
                user is None
                or not user.is_active
                or user.role != UserRole.ADMIN
                or not verify_password(str(password), user.hashed_password)
            ):
                return False
            request.session[SESSION_USER_ID_KEY] = str(user.id)
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get(SESSION_USER_ID_KEY)
        if not user_id:
            return False
        with SessionLocal() as db:
            user = db.get(User, uuid.UUID(user_id))
            return user is not None and user.is_active and user.role == UserRole.ADMIN


class EntityAdmin(ModelView, model=Entity):
    column_list = [Entity.id, Entity.name, Entity.entity_type, Entity.jurisdiction]
    form_excluded_columns = [Entity.created_at, Entity.updated_at]


class CounterpartyAdmin(ModelView, model=Counterparty):
    column_list = [
        Counterparty.id,
        Counterparty.name,
        Counterparty.counterparty_type,
        Counterparty.email,
    ]
    form_excluded_columns = [Counterparty.created_at, Counterparty.updated_at]


class InvestmentAdmin(ModelView, model=Investment):
    column_list = [
        Investment.id,
        Investment.name,
        Investment.asset_type,
        Investment.status,
        Investment.initial_investment_amount,
        Investment.current_valuation,
    ]
    form_excluded_columns = [Investment.created_at, Investment.updated_at]


class InvestmentCounterpartyAdmin(ModelView, model=InvestmentCounterparty):
    column_list = [
        InvestmentCounterparty.id,
        InvestmentCounterparty.investment_id,
        InvestmentCounterparty.counterparty_id,
        InvestmentCounterparty.role,
    ]


class OwnershipAdmin(ModelView, model=Ownership):
    column_list = [
        Ownership.id,
        Ownership.entity_id,
        Ownership.investment_id,
        Ownership.percentage,
        Ownership.units,
        Ownership.effective_date,
    ]


class TransactionAdmin(ModelView, model=Transaction):
    column_list = [
        Transaction.id,
        Transaction.investment_id,
        Transaction.entity_id,
        Transaction.transaction_type,
        Transaction.amount,
        Transaction.transaction_date,
    ]
    form_excluded_columns = [Transaction.created_at, Transaction.updated_at]


class DocumentAdmin(ModelView, model=Document):
    column_list = [
        Document.id,
        Document.filename,
        Document.doc_type,
        Document.status,
        Document.tax_year,
        Document.entity_id,
        Document.investment_id,
    ]


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.full_name, User.role, User.is_active]
    form_excluded_columns = [User.hashed_password, User.created_at, User.updated_at]
    can_delete = False


def mount_admin(app: FastAPI) -> Admin:
    settings = get_settings()
    admin = Admin(
        app,
        engine,
        authentication_backend=AdminAuth(secret_key=settings.secret_key),
        base_url="/admin",
        title="AltsManager Admin",
    )
    for view in (
        EntityAdmin,
        CounterpartyAdmin,
        InvestmentAdmin,
        InvestmentCounterpartyAdmin,
        OwnershipAdmin,
        TransactionAdmin,
        DocumentAdmin,
        UserAdmin,
    ):
        admin.add_view(view)
    return admin
