from sqlalchemy.orm import Session
from app.models.chat import Message


def get_or_create_chat(db: Session, user1_id: int, user2_id: int):
    chat = db.query(Message).filter(
        ((Message.user1_id == user1_id) & (Message.user2_id == user2_id)) |
        ((Message.user1_id == user2_id) & (Message.user2_id == user1_id))
    ).first()

    if chat:
        return chat

    chat = Message(user1_id=user1_id, user2_id=user2_id)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_user_chats(db: Session, user_id: int):
    return db.query(Message).filter(
        (Message.user1_id == user_id) | (Message.user2_id == user_id)
    ).all()