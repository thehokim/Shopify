from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Order, User, OrderStatus
from app.schemas import OrderCreate, OrderResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new order"""
    
    # Create order logic...
    new_order = Order(
        tenant_id=order_data.tenant_id,
        user_id=current_user.id,
        status=OrderStatus.PENDING,
        # ... other fields
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    from app.tasks.order_tasks import process_new_order
    process_new_order.delay(new_order.id)
    
    return new_order