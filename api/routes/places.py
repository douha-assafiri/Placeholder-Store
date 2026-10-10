from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from helpers import get_db, require_admin, logger
from models import Place, User
from schemas import PlacesResponse, PlacesFilterRequest, \
    PlaceResponse, CreatePlace

router = APIRouter(
    prefix="/places",
    tags=["places"],
)


# The empty path means it just goes to the prefix above, I.e places
@router.get("", response_model=PlacesResponse)
async def get_places_filter(filters: PlacesFilterRequest, db: Session = Depends(get_db)):
    #https://stackoverflow.com/questions/31063860/conditionally-filtering-in-sqlalchemy
    query = db.query(Place)

    if filters.name is not None:
        query = query.filter(Place.name.ilike(f"%{filters.name}%"))
    if filters.description is not None:
        query = query.filter(Place.description.ilike(f"%{filters.description}%"))
    if filters.stock is not None:
        query = query.filter(Place.stock == filters.stock)
    if filters.price_min is not None:
        query = query.filter(Place.price >= filters.price_min)
    if filters.price_min is not None:
        query = query.filter(Place.price <= filters.price_max)

    return PlaceResponse(places=query.all())


@router.get("/{place_id}", response_model=PlaceResponse)
async def get_place(place_id: int, db: Session = Depends(get_db)):
    return db.query(Place).filter(Place.id == place_id).first()


@router.post("")
async def create_place(newPlace: CreatePlace,
                       db: Session = Depends(get_db),
                       user: User = require_admin()):
    db.add(Place(
        name=newPlace.name,
        description=newPlace.description,
        image_path=newPlace.image_path,
        stock=newPlace.stock,
        price=newPlace.price
    ))
    db.commit()
    db.refresh(newPlace)
    logger.info(f"User: {user.email} created place: {newPlace.name}")
    return Response(status_code=status.HTTP_200_OK, content=newPlace.model_dump())


@router.delete("/{place_id}")
async def delete_place(place_id: int, user=require_admin(), db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    db.delete(place)
    db.commit()
    db.refresh(place)
    logger.info(f"User: {user.email} deleted place: {place_id}")
    return Response(status_code=status.HTTP_200_OK, content=f"Place: {place_id} deleted")
