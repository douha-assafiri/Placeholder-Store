from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from helpers import DB, logger

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("", responses={503: {"description": "Database unavailable"}})
async def health(db: DB):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Health check: database unavailable")
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            content={"status": "error", "database": "unavailable"})
    return {"status": "ok", "database": "ok"}


@router.get("/live")
async def liveness():
    return {"status": "ok"}


@router.get("/ready", responses={503: {"description": "Database unavailable"}})
async def readiness(db: DB):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Readiness check: database unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"status": "degraded", "database": "unavailable"},
        )
    return {"status": "ok", "database": "ok"}
