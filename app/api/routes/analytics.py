from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Product, Order, User, UserRole, Wishlist
from app.schemas import AnalyticsSummary
from app.auth import get_current_user, get_tenant_owner

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_tenant_owner)
):
    """Get analytics summary for tenant"""
    
    if not current_user.tenant_id:
        return {
            "total_products": 0,
            "active_products": 0,
            "total_orders": 0,
            "total_revenue": 0,
            "total_customers": 0,
            "popular_products": [],
            "recent_orders": []
        }
    
    # Total products
    total_products = (
        db.query(func.count(Product.id))
        .filter(Product.tenant_id == current_user.tenant_id)
        .scalar()
    )
    
    # Active products
    active_products = (
        db.query(func.count(Product.id))
        .filter(
            Product.tenant_id == current_user.tenant_id,
            Product.status == "active"
        )
        .scalar()
    )
    
    # Total orders
    total_orders = (
        db.query(func.count(Order.id))
        .filter(Order.tenant_id == current_user.tenant_id)
        .scalar()
    )
    
    # Total revenue
    total_revenue = (
        db.query(func.sum(Order.total))
        .filter(Order.tenant_id == current_user.tenant_id)
        .scalar() or 0
    )
    
    # Total customers
    total_customers = (
        db.query(func.count(func.distinct(Order.customer_id)))
        .filter(Order.tenant_id == current_user.tenant_id)
        .scalar()
    )
    
    # Popular products (by sales)
    popular_products = (
        db.query(
            Product.id,
            Product.name,
            Product.sales_count,
            Product.wishlist_count,
            Product.base_price
        )
        .filter(Product.tenant_id == current_user.tenant_id)
        .order_by(Product.sales_count.desc())
        .limit(10)
        .all()
    )
    
    popular_products_list = [
        {
            "id": p.id,
            "name": p.name,
            "sales_count": p.sales_count,
            "wishlist_count": p.wishlist_count,
            "base_price": p.base_price
        }
        for p in popular_products
    ]
    
    # Recent orders
    recent_orders = (
        db.query(Order)
        .filter(Order.tenant_id == current_user.tenant_id)
        .order_by(Order.created_at.desc())
        .limit(10)
        .all()
    )
    
    recent_orders_list = [
        {
            "id": o.id,
            "order_number": o.order_number,
            "total": o.total,
            "status": o.status.value,
            "created_at": o.created_at.isoformat()
        }
        for o in recent_orders
    ]
    
    return {
        "total_products": total_products,
        "active_products": active_products,
        "total_orders": total_orders,
        "total_revenue": float(total_revenue),
        "total_customers": total_customers,
        "popular_products": popular_products_list,
        "recent_orders": recent_orders_list
    }


@router.get("/products/most-wished")
async def get_most_wished_products(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_tenant_owner)
):
    """Get most wished products"""
    
    products = (
        db.query(Product)
        .filter(Product.tenant_id == current_user.tenant_id)
        .order_by(Product.wishlist_count.desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "wishlist_count": p.wishlist_count,
            "base_price": p.base_price,
            "image_url": p.images[0].image_url if p.images else None
        }
        for p in products
    ]
