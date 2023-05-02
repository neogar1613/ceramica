from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from api.user.models import (
    UserCreate,
    GetUser,
    UpdatedUserResponse,
    DeleteUserResponse,
    UserUpdate
)
from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional

from db.session import get_db
from api.user.actions import (
    create_new_user,
    check_email_exists,
    get_all_users,
    get_by_id_or_email,
    update_user,
    activate_user,
    deactivate_user,
    delete_user
)
from api.user.exceptions import UserExists
from api.auth.actions import get_current_user_from_token
from utils.error_handlers import raise_custom_exception


user_router = APIRouter()


@user_router.post("/create", response_model=GetUser)
async def create_user_handler(data: UserCreate, db: AsyncSession = Depends(get_db)):
    exists: bool = await check_email_exists(email=data.email, db=db)
    if exists:
        raise UserExists(msg="Email already exists")
    try:
        result = await create_new_user(data=data, db=db)
    except UserExists as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.err_msg)
    return result


@user_router.get("/get_all_users", response_model=list[GetUser])
async def get_all_users_handler(limit: Optional[int] = 10, offset: Optional[int] = 0,
                                db: AsyncSession = Depends(get_db)):
    return await get_all_users(limit=limit, offset=offset, db=db)


@user_router.get("/get_by_id_or_email", response_model=GetUser)
async def get_user_handler(user_id_or_email: Union[UUID, EmailStr],
                           db: AsyncSession = Depends(get_db)):
    user = await get_by_id_or_email(user_id_or_email=user_id_or_email, db=db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or not active")
    return user


@user_router.get("/me", response_model=GetUser)
async def get_current_user_handler(current_user = Depends(get_current_user_from_token),
                                   db: AsyncSession = Depends(get_db)):
    return GetUser(**current_user)


@user_router.put("/update", response_model=UpdatedUserResponse)
async def update_user_data_handler(user_id: UUID,
                                   updated_data: UserUpdate,
                                   db: AsyncSession = Depends(get_db)):
    updated_user_id = await update_user(updated_data=updated_data.dict(), user_id=user_id, db=db)
    if updated_user_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or not active")
    return UpdatedUserResponse(updated_user_id=updated_user_id, message='User updated')


@user_router.patch("/activate", response_model=DeleteUserResponse)
async def activate_user_handler(user_id_or_email: Union[UUID, EmailStr], db: AsyncSession = Depends(get_db)):
    activated_user_id = await activate_user(user_id_or_email=user_id_or_email, db=db)
    if activated_user_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or active")
    return DeleteUserResponse(user_id=activated_user_id, message="User activated")


@user_router.patch("/deactivate", response_model=DeleteUserResponse)
async def deactivate_user_handler(user_id_or_email: Union[UUID, EmailStr], db: AsyncSession = Depends(get_db)):
    deactivated_user_id = await deactivate_user(user_id_or_email=user_id_or_email, db=db)
    if deactivated_user_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or not active")
    return DeleteUserResponse(user_id=deactivated_user_id, message="User deactivated")


@user_router.delete("/delete", response_model=DeleteUserResponse)
async def delete_user_handler(user_id_or_email: Union[UUID, EmailStr], db: AsyncSession = Depends(get_db)):
    deleted_user_id = await delete_user(user_id_or_email=user_id_or_email, db=db)
    if deleted_user_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return DeleteUserResponse(user_id=deleted_user_id, message="User deleted")
