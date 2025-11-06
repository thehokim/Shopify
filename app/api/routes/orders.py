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
        status=OrderStatus.PENDING,
        payment_status="pending"
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
    
    # 🔥 TRIGGER ASYNC TASKS
    try:
        from app.tasks.order_tasks import process_new_order
        process_new_order.delay(new_order.id)
    except Exception as e:
        # Log error but don't fail the order creation
        print(f"Failed to trigger order processing task: {e}")
    
    return new_order


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = 0,
    limit: int = 50,
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List user's orders"""
    query = db.query(Order).filter(Order.customer_id == current_user.id)
    
    # Filter by status if provided
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    orders = (
        query
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


@router.patch("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel an order (customer can only cancel pending orders)"""
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
    
    # Only pending orders can be cancelled
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status: {order.status}"
        )
    
    # Update status
    order.status = OrderStatus.CANCELLED
    
    # Restore product stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product and product.track_inventory:
            product.stock_quantity += item.quantity
            product.sales_count -= item.quantity
    
    db.commit()
    
    # 🔥 Send cancellation notification
    try:
        from app.tasks.email_tasks import send_order_cancelled
        send_order_cancelled.delay(order.id)
    except Exception as e:
        print(f"Failed to send cancellation email: {e}")
    
    return {
        "message": "Order cancelled successfully",
        "order_id": order.id,
        "order_number": order.order_number
    }


@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update order status (tenant owner only)"""
    
    # Check if user is tenant owner
    if current_user.role.value != "tenant_owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only shop owners can update order status"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Verify order belongs to owner's tenant
    if order.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this order"
        )
    
    old_status = order.status
    order.status = new_status
    
    # Update payment status if needed
    if new_status == OrderStatus.CONFIRMED:
        order.payment_status = "paid"
    
    db.commit()
    db.refresh(order)
    
    # 🔥 Send status update notification
    try:
        from app.tasks.email_tasks import send_order_status_update
        send_order_status_update.delay(
            order.id,
            order.customer.email,
            new_status.value
        )
    except Exception as e:
        print(f"Failed to send status update email: {e}")
    
    return {
        "message": f"Order status updated from {old_status} to {new_status}",
        "order": order
    }


@router.post("/{order_id}/payment/webhook")
async def payment_webhook(
    order_id: int,
    webhook_data: dict,
    db: Session = Depends(get_db)
):
    """
    Handle payment gateway webhook
    This should be called by payment provider (Stripe, PayPal, Click, Payme)
    """
    
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    payment_status = webhook_data.get('status')
    
    if payment_status == 'success':
        order.status = OrderStatus.CONFIRMED
        order.payment_status = 'paid'
        
        # 🔥 Trigger order confirmation
        try:
            from app.tasks.email_tasks import send_order_confirmation
            from app.tasks.notification_tasks import notify_shop_owner
            
            send_order_confirmation.delay(order.id)
            notify_shop_owner.delay(order.id)
        except Exception as e:
            print(f"Failed to send confirmation: {e}")
    
    elif payment_status == 'failed':
        order.payment_status = 'failed'
    
    db.commit()
    
    return {"status": "processed", "order_id": order.id}


@router.get("/admin/all", response_model=List[OrderResponse])
async def list_all_orders(
    skip: int = 0,
    limit: int = 50,
    status_filter: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all orders for tenant (owner only)"""
    
    if current_user.role.value != "tenant_owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only shop owners can view all orders"
        )
    
    query = db.query(Order).filter(Order.tenant_id == current_user.tenant_id)
    
    if status_filter:
        query = query.filter(Order.status == status_filter)
    
    orders = (
        query
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return orders