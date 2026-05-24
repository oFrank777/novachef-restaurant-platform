from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserResponse
from app.services import auth_service
from app.utils.constants import INTERNAL_ERROR_DETAIL
from app.utils.exceptions import AppException
from app.utils.security import create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = auth_service.register_user(db, user_data)
        return new_user
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        user = auth_service.authenticate_user(
            db, form_data.username, form_data.password
        )
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role},
            expires_delta=access_token_expires,
        )
        return TokenResponse(access_token=access_token, token_type="bearer")
    except AppException:
        raise
    except Exception:
        raise AppException(status_code=500, detail=INTERNAL_ERROR_DETAIL)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
