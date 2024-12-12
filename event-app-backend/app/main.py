# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from . import models, schemas, crud
from .schemas import auth, event, response
from .crud import auth as auth_crud
from .models.database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm

# Crear todas las tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API de Eventos")

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rutas de Autenticación

@app.post("/register", response_model=schemas.user.UserResponse)
def register(user: schemas.user.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return crud.user.create_user(db=db, user=user)

@app.post("/token", response_model=auth.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth_crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth_crud.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_crud.create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.user.UserResponse)
def read_users_me(current_user: models.User = Depends(auth_crud.get_current_user)):
    return current_user

# Rutas de Eventos

@app.get("/events", response_model=List[event.EventResponse])
def read_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = crud.event.get_events(db, skip=skip, limit=limit)
    return events

@app.get("/events/{event_id}", response_model=event.EventResponse)
def read_event(event_id: int, db: Session = Depends(get_db)):
    db_event = crud.event.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return db_event

@app.post("/events", response_model=event.EventResponse)
def create_new_event(event: event.EventCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth_crud.get_current_user)):
    return crud.event.create_event(db=db, event=event, user_id=current_user.id)

@app.put("/events/{event_id}", response_model=event.EventResponse)
def update_existing_event(event_id: int, event: event.EventUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(auth_crud.get_current_user)):
    db_event = crud.event.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    if db_event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar este evento")
    updated_event = crud.event.update_event(db=db, event_id=event_id, event=event)
    return updated_event

@app.delete("/events/{event_id}")
def delete_existing_event(event_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth_crud.get_current_user)):
    db_event = crud.event.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    if db_event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este evento")
    success = crud.event.delete_event(db=db, event_id=event_id)
    if not success:
        raise HTTPException(status_code=400, detail="No se pudo eliminar el evento")
    return {"detail": "Evento eliminado exitosamente"}

# Ruta para Responder a un Evento

@app.post("/events/{event_id}/respond", response_model=event.EventResponse)
def respond_to_event(event_id: int, response: response.ResponseCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth_crud.get_current_user)):
    db_event = crud.event.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    crud.response.create_or_update_response(db=db, response=response, user_id=current_user.id, event_id=event_id)
    db_event = crud.event.get_event(db, event_id=event_id)  # Actualizar el evento con las nuevas respuestas
    return db_event