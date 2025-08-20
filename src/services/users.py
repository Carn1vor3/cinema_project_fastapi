from datetime import datetime, timedelta, timezone
import secrets
from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import HTTPException, Depends
from jwt import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from starlette import status

from database import get_db
from models.users import User, UserProfile
from models.users import ActivationToken, PasswordResetToken, RefreshToken
from schemas.users import UserCreate, UserOut
from core.security import hash_password, verify_password, create_access_token, create_refresh_token, \
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ALGORITHM, SECRET_KEY
from services.email import send_activation_email, send_password_reset_email

ACTIVATION_TOKEN_EXPIRE_HOURS = 24
PASSWORD_RESET_TOKEN_EXPIRE_HOURS = 24
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



async def register_user(user_data: UserCreate, db: AsyncSession) -> UserOut:
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise ValueError("Email already registered")

    hashed_pw = hash_password(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pw,
        is_active=False,
        group_id=1
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    profile = UserProfile(user_id=new_user.id)
    db.add(profile)
    await db.commit()

    token_value = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=ACTIVATION_TOKEN_EXPIRE_HOURS)
    activation_token = ActivationToken(user_id=new_user.id, token=token_value, expires_at=expires_at)
    db.add(activation_token)
    await db.commit()

    await send_activation_email(new_user.email, token_value)

    return UserOut.from_orm(new_user)


async def activate_user(token: str, db: AsyncSession) -> dict:
    result = await db.execute(select(ActivationToken).where(ActivationToken.token == token))
    activation = result.scalars().first()
    if not activation:
        raise ValueError("Invalid token")
    exp = activation.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)

    if exp < datetime.now(timezone.utc):
        raise ValueError("Token expired")

    user = await db.get(User, activation.user_id)
    user.is_active = True
    await db.delete(activation)
    await db.commit()
    return {"message": "Account activated successfully"}


async def resend_activation(email: str, db: AsyncSession) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user:
        raise ValueError("User not found")
    if user.is_active:
        raise HTTPException(status_code=400, detail="User already active")

    result = await db.execute(select(ActivationToken).where(ActivationToken.user_id == user.id))
    old_token = result.scalars().first()
    if old_token:
        await db.delete(old_token)
        await db.commit()

    token_value = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=ACTIVATION_TOKEN_EXPIRE_HOURS)
    new_token = ActivationToken(user_id=user.id, token=token_value, expires_at=expires_at)
    db.add(new_token)
    await db.commit()

    await send_activation_email(user.email, token_value)
    return {"message": "New activation link sent"}


async def request_password_reset(email: str, db: AsyncSession) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not user.is_active:
        raise ValueError("User not found or inactive")

    result = await db.execute(select(PasswordResetToken).where(PasswordResetToken.user_id == user.id))
    old_token = result.scalars().first()
    if old_token:
        await db.delete(old_token)
        await db.commit()

    token_value = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
    reset_token = PasswordResetToken(user_id=user.id, token=token_value, expires_at=expires_at)
    db.add(reset_token)
    await db.commit()

    await send_password_reset_email(user.email, token_value)
    return {"message": "Password reset email sent"}


async def reset_password(token: str, new_password: str, db: AsyncSession) -> dict:
    result = await db.execute(select(PasswordResetToken).where(PasswordResetToken.token == token))
    reset_token = result.scalars().first()
    if not reset_token:
        raise ValueError("Invalid token")
    exp = reset_token.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)

    if exp < datetime.now(timezone.utc):
        raise ValueError("Token expired")

    user = await db.get(User, reset_token.user_id)
    user.hashed_password = hash_password(new_password)
    await db.delete(reset_token)
    await db.commit()
    return {"message": "Password reset successfully"}


async def login_user(email: str, password: str, db: AsyncSession) -> dict:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    if not user or not user.is_active:
        raise ValueError("Invalid credentials or inactive account")
    if not verify_password(password, user.hashed_password):
        raise ValueError("Invalid credentials")

    access_token = create_access_token({"user_id": user.id}, minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_value = create_refresh_token()
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = RefreshToken(user_id=user.id, token=refresh_token_value, expires_at=expires_at)
    db.add(refresh_token)
    await db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token_value}


async def logout_user(token_value: str, db: AsyncSession) -> dict:
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == token_value))
    token = result.scalars().first()
    if token:
        await db.delete(token)
        await db.commit()
    return {"message": "Logged out successfully"}


async def refresh_access_token(refresh_token_value: str, db: AsyncSession) -> dict:
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token_value))
    token = result.scalars().first()
    if not token:
        raise ValueError("Invalid or expired refresh token")

    exp = token.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)

    if exp < datetime.now(timezone.utc):
        raise ValueError("Invalid or expired refresh token")

    access_token = create_access_token({"user_id": token.user_id}, minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,
        "token_type": "bearer"
    }


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await session.execute(
        select(User).options(selectinload(User.group)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


