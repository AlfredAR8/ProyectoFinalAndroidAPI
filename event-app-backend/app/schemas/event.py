# app/schemas/event.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .user import UserResponse

class EventBase(BaseModel):
    title: str
    description: str
    date: datetime
    time: str
    location: str
    image: Optional[str] = None

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    time: Optional[str] = None
    location: Optional[str] = None
    image: Optional[str] = None

class UserSummary(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True

class Attendee(BaseModel):
    user: UserSummary
    status: str  # "going", "interested", "not going"
    ticket_purchased: bool

    class Config:
        orm_mode = True

class EventResponse(EventBase):
    id: int
    created_by: UserSummary
    attendees: List[Attendee] = []
    created_at: datetime

    class Config:
        orm_mode = True