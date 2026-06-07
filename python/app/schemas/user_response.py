from app.db.models.user import User


def user_to_dict(user: User) -> dict:
    return {
        "id": user.user_id,
        "username": user.username,
        "email": getattr(user, "email", "") or "",
        "phone": getattr(user, "phone", "") or "",
        "avatar": getattr(user, "avatar", None),
        "role": getattr(user, "role", "user"),
    }
