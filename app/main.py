from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import connect_to_mongo, close_mongo_connection
from app.api import auth, students, wallet, savings_ml, admin # Import your routers

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(lifespan=lifespan, title="E-Wallet API", version="0.1.0")

app.include_router(auth.router)
app.include_router(students.router)
# app.include_router(wallet.router)
# app.include_router(savings_ml.router)
# app.include_router(admin.router) # Uncomment when admin is ready
