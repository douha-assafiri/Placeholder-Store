from database import Base, engine, LocalSession
from initial_data import add_initial_data
from routes import accounts, health, orders, places

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(engine)
with LocalSession() as db:
    add_initial_data(db)

# Proxy strips /api
app = FastAPI(docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")

# Type checker did not like this here, it *is* correct
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router)
app.include_router(orders.router)
app.include_router(places.router)
app.include_router(health.router)
