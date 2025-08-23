from fastapi import Depends, HTTPException, status
from src.models.users import User, UserGroupEnum
from src.services.users import get_current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
):
    if current_user.group.name != UserGroupEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access"
        )
    return current_user
