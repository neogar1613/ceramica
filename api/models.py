import re
import uuid
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, validator



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
