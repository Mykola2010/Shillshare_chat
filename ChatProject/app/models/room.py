from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base

room_members = Table(
    "room_members",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("room_id", Integer, ForeignKey("rooms.id")),
)

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    members = relationship("User", secondary=room_members, back_populates="rooms")
    messages = relationship("RoomMessage", back_populates="room")

class RoomMessage(Base):
    __tablename__ = "room_messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    room = relationship("Room", back_populates="messages")
    sender = relationship("User")
