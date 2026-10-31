"""Room endpoints addressed directly by room id."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/rooms", tags=["rooms"])


def _get_room(room_id: int, db: Session) -> models.Room:
    room = db.get(models.Room, room_id)
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    return room


@router.get("/{room_id}", response_model=schemas.RoomOut)
def get_room(room_id: int, db: Session = Depends(get_db)):
    return _get_room(room_id, db)


@router.patch("/{room_id}", response_model=schemas.RoomOut)
def update_room(
    room_id: int, payload: schemas.RoomUpdate, db: Session = Depends(get_db)
):
    room = _get_room(room_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Another room with that number already exists in this property",
        )
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = _get_room(room_id, db)
    db.delete(room)
    db.commit()
