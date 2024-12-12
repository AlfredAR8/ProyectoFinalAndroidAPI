# app/models/__init__.py
from .database import Base, engine
from .user import User
from .event import Event
from .response import Response

# Crear todas las tablas en la base de datos
Base.metadata.create_all(bind=engine)