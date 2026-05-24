from typing import List

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.exceptions import ForbiddenError, UnauthorizedError
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    payload = decode_access_token(token)

    user_id: int | None = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError(detail="No se pudieron validar las credenciales")

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise UnauthorizedError(detail="No se pudieron validar las credenciales")

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise UnauthorizedError(detail="No se pudieron validar las credenciales")
    if not user.is_active:
        raise UnauthorizedError(detail="No se pudieron validar las credenciales")

    token_role = payload.get("role")
    if token_role is not None and token_role != user.role:
        raise UnauthorizedError(detail="No se pudieron validar las credenciales")

    return user


def require_role(*roles: str):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenError(detail="No tienes permiso para realizar esta acción")
        return current_user

    return role_checker
