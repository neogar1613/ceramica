import uvicorn
from fastapi import FastAPI, status, APIRouter
from api.handlers import user_router
from utils.custom_middlewares import catch_exceptions_middleware


app = FastAPI(title='Ceramica API', version='0.0.2')


@app.get("/")
def root():
    return status.HTTP_200_OK

router = APIRouter()

router.include_router(user_router, prefix="/user", tags=["user"])

# Кастомные middlewares
app.middleware('http')(catch_exceptions_middleware)
app.include_router(router)


# alembic init migrations
# alembic.ini --> sqlalchemy.url = postgresql://postgres:postgres@0.0.0.0:5433/postgres
# migrations/env.py --> from main import Base target_metadata = Base.metadata
# alembic revision --autogenerate -m 'create user tables'
# alembic upgrade heads
if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
