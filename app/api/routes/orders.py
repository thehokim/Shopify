from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from app.database import get_db
from app.models import Order, OrderItem, User, Product, CartItem, OrderStatus
from app.schemas import OrderCreate, OrderResponse
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new order from cart or direct items"""
    
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a tenant"
        )
    
    # Calculate totals
    subtotal = 0
    order_items = []
    
    for item_data in order_data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {item_data.product_id} not found"
            )
        
        # Check stock
        if product.track_inventory and product.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product.name}"
            )
        
        unit_price = product.discount_price or product.base_price
        total_price = unit_price * item_data.quantity
        subtotal += total_price
        
        order_items.append({
            "product_id": product.id,
            "product_name": product.name,
            "variant_id": item_data.variant_id,
            "quantity": item_data.quantity,
            "unit_price": unit_price,
            "total_price": total_price,
            "product_attributes": item_data.selected_attributes
        })
    
    # Apply discount if provided
    discount_amount = 0
    if order_data.discount_code:
        # TODO: Validate and apply discount code
        pass
    
    # Calculate shipping and tax
    shipping_cost = 0  # TODO: Calculate based on address
    tax_amount = subtotal * 0.1  # 10% tax (example)
    
    total = subtotal - discount_amount + shipping_cost + tax_amount
    
    # Create order
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    new_order = Order(
        tenant_id=current_user.tenant_id,
        customer_id=current_user.id,
        order_number=order_number,
        subtotal=subtotal,
        discount_amount=discount_amount,
        shipping_cost=shipping_cost,
        tax_amount=tax_amount,
        total=total,
        discount_code=order_data.discount_code,
        shipping_address=order_data.shipping_address,
        billing_address=order_data.billing_address or order_data.shipping_address,
        payment_method=order_data.payment_method,
        notes=order_data.notes,
        status=OrderStatus.PENDING
    )
    
    db.add(new_order)
    db.flush()
    
    # Create order items and update inventory
    for item in order_items:
        order_item = OrderItem(
            order_id=new_order.id,
            **item
        )
        db.add(order_item)
        
        # Update product stock and sales count
        product = db.query(Product).filter(Product.id == item["product_id"]).first()
        if product.track_inventory:
            product.stock_quantity -= item["quantity"]
        product.sales_count += item["quantity"]
    
    # Clear cart
    db.query(CartItem).filter(CartItem.customer_id == current_user.id).delete()
    
    db.commit()
    db.refresh(new_order)
    
    return new_order


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's orders"""
    orders = (
        db.query(Order)
        .filter(Order.customer_id == current_user.id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get order details"""
    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.customer_id == current_user.id
        )
        .first()
    )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order
