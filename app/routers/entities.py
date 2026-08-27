import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.deps import CurrentUser, DbSession, Limit, Offset, require_role
from app.core.exceptions import NotFoundError
from app.crud import entity as entity_crud
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.common import Page
from app.schemas.entity import EntityCreate, EntityRead, EntityUpdate
from app.schemas.ownership import OwnershipRead

router = APIRouter(prefix="/api/v1/entities", tags=["entities"])

WriteAccess = Annotated[User, Depends(require_role(UserRole.ADMIN, UserRole.STAFF))]
DeleteAccess = Annotated[User, Depends(require_role(UserRole.ADMIN))]


def _get_or_404(db: DbSession, entity_id: uuid.UUID):
    entity = entity_crud.get_entity(db, entity_id)
    if entity is None:
        raise NotFoundError("Entity", entity_id)
    return entity


@router.get("", response_model=Page[EntityRead])
def list_entities(db: DbSession, _: CurrentUser, limit: Limit = 50, offset: Offset = 0):
    items, total = entity_crud.list_entities(db, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=EntityRead, status_code=status.HTTP_201_CREATED)
def create_entity(data: EntityCreate, db: DbSession, _: WriteAccess):
    return entity_crud.create_entity(db, **data.model_dump())


@router.get("/{entity_id}", response_model=EntityRead)
def get_entity(entity_id: uuid.UUID, db: DbSession, _: CurrentUser):
    return _get_or_404(db, entity_id)


@router.patch("/{entity_id}", response_model=EntityRead)
def update_entity(entity_id: uuid.UUID, data: EntityUpdate, db: DbSession, _: WriteAccess):
    entity = _get_or_404(db, entity_id)
    return entity_crud.update_entity(db, entity, **data.model_dump(exclude_unset=True))


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entity(entity_id: uuid.UUID, db: DbSession, _: DeleteAccess):
    entity = _get_or_404(db, entity_id)
    entity_crud.delete_entity(db, entity)


@router.get("/{entity_id}/ownerships", response_model=Page[OwnershipRead])
def list_entity_ownerships(
    entity_id: uuid.UUID, db: DbSession, _: CurrentUser, limit: Limit = 50, offset: Offset = 0
):
    _get_or_404(db, entity_id)
    items, total = entity_crud.list_entity_ownerships(db, entity_id, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)
