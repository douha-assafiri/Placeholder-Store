from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine, LocalSession
from initial_data import add_initial_data
from routes import accounts, health, orders, places

Base.metadata.create_all(engine)
with LocalSession() as db:
    add_initial_data(db)

# For the load balancer's /api rule
app = FastAPI(docs_url="/api/docs", redoc_url="/api/redoc", openapi_url="/api/openapi.json")

# Type checker did not like this here, it *is* correct
# noinspection PyTypeChecker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(places.router, prefix="/api")
app.include_router(health.router, prefix="/api")