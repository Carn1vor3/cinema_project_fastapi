from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.schemas.auth import LoginRequest, TokenResponse, RefreshRequest
from src.services.users import login_user, logout_user, refresh_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login_user(data.email, data.password, db)


@router.post("/logout")
async def logout(refresh_token: str, db: AsyncSession = Depends(get_db)):
    return await logout_user(refresh_token, db)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await refresh_access_token(data.refresh_token, db)
