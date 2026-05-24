from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings
from app.utils.exceptions import UnauthorizedError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plain-text password against a bcrypt hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Return the bcrypt hash of the given plain-text password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT containing *data* with an expiration claim."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "iat": now})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT.  Raises UnauthorizedError on any failure."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM],
            options={"verify_exp": True, "leeway": 0}
        )
        if payload is None:
            raise UnauthorizedError(detail="Payload de token inválido")
        return payload
    except JWTError as e:
        if "Signature has expired" in str(e):
            raise UnauthorizedError(detail="El token ha expirado")
        raise UnauthorizedError(detail="No se pudieron validar las credenciales")
