# app/crud/response.py
from sqlalchemy.orm import Session
from ..models.response import Response
from ..schemas.response import ResponseCreate

def get_response(db: Session, user_id: int, event_id: int):
    return db.query(Response).filter(Response.user_id == user_id, Response.event_id == event_id).first()

def create_or_update_response(db: Session, response: ResponseCreate, user_id: int, event_id: int):
    db_response = get_response(db, user_id, event_id)
    if db_response:
        db_response.status = response.status
        db_response.ticket_purchased = response.ticket_purchased
    else:
        db_response = Response(
            status=response.status,
            ticket_purchased=response.ticket_purchased,
            user_id=user_id,
            event_id=event_id
        )
        db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response