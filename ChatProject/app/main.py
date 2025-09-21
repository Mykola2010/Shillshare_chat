import pathlib
from typing import List

from fastapi import FastAPI, Request, Cookie, Depends, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import Base, engine
from app.models.chat import Message
from app.models.user import User
from app.routes import room
from app.routes.skills import router as skills_router
from app.schemas.chat import MessageCreate, MessageRead
from app.schemas.user import UserCreate
from app.utils.dependencies import get_current_user, get_db
from app.utils.security import create_access_token, hash_password

app = FastAPI()
Base.metadata.create_all(bind=engine)
router = APIRouter(tags=["Rooms"])
app.include_router(skills_router)
app.include_router(room.router)

BASE_DIR = pathlib.Path(__file__).parent

static_dir = BASE_DIR / "static"
template_dir = BASE_DIR / "templates"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


templates = Jinja2Templates(directory=template_dir)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@router.get("/me")
def me(user_id: str = Cookie(None), db: Session = Depends(get_db)):
    if not user_id:
        return JSONResponse({"error": "Not logged in"}, status_code=401)

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return JSONResponse({"error": "User not found"}, status_code=401)

    return {"id": user.id, "username": user.username, "email": user.email}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/auth", response_class=HTMLResponse)
async def auth_page(request: Request, mode: str = "login"):
    return templates.TemplateResponse("auth.html", {"request": request, "mode": mode})


@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter((User.email == form_data.username) | (User.username == form_data.username)).first()

    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id)})

    response = JSONResponse(
        content={
            "success": True,
            "redirect": "/dashboard",
            "token": access_token
        }
    )

    return response



@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": str(new_user.id)})

    response = JSONResponse(content={
        "success": True,
        "redirect": "/dashboard",
        "token": token
    })
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )
    return response


@app.get("/chats-page", response_class=HTMLResponse)
async def chat_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("chat.html", {"request": request, "user": current_user})

@app.get("/chats", response_model=List[dict])
def get_chats(current_user: User = Depends(get_current_user)):
    return [
        {"id": 1, "name": "General Chat"},
        {"id": 2, "name": "Project Alpha"},
        {"id": 3, "name": "Random"},
    ]


@app.get("/dashboard-data")
def get_dashboard_data(current_user: User = Depends(get_current_user)):
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
        },
        "navigation": [
            {"name": "Головна", "href": "#", "icon": "HomeIcon"},
            {"name": "Чати", "href": "#", "icon": "ChatBubbleLeftRightIcon"},
            {"name": "Проекти", "href": "#", "icon": "FolderIcon"},
        ]
    }


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request,}
    )


@app.post("/send-message", response_model=MessageRead)
def send_message(
        message_in: MessageCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    receiver = db.query(User).filter(User.id == message_in.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        content=message_in.content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@app.get("/messages-with/{user_id}", response_model=List[MessageRead])
def get_messages_with_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    messages = db.query(Message).filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    return messages

@router.get("/rooms", response_model=List[dict])
def get_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Room).all()
    return [{"id": r.id, "name": r.name} for r in rooms]

# Create a room
@router.post("/rooms", response_model=dict)
def create_room(name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    room = Room(name=name)
    db.add(room)
    db.commit()
    db.refresh(room)
    return {"id": room.id, "name": room.name}