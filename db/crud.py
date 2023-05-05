from typing import Union, Optional
from uuid import UUID
from pydantic import EmailStr
from sqlalchemy import and_, update, delete, select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import User
from api.user.models import UserRoles


class UserCRUD:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db_session = db_session

    async def create(self,
                     username: str,
                     name: str,
                     surname: str,
                     email: str,
                     hashed_password: str) -> User:
        new_user = User(username=username,
                        name=name,
                        surname=surname,
                        email=email,
                        roles=[UserRoles.ROLE_USER, ],
                        hashed_password=hashed_password)
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def get_by_id_or_email(self, user_id: Optional[UUID] = None,
                                 user_email: Optional[EmailStr] = None) -> Union[User, None]:
        if user_id:
            query = select(User).where(User.user_id == user_id)
        elif user_email:
            query = select(User).where(User.email == user_email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]

    async def get_all_users(self, limit: int, offset: int) -> Union[list[User], None]:
        query = select(User).limit(limit).offset(offset)
        res = await self.db_session.execute(query)
        user_rows = res.fetchall()
        return user_rows

    async def update(self, user_id: UUID, **kwargs) -> Union[UUID, None]:
        query = (update(User)
                 .where(and_(User.user_id == user_id, User.is_active == True))
                 .values(kwargs)
                 .returning(User.user_id))
        res = await self.db_session.execute(query)
        update_user_id_row = res.fetchone()
        if update_user_id_row is not None:
            return update_user_id_row[0]

    async def activate(self, user_id: Optional[UUID] = None,
                       user_email: Optional[EmailStr] = None ) -> Union[UUID, None]:
        if user_id:
            query = (update(User)
                    .where(and_(User.user_id == user_id, User.is_active == False))
                    .values(is_active=True)
                    .returning(User.user_id))
        elif user_email:
            query = (update(User)
                    .where(and_(User.email == user_email, User.is_active == False))
                    .values(is_active=True)
                    .returning(User.user_id))
        res = await self.db_session.execute(query)
        user_id_row = res.fetchone()
        if user_id_row is not None:
            return user_id_row[0]

    async def deactivate(self, user_id: Optional[UUID] = None,
                         user_email: Optional[EmailStr] = None ) -> Union[UUID, None]:
        if user_id:
            query = (update(User)
                    .where(and_(User.user_id == user_id, User.is_active == True))
                    .values(is_active=False)
                    .returning(User.user_id))
        elif user_email:
            query = (update(User)
                    .where(and_(User.email == user_email, User.is_active == True))
                    .values(is_active=False)
                    .returning(User.user_id))
        res = await self.db_session.execute(query)
        user_id_row = res.fetchone()
        if user_id_row is not None:
            return user_id_row[0]

    async def delete(self, user_id: Optional[UUID] = None,
                     user_email: Optional[EmailStr] = None ) -> Union[UUID, None]:
        if user_id:
            query = (delete(User)
                    .where(User.user_id == user_id)
                    .returning(User.user_id))
        elif user_email:
            query = (delete(User)
                    .where(User.email == user_email)
                    .returning(User.user_id))
        res = await self.db_session.execute(query)
        user_id_row = res.fetchone()
        if user_id_row is not None:
            return user_id_row[0]

    async def exists_by_email(self, email: str) -> bool:
        query = exists(User).where(User.email == email).select()
        res = await self.db_session.execute(query)
        row = res.fetchone()
        return row
