from pydantic import BaseModel
from datetime import datetime

class RoomCreate(BaseModel):
    name: str

class RoomRead(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class RoomMessageCreate(BaseModel):
    room_id: int
    content: str

class RoomMessageRead(BaseModel):
    id: int
    room_id: int
    sender_id: int
    content: str
    timestamp: datetime
    class Config:
        from_attributes = True
