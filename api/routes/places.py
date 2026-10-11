from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session

from helpers import get_db, require_admin, logger
from models import Place, User
from schemas import PlacesFilterRequest, \
    PlaceResponse, CreatePlace

router = APIRouter(
    prefix="/places",
    tags=["places"],
)


# The empty path means it just goes to the prefix above, I.e. places
@router.get("", response_model=list[PlaceResponse])
async def get_places_filter(filters: PlacesFilterRequest = Depends(), db: Session = Depends(get_db)):
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

    return query.all()


@router.get("/{place_id}", response_model=PlaceResponse)
async def get_place(place_id: int, db: Session = Depends(get_db)):
    return db.query(Place).filter(Place.id == place_id).first()


@router.post("")
async def create_place(new_place: CreatePlace,
                       db: Session = Depends(get_db),
                       user: User = Depends(require_admin)):
    place = Place(
        name=new_place.name,
        description=new_place.description,
        image_path=new_place.image_path,
        stock=new_place.stock,
        price=new_place.price
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    logger.info(f"User: {user.email} created place: {new_place.name}")
    return Response(status_code=status.HTTP_201_CREATED, content=f"Place: {new_place.name} created")


@router.delete("/{place_id}")
async def delete_place(place_id: int, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    place = db.query(Place).filter(Place.id == place_id).first()
    try:
        db.delete(place)
        db.commit()
    except InvalidRequestError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No place with that id")
    logger.info(f"User: {user.email} deleted place: {place_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT, content=f"Place: {place_id} deleted")
