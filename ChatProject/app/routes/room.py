from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db, get_current_user
from app.database import SessionLocal
from app.models.room import Room, RoomMessage
from app.models.user import User
from app.schemas.room import RoomCreate, RoomRead, RoomMessageCreate, RoomMessageRead

router = APIRouter(tags=["Rooms"])


@router.post("/rooms", response_model=RoomRead)
def create_room(room_in: RoomCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Room).filter(Room.name == room_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Room already exists")
    room = Room(name=room_in.name)
    room.members.append(current_user)
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

@router.post("/rooms/join/{room_id}", response_model=RoomRead)
def join_room(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if current_user not in room.members:
        room.members.append(current_user)
        db.commit()
    return room

@router.get("/rooms", response_model=list[RoomRead])
def list_rooms(db: Session = Depends(get_db)):
    return db.query(Room).all()

@router.post("/rooms/message", response_model=RoomMessageRead)
def send_room_message(msg_in: RoomMessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = db.query(Room).filter(Room.id == msg_in.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if current_user not in room.members:
        raise HTTPException(status_code=403, detail="You are not a member of this room")
    msg = RoomMessage(room_id=room.id, sender_id=current_user.id, content=msg_in.content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

@router.get("/rooms/messages/{room_id}", response_model=list[RoomMessageRead])
def get_room_messages(room_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if current_user not in room.members:
        raise HTTPException(status_code=403, detail="You are not a member of this room")
    return db.query(RoomMessage).filter(RoomMessage.room_id == room.id).order_by(RoomMessage.timestamp.asc()).all()
