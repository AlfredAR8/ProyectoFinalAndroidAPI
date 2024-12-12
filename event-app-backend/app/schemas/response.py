# app/schemas/response.py
from pydantic import BaseModel

class ResponseCreate(BaseModel):
    status: str  # "going", "interested", "not going"
    ticket_purchased: bool = False