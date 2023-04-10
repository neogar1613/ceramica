from fastapi import FastAPI, status
import uvicorn
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from settings import REAL_DATABASE_URL


engine = create_async_engine(REAL_DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
base = declarative_base()




app = FastAPI()

@app.get("/")
def root():
    return status.HTTP_200_OK