import re
import uuid
from fastapi import HTTPException, status
from pydantic import (
    BaseModel,
    EmailStr,
    validator,
    constr
)
from typing import Optional


LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z0-9\-]+$")


class DefaultModel(BaseModel):
    """ Общий конфиг для всех моделей """
    class Config:
        orm_mode = True # Всё к JSON


class GetUser(DefaultModel):
    user_id: uuid.UUID
    username: str
    name: str
    surname: str
    email: EmailStr
    is_active: bool


class UserCreate(BaseModel):
    username: str
    name: str
    surname: str
    email: EmailStr

    @validator("username")
    def username_valid(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Имя пользователя может содержать только буквы")
        return value

    @validator("name")
    def name_valid(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Имя может содержать только буквы")
        return value

    @validator("surname")
    def surname_valid(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Фамилия может содержать только буквы")
        return value


class DeleteUserResponse(BaseModel):
    deleted_user_id: uuid.UUID


class UpdatedUserResponse(BaseModel):
    updated_user_id: uuid.UUID


class UserUpdate(BaseModel):
    name: Optional[constr(min_length=1)]
    surname: Optional[constr(min_length=1)]
    email: Optional[EmailStr]

    @validator("name")
    def validate_name(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(status_code=422,
                                detail="Name should contains only letters")
        return value

    @validator("surname")
    def validate_surname(cls, value):
        if not LETTER_MATCH_PATTERN.match(value):
            raise HTTPException(status_code=422,
                                detail="Surname should contains only letters")
        return value


class Token(BaseModel):
    access_token: str
    token_type: str
