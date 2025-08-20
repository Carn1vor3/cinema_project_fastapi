from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from dependencies import get_current_admin
from models.users import User, UserGroup
from schemas.users import UserCreate, UserOut, UserUpdateAdmin, UserPasswordUpdate
from services.users import register_user, activate_user, resend_activation, request_password_reset, reset_password

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserOut)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await register_user(user, db)


@router.get("/activate/{token}")
async def activate(token: str, db: AsyncSession = Depends(get_db)):
    return await activate_user(token, db)


@router.post("/resend-activation")
async def resend_activation_link(email: str, db: AsyncSession = Depends(get_db)):
    return await resend_activation(email, db)


@router.post("/password-reset-request")
async def password_reset_request(email: str, db: AsyncSession = Depends(get_db)):
    return await request_password_reset(email, db)


@router.post("/password-reset/{token}")
async def password_reset(token: str, password_data: UserPasswordUpdate, db: AsyncSession = Depends(get_db)):
    return await reset_password(token=token, new_password=password_data.password, db=db)


@router.patch("/{user_id}/admin-update")
async def admin_update_user(
    user_id: int,
    data: UserUpdateAdmin,
    session: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    result = await session.execute(
        select(User).options(selectinload(User.group)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.group is not None:
        result_group = await session.execute(
            select(UserGroup).where(UserGroup.name == data.group)
        )
        group_obj = result_group.scalar_one_or_none()
        if not group_obj:
            raise HTTPException(status_code=404, detail="Group not found")
        user.group = group_obj

    if data.is_active is not None:
        user.is_active = data.is_active

    await session.commit()
    await session.refresh(user)

    return {
        "message": "User updated successfully",
        "user": {
            "id": user.id,
            "group": user.group.name,
            "is_active": user.is_active,
        }
    }


