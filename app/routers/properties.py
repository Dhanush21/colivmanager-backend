"""Property endpoints and nested room creation/listing."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/properties", tags=["properties"])


def _get_property(property_id: int, db: Session) -> models.Property:
    prop = db.get(models.Property, property_id)
    if prop is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Property not found")
    return prop


@router.post("", response_model=schemas.PropertyOut, status_code=status.HTTP_201_CREATED)
def create_property(payload: schemas.PropertyCreate, db: Session = Depends(get_db)):
    prop = models.Property(**payload.model_dump())
    db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop


@router.get("", response_model=list[schemas.PropertyOut])
def list_properties(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    stmt = select(models.Property).offset(skip).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{property_id}", response_model=schemas.PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    return _get_property(property_id, db)


@router.patch("/{property_id}", response_model=schemas.PropertyOut)
def update_property(
    property_id: int,
    payload: schemas.PropertyUpdate,
    db: Session = Depends(get_db),
):
    prop = _get_property(property_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(prop, field, value)
    db.commit()
    db.refresh(prop)
    return prop


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property(property_id: int, db: Session = Depends(get_db)):
    prop = _get_property(property_id, db)
    db.delete(prop)
    db.commit()


# --- Nested rooms ------------------------------------------------------

@router.post(
    "/{property_id}/rooms",
    response_model=schemas.RoomOut,
    status_code=status.HTTP_201_CREATED,
    tags=["rooms"],
)
def create_room(
    property_id: int,
    payload: schemas.RoomCreate,
    db: Session = Depends(get_db),
):
    _get_property(property_id, db)
    room = models.Room(property_id=property_id, **payload.model_dump())
    db.add(room)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Room '{payload.number}' already exists in this property",
        )
    db.refresh(room)
    return room


@router.get(
    "/{property_id}/rooms",
    response_model=list[schemas.RoomOut],
    tags=["rooms"],
)
def list_rooms(property_id: int, db: Session = Depends(get_db)):
    _get_property(property_id, db)
    stmt = select(models.Room).where(models.Room.property_id == property_id)
    return db.scalars(stmt).all()
