from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from api.auth.models import Token
from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional

from db.session import get_db
from api.auth.actions import authenticate_user, create_access_token
from api.auth.exceptions import UserNotExists
from utils.error_handlers import raise_custom_exception


auth_router = APIRouter()

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


@auth_router.post("/get_token", response_model=Token)
async def get_tokens_handler(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(email=form_data.username, password=form_data.password, db=db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": str(user.user_id), "custom_data": "FHRETEB67EnneE"})
    return Token(access_token=access_token, refresh_token=access_token, token_type="bearer")
