from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from settings import DATABASE_URL
from sqlalchemy.orm import sessionmaker, declarative_base


Base = declarative_base()

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    try:
        session: AsyncSession = async_session()
        yield session
    finally:
        await session.close()
