from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session


def create(db: Session, model: type, **fields: Any):
    obj = model(**fields)
    db.add(obj)
    db.flush()
    db.refresh(obj)
    return obj


def list_paginated(db: Session, model: type, limit: int, offset: int, *filters: Any):
    total = db.scalar(select(func.count()).select_from(model).where(*filters)) or 0
    items = db.scalars(
        select(model).where(*filters).order_by(model.id).limit(limit).offset(offset)
    ).all()
    return list(items), total


def update(db: Session, obj: Any, **fields: Any):
    for key, value in fields.items():
        setattr(obj, key, value)
    db.flush()
    db.refresh(obj)
    return obj


def delete(db: Session, obj: Any) -> None:
    db.delete(obj)
    db.flush()
