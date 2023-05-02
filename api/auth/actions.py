from datetime import datetime, timedelta
from typing import Union, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import UserCRUD
from db.models import User
from db.session import get_db
from settings import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_SECRET_KEY, JWT_ALGORITHM
from utils.hashing import Hasher


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/get_token")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def _get_user_by_email_for_auth(email: Optional[str] = None,
                                      user_id: Optional[str] = None,
                                      db: AsyncSession = None):
    async with db.begin():
        crud = UserCRUD(db)
        if user_id:
            return await crud.get_by_id_or_email(user_id=user_id)
        elif email:
            return await crud.get_by_id_or_email(user_email=email)
        return None


async def authenticate_user(email: str, password: str, db: AsyncSession) -> Union[User, None]:
    user = await _get_user_by_email_for_auth(email=email, db=db)
    if user is None:
        return None
    if not Hasher.verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user_from_token(token: str = Depends(oauth2_scheme),
                                      db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await _get_user_by_email_for_auth(user_id=user_id, session=db)
    if user is None:
        raise credentials_exception
    return user
