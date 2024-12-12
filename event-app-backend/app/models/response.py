# app/models/response.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    status = Column(String, nullable=False)  # "going", "interested", "not going"
    ticket_purchased = Column(Boolean, default=False)

    user = relationship("User", back_populates="responses")
    event = relationship("Event", back_populates="responses")