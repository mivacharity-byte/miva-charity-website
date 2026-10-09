from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models import Admin
from schemas.admin import AdminResponse
from schemas.auth import TokenResponse
from security import create_access_token, get_current_admin
from services.auth import authenticate_admin


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    admin = authenticate_admin(
        db=db,
        email=form_data.username,
        password=form_data.password,
    )

    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=str(admin.id),
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=AdminResponse,
)
def get_me(
    current_admin: Admin = Depends(get_current_admin),
) -> AdminResponse:
    return AdminResponse.model_validate(current_admin)