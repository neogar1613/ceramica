from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from api.auth.models import Token
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from api.auth.actions import authenticate_user, create_access_token


auth_router = APIRouter()


@auth_router.post("/get_token", response_model=Token)
async def get_tokens_handler(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(email=form_data.username, password=form_data.password, db=db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": str(user.user_id), "custom_data": "FHRETEB67EnneE"})
    return Token(access_token=access_token, refresh_token=access_token, token_type="bearer")
