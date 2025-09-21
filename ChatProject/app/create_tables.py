# app/create_tables.py
from app.database import Base, engine
from app.models.room import Room, RoomMessage
from app.models.user import User

Base.metadata.create_all(bind=engine)
print("Tables created successfully!")
