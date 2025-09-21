from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db
from app.models.skill import Skill
from app.models.user import User
from app.schemas.skill import SkillCreate, SkillOut
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.post(
    "/",
    response_model=SkillOut,
    summary="Створити навичку",
    description="""
Створює нову навичку у базі.

- Перевіряє, чи навичка з таким іменем вже існує.
- Якщо існує — повертає помилку `400`.
- Якщо не існує — створює навичку та повертає її дані.
""",
    responses={
        201: {"description": "Навичка успішно створена", "model": SkillOut},
        400: {"description": "Така навичка вже існує"},
    },
    status_code=201,
)
def create_skill(skill: SkillCreate, db: Session = Depends(get_db)):
    existing = db.query(Skill).filter(Skill.name == skill.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Така навичка вже існує")
    new_skill = Skill(name=skill.name)
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill


@router.post(
    "/add/{skill_id}",
    summary="Додати навичку користувачу",
    description="""
Додає існуючу навичку користувачу.

- Перевіряє, чи навичка з `skill_id` існує.
- Якщо навичку не знайдено — повертає `404`.
- Додає навичку до поточного користувача та повертає повідомлення про успіх.
""",
    responses={
        200: {"description": "Навичка успішно додана користувачу"},
        401: {"description": "Неавторизований запит"},
        404: {"description": "Навичка не знайдена"},
    },
)
def add_skill_to_user(
        skill_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    skill = db.query(Skill).filter(Skill.id == skill_id).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill не знайдено")

    current_user.skills.append(skill)
    db.commit()
    return {"message": f"Навичка {skill.name} додана користувачу {current_user.username}"}


@router.get(
    "/my",
    response_model=list[SkillOut],
    summary="Отримати свої навички",
    description="""
Повертає список усіх навичок поточного авторизованого користувача.

- Потрібна авторизація через токен.
- Використовується для перегляду власних навичок.
""",
    responses={
        200: {"description": "Список навичок поточного користувача", "model": list[SkillOut]},
        401: {"description": "Неавторизований запит"},
    },
)
def get_my_skills(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return current_user.skills