from fastapi import APIRouter
from api.models import UserCreate, GetUser
from db.session import async_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.crud import UserCRUD
from db.session import get_db


user_router = APIRouter()

async def _create_new_user(data: UserCreate, db) -> GetUser:
    async with db as session:
        async with session.begin():
            user_crud = UserCRUD(session)
            user = await user_crud.create(username=data.username,
                                          name=data.name,
                                          surname=data.surname,
                                          email=data.email,)
            return GetUser(user_id=user.user_id,
                           username=user.username,
                           name=user.name,
                           surname=user.surname,
                           email=user.email,
                           is_active=user.is_active,)


async def _check_exists_by_email(email: str, db) -> bool:
    async with db as session:
        async with session.begin():
            user_crud = UserCRUD(session)
            result = await user_crud.user_exists(email=email)
            is_exists: bool = result["anon_1"]
            return is_exists


@user_router.post("/create", response_model=GetUser)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await _create_new_user(data=data, db=db)

@user_router.post("/check_exists")
async def check_email_exists(email: str, db: AsyncSession = Depends(get_db)):
    return await _check_exists_by_email(email=email, db=db)
