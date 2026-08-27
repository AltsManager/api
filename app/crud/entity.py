from sqlalchemy.orm import Session

from app.crud import base
from app.models.entity import Entity
from app.models.ownership import Ownership


def create_entity(db: Session, **fields):
    return base.create(db, Entity, **fields)


def get_entity(db: Session, entity_id) -> Entity | None:
    return db.get(Entity, entity_id)


def list_entities(db: Session, limit: int, offset: int):
    return base.list_paginated(db, Entity, limit, offset)


def update_entity(db: Session, entity: Entity, **fields):
    return base.update(db, entity, **fields)


def delete_entity(db: Session, entity: Entity) -> None:
    base.delete(db, entity)


def list_entity_ownerships(db: Session, entity_id, limit: int, offset: int):
    return base.list_paginated(db, Ownership, limit, offset, Ownership.entity_id == entity_id)
