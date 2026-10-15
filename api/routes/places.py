from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import InvalidRequestError

from helpers import DB, Admin, logger
from models import Place
from schemas import PlacesFilterRequest, \
    PlaceResponse, CreatePlace, UpdatePlace

PLACE_NOT_FOUND = "No place with that id"

router = APIRouter(
    prefix="/places",
    tags=["places"],
)


# The empty path means it just goes to the prefix above, I.e. places
@router.get("", response_model=list[PlaceResponse])
async def get_places_filter(filters: Annotated[PlacesFilterRequest, Depends()], db: DB):
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
    if filters.price_max is not None:
        query = query.filter(Place.price <= filters.price_max)
    if filters.category is not None:
        query = query.filter(Place.category == filters.category)

    return query.all()


@router.get("/{place_id}", response_model=PlaceResponse, responses={404: {"description": PLACE_NOT_FOUND}})
async def get_place(place_id: int, db: DB):
    place = db.query(Place).filter(Place.id == place_id).first()
    if place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PLACE_NOT_FOUND)
    return place


@router.post("")
async def create_place(new_place: CreatePlace,
                       db: DB,
                       user: Admin):
    place = Place(
        name=new_place.name,
        description=new_place.description,
        image_path=new_place.image_path,
        stock=new_place.stock if new_place.quantity is None else new_place.quantity > 0,
        price=new_place.price,
        category=new_place.category,
        rating=new_place.rating,
        old_price=new_place.old_price,
        tag=new_place.tag,
        quantity=new_place.quantity,
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    logger.info(f"User: {user.email} created place: {new_place.name}")
    return Response(status_code=status.HTTP_201_CREATED, content=f"Place: {new_place.name} created")


@router.patch("/{place_id}", response_model=PlaceResponse, responses={404: {"description": PLACE_NOT_FOUND}})
async def update_place(place_id: int, changes: UpdatePlace,
                       user: Admin,
                       db: DB):
    place = db.query(Place).filter(Place.id == place_id).first()
    if place is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PLACE_NOT_FOUND)
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(place, field, value)
    if place.quantity is not None:
        place.stock = place.quantity > 0
    db.commit()
    db.refresh(place)
    logger.info(f"User: {user.email} updated place: {place_id}")
    return place


@router.delete("/{place_id}", responses={404: {"description": PLACE_NOT_FOUND}})
async def delete_place(place_id: int, user: Admin, db: DB):
    place = db.query(Place).filter(Place.id == place_id).first()
    try:
        db.delete(place)
        db.commit()
    except InvalidRequestError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PLACE_NOT_FOUND)
    logger.info(f"User: {user.email} deleted place: {place_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT) # 204 must not have a body
