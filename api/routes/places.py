from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from helpers import get_db
from models import Place
from schemas import PlacesResponse, PlacesFilterRequest, \
    PlaceResponse

router = APIRouter(
    prefix="/places",
    tags=["places"],
)


# The empty path means it just goes to the prefix above, I.e places
@router.get("", response_model=PlacesResponse)
async def get_places_filter(filters: PlacesFilterRequest , db : Session = Depends(get_db)):
    #https://stackoverflow.com/questions/31063860/conditionally-filtering-in-sqlalchemy
    query = db.query(Place)

    if filters.name is not None:
        query = query.filter(Place.name.ilike(f"%{filters.name}%"))
    if filters.description is not None:
        query = query.filter(Place.description.ilike(f"%{filters.description}%"))
    if filters.stock is not None:
        query = query.filter(Place.stock == filters.stock)
    if filters.price_min is not None:
        query = query.filter(Place.price >= filters.price_min )
    if filters.price_min is not None:
        query = query.filter(Place.price <= filters.price_max )

    return PlaceResponse(places=query.all())