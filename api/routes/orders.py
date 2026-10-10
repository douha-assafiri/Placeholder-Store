from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from helpers import get_db, require_admin, logger, get_current_user, lookup_price
from models import User, Order
from schemas import OrderRequest

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)

@router.post("")
async def create_order(newOrder: OrderRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logger.debug(f"Creating order: {newOrder.model_dump()}")
    order = Order(
        owner=current_user.id,
        place_id=newOrder.place_id,
        price=lookup_price(newOrder.place_id, db),
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return Response(status_code=status.HTTP_201_CREATED, content=f"Created order {order.place_id} at price {order.price}")