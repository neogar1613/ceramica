from fastapi import FastAPI, status, HTTPException, APIRouter
from pydantic import BaseModel, EmailStr, validator
import re
from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, declarative_base
import uuid
import uvicorn

from settings import DATABASE_URL


# DB connection
engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# DB models layer
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)

# DB interaction layer
class UserCRUD:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(self, username: str, name: str, surname: str, email: str) -> User:
        new_user = User(username=username, name=name, surname=surname, email=email,)
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user


# API models layer
LETTER_MATCH_PATTERN = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")

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


# API routes

app = FastAPI()
user_router = APIRouter()

@app.get("/")
def root():
    return status.HTTP_200_OK


async def _create_new_user(data: UserCreate) -> GetUser:
    async with async_session() as session:
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


@user_router.post("/create", response_model=GetUser)
async def create_user(data: UserCreate):
    return await _create_new_user(data=data)


router = APIRouter()

router.include_router(user_router, prefix="/user", tags=["user"])

app.include_router(router)


# alembic init migrations
# alembic.ini --> sqlalchemy.url = postgresql://postgres:postgres@0.0.0.0:5433/postgres
# migrations/env.py --> from main import Base target_metadata = Base.metadata
# alembic revision --autogenerate -m 'create user tables'
# alembic upgrade heads
if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
