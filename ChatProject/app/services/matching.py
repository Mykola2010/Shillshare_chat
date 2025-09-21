from sqlalchemy.orm import Session
from app.models.user import User
from app.models.matches import Match



def find_matches_for_user(db: Session, current_user: User):
    my_skill_ids = {s.id for s in current_user.skills}
    if not my_skill_ids:
        return {"message": "Додайте навички, щоб знайти співпадіння"}

    users = db.query(User).filter(User.id != current_user.id).all()
    matches = []

    for u in users:
        common_skills = my_skill_ids & {s.id for s in u.skills}
        if common_skills:
            matches.append({
                "user_id": u.id,
                "username": u.username,
                "common_skills": [s.name for s in u.skills if s.id in common_skills]
            })

    return {"matches": matches}



def save_match_in_db(db: Session, current_user: User, user_id: int):
    new_match = Match(user1_id=current_user.id, user2_id=user_id)
    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return {"message": "Матч збережено", "match_id": new_match.id}