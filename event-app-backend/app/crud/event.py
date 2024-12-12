# app/crud/event.py
from sqlalchemy.orm import Session
from ..models.event import Event
from ..schemas.event import EventCreate, EventUpdate
from typing import List, Optional

def get_event(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def get_events(db: Session, skip: int = 0, limit: int = 100) -> List[Event]:
    return db.query(Event).offset(skip).limit(limit).all()

def create_event(db: Session, event: EventCreate, user_id: int):
    db_event = Event(
        title=event.title,
        description=event.description,
        date=event.date,
        time=event.time,
        location=event.location,
        image=event.image,
        created_by=user_id
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(db: Session, event_id: int, event: EventUpdate):
    db_event = get_event(db, event_id)
    if not db_event:
        return None
    for var, value in vars(event).items():
        if value is not None:
            setattr(db_event, var, value)
    db.commit()
    db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: int):
    db_event = get_event(db, event_id)
    if not db_event:
        return False
    db.delete(db_event)
    db.commit()
    return True