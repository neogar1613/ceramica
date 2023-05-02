from pydantic import EmailStr
from typing import Union
from uuid import UUID

from api.user.models import (
    UserCreate,
    GetUser
)
from api.user.exceptions import UserExists
from db.crud import UserCRUD
from utils.hashing import Hasher
from utils.error_handlers import raise_custom_exception


async def create_new_user(data: UserCreate, db) -> GetUser:
    async with db.begin():
        user_crud = UserCRUD(db)
        try:
            user = await user_crud.create(username=data.username,
                                          name=data.name,
                                          surname=data.surname,
                                          email=data.email,
                                          hashed_password=Hasher.get_password_hash(plain_password=data.password))
        except Exception:
            raise UserExists(msg='User exists')
        return GetUser(user_id=user.user_id,
                       username=user.username,
                       name=user.name,
                       surname=user.surname,
                       email=user.email,
                       is_active=user.is_active,)


async def get_by_id_or_email(user_id_or_email: Union[UUID, EmailStr], db) -> Union[GetUser, None]:
    async with db.begin():
        user_crud = UserCRUD(db)
        if isinstance(user_id_or_email, UUID):
            user = await user_crud.get_by_id_or_email(user_id=user_id_or_email)
        else:
            user = await user_crud.get_by_id_or_email(user_email=user_id_or_email)
        if user is None:
            return None
        return GetUser(user_id=user.user_id,
                       username=user.username,
                       name=user.name,
                       surname=user.surname,
                       email=user.email,
                       is_active=user.is_active,)


async def get_all_users(limit: int, offset: int, db) -> list[GetUser]:
    async with db.begin():
        user_crud = UserCRUD(db)
        users = await user_crud.get_all_users(limit=limit, offset=offset)
        users_list = []
        for user in users:
            users_list.append(user["User"])
        return users_list


async def update_user(updated_data: dict,
                      user_id: UUID,
                      db) -> Union[UUID, None]:
    # Фильтруем все None значения
    updated_data: dict = {key: value for key, value in updated_data.items() if value is not None}
    async with db.begin():
        user_crud = UserCRUD(db)
        updated_user_id = await user_crud.update(user_id=user_id,
                                                 **updated_data)
        return updated_user_id


async def activate_user(user_id_or_email: Union[UUID, EmailStr], db) -> UUID:
    async with db.begin():
        user_crud = UserCRUD(db)
        if isinstance(user_id_or_email, UUID):
            user_id = await user_crud.activate(user_id=user_id_or_email)
        else:
            user_id = await user_crud.activate(user_email=user_id_or_email)
        return user_id


async def deactivate_user(user_id_or_email: Union[UUID, EmailStr], db) -> UUID:
    async with db.begin():
        user_crud = UserCRUD(db)
        if isinstance(user_id_or_email, UUID):
            user_id = await user_crud.deactivate(user_id=user_id_or_email)
        else:
            user_id = await user_crud.deactivate(user_email=user_id_or_email)
        return user_id


async def delete_user(user_id_or_email: Union[UUID, EmailStr], db) -> UUID:
    async with db.begin():
        user_crud = UserCRUD(db)
        if isinstance(user_id_or_email, UUID):
            user_id = await user_crud.delete(user_id=user_id_or_email)
        else:
            user_id = await user_crud.delete(user_email=user_id_or_email)
        return user_id


async def check_email_exists(email: str, db) -> bool:
    async with db.begin():
        user_crud = UserCRUD(db)
        result = await user_crud.exists_by_email(email=email)
        exists: bool = result["anon_1"]
        return exists
