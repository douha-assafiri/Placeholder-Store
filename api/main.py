import logging

from database import Base, engine, LocalSession
from initial_data import add_initial_data
from routes import accounts, health, orders, places

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

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

@app.get("/health/live", tags=["health"])
async def liveness():
    return {"status": "ok"}


@app.get("/health/ready", tags=["health"])
async def readiness():
    db = LocalSession()
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok"}
    except SQLAlchemyError:
        logging.getLogger("api").exception("Readiness check failed")
        raise HTTPException(
            status_code=503,
            detail={"status": "degraded", "database": "unavailable"},
        )
    finally:
        db.close()
