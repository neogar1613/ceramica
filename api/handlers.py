from asyncpg.exceptions import UniqueViolationError
from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from api.models import (
    UserCreate,
    GetUser,
    UpdatedUserResponse,
    DeleteUserResponse,
    UserUpdate
)
from db.session import async_session
from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional
from db.crud import UserCRUD
from db.session import get_db
from api.exceptions import UserExistsError


user_router = APIRouter()


async def _create_new_user(data: UserCreate, db) -> GetUser:
    async with db.begin():
        user_crud = UserCRUD(db)
        try:
            user = await user_crud.create(username=data.username,
                                        name=data.name,
                                        surname=data.surname,
                                        email=data.email,)
        except Exception as e:
            raise UserExistsError(err_msg=str(e.orig).split('DETAIL:')[1].strip())
        return GetUser(user_id=user.user_id,
                       username=user.username,
                       name=user.name,
                       surname=user.surname,
                       email=user.email,
                       is_active=user.is_active,)


async def _get_by_id_or_email(user_id_or_email: Union[UUID, EmailStr], db) -> GetUser:
    async with db.begin():
        user_crud = UserCRUD(db)
        if isinstance(user_id_or_email, UUID):
            user = await user_crud.get_by_id_or_email(user_id=user_id_or_email)
        else:
            user = await user_crud.get_by_id_or_email(user_email=user_id_or_email)
        return GetUser(user_id=user.user_id,
                       username=user.username,
                       name=user.name,
                       surname=user.surname,
                       email=user.email,
                       is_active=user.is_active,)


async def _get_all_users(limit: int, offset: int, db) -> list[GetUser]:
    async with db.begin():
        user_crud = UserCRUD(db)
        users = await user_crud.get_all_users(limit=limit, offset=offset)
        users_list = []
        for user in users:
            users_list.append(user["User"])
        return users_list


async def _update_user(updated_data: dict,
                       user_id: UUID,
                       db) -> Union[UUID, None]:
    async with db.begin():
        user_crud = UserCRUD(db)
        updated_user_id = await user_crud.update(user_id=user_id,
                                                 **updated_data)
        return updated_user_id


async def _deactivate_user(user_id_or_email: Union[UUID, EmailStr], db) -> UUID:
    async with db.begin():
        user_crud = UserCRUD(db)
        if isinstance(user_id_or_email, UUID):
            user_id = await user_crud.deactivate(user_id=user_id_or_email)
        else:
            user_id = await user_crud.deactivate(user_email=user_id_or_email)
        return user_id


async def _check_exists_by_email(email: str, db) -> bool:
    async with db.begin():
        user_crud = UserCRUD(db)
        result = await user_crud.exists_by_email(email=email)
        is_exists: bool = result["anon_1"]
        return is_exists


# def check_user_permissions(target_user: User, current_user: User) -> bool:
#     if PortalRole.ROLE_PORTAL_SUPERADMIN in current_user.roles:
#         raise HTTPException(
#             status_code=406, detail="Superadmin cannot be deleted via API."
#         )
#     if target_user.user_id != current_user.user_id:
#         # check admin role
#         if not {
#             PortalRole.ROLE_PORTAL_ADMIN,
#             PortalRole.ROLE_PORTAL_SUPERADMIN,
#         }.intersection(current_user.roles):
#             return False
#         # check admin deactivate superadmin attempt
#         if (
#             PortalRole.ROLE_PORTAL_SUPERADMIN in target_user.roles
#             and PortalRole.ROLE_PORTAL_ADMIN in current_user.roles
#         ):
#             return False
#         # check admin deactivate admin attempt
#         if (
#             PortalRole.ROLE_PORTAL_ADMIN in target_user.roles
#             and PortalRole.ROLE_PORTAL_ADMIN in current_user.roles
#         ):
#             return False
#     return True



@user_router.post("/create", response_model=GetUser)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        result = await _create_new_user(data=data, db=db)
    except UserExistsError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.err_msg)
    return result

@user_router.post("/check_exists")
async def check_email_exists(email: str, db: AsyncSession = Depends(get_db)):
    return await _check_exists_by_email(email=email, db=db)


@user_router.get("/get_all_users", response_model=list[GetUser])
async def get_all_users(limit: Optional[int] = 10, offset: Optional[int] = 0,
                        db: AsyncSession = Depends(get_db)):
    return await _get_all_users(limit=limit, offset=offset, db=db)


@user_router.get("/get_by_id_or_email", response_model=GetUser)
async def get_user_by_id(user_id_or_email: Union[UUID, EmailStr],
                         db: AsyncSession = Depends(get_db)):
    return await _get_by_id_or_email(user_id_or_email=user_id_or_email, db=db)


@user_router.put("/update", response_model=UpdatedUserResponse)
async def update_user_data(user_id: UUID,
                           updated_data: UserUpdate,
                           db: AsyncSession = Depends(get_db)):
    updated_user_id = await _update_user(updated_data=updated_data, user_id=user_id, db=db)
    if updated_user_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or not active")
    return UpdatedUserResponse(updated_user_id=updated_user_id)


@user_router.delete("/delete", response_model=DeleteUserResponse)
async def delete_user(user_id_or_email: Union[UUID, EmailStr], db: AsyncSession = Depends(get_db)):
    pass


@user_router.patch("/deactivate", response_model=DeleteUserResponse)
async def deactivate_user(user_id_or_email: Union[UUID, EmailStr], db: AsyncSession = Depends(get_db)):
    deactivated_user_id = await _deactivate_user(user_id_or_email=user_id_or_email, db=db)
    if deactivated_user_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or not active")
    return DeleteUserResponse(deactivated_user_id=deactivated_user_id, message="User deactivated")
