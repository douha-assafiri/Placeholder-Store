from fastapi import APIRouter, HTTPException, Response, status

from helpers import DB, CurrentUser, Admin, logger
from models import Order, OrderItem, Place
from schemas import OrderRequest, OrderResponse, OrderStatusUpdate

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

@router.post("", responses={
    404: {"description": "Place not found"},
    409: {"description": "Not enough in stock"},
})
async def create_order(new_order: OrderRequest, db: DB, current_user: CurrentUser):
    logger.debug(f"Creating order: {new_order.model_dump()}")
    items = []
    for item in new_order.items:
        place = db.query(Place).filter(Place.id == item.place_id).first()
        if place is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
        # Untracked quantities never run out
        if place.quantity is not None:
            if place.quantity < item.quantity:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Not enough {place.name} in stock")
            place.quantity -= item.quantity
            place.stock = place.quantity > 0
        items.append(OrderItem(place_id=place.id, name=place.name, quantity=item.quantity, price=place.price))

    order = Order(
        owner=current_user.id,
        price=sum(item.price * item.quantity for item in items),
        items=items,
        first_name=new_order.first_name,
        last_name=new_order.last_name,
        email=new_order.email,
        street=new_order.street,
        city=new_order.city,
        state=new_order.state,
        postcode=new_order.postcode,
        country=new_order.country,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return Response(status_code=status.HTTP_201_CREATED, content=OrderResponse.model_validate(order).model_dump_json(),
                    media_type="application/json")


@router.get("", response_model=list[OrderResponse])
async def view_all_orders(_user: Admin, db: DB):
    return db.query(Order).order_by(Order.id.desc()).all()


@router.patch("/{order_id}/status", response_model=OrderResponse,
              responses={404: {"description": "No order with that id"}})
async def update_order_status(order_id: int, update: OrderStatusUpdate,
                              user: Admin,
                              db: DB):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No order with that id")
    order.status = update.status
    db.commit()
    db.refresh(order)
    logger.info(f"User: {user.email} set order {order_id} to {update.status.value}")
    return order
