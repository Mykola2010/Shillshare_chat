from fastapi import APIRouter, Request, Cookie, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.templates import templates

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    user_id: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not user_id:
        return RedirectResponse("/auth?mode=login")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        return RedirectResponse("/auth?mode=login")

    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})
