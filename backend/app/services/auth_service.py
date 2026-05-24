from urllib.parse import quote

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.utils.security import get_password_hash, verify_password


def register_user(db: Session, user_data: UserCreate) -> User:
    """Register a new user after checking username and email uniqueness."""
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise ConflictError(detail="El nombre de usuario ya está registrado")
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise ConflictError(detail="El correo electrónico ya está registrado")
    hashed_password = get_password_hash(user_data.password)
    safe_name = quote(f"{user_data.first_name} {user_data.last_name}", safe="")
    avatar_url = f"https://ui-avatars.com/api/?name={safe_name}&background=random"
    new_user = User(
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        avatar_url=avatar_url,
        email=user_data.email,
        hashed_password=hashed_password,
        role="cliente",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user(db: Session, username: str, password: str) -> User:
    """Verify credentials and return the user. Raises UnauthorizedError on failure."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        user = db.query(User).filter(User.email == username).first()
    if not user:
        raise UnauthorizedError(detail="Usuario o contraseña inválidos")

    if not verify_password(password, user.hashed_password):
        raise UnauthorizedError(detail="Usuario o contraseña inválidos")

    if not user.is_active:
        raise UnauthorizedError(detail="La cuenta de usuario está desactivada")

    return user


def get_user_by_id(db: Session, user_id: int) -> User:
    """Fetch a user by ID. Raises NotFoundError if not found."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError(detail=f"Usuario con id {user_id} no encontrado")
    return user
