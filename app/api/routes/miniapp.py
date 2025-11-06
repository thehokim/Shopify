"""
Telegram Mini App API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import hmac
import hashlib
import json
from urllib.parse import parse_qs

from app.database import get_db
from app.models import Product, Order
from app.config import settings

router = APIRouter(prefix="/miniapp", tags=["Telegram Mini App"])


def verify_telegram_webapp_data(init_data: str) -> dict:
    """Verify Telegram WebApp data"""
    try:
        parsed_data = parse_qs(init_data)
        hash_value = parsed_data.get('hash', [''])[0]
        
        # Remove hash from data
        data_check_string = '\n'.join([
            f"{k}={v[0]}" for k, v in sorted(parsed_data.items()) 
            if k != 'hash'
        ])
        
        # Calculate hash
        secret_key = hmac.new(
            "WebAppData".encode(),
            settings.TELEGRAM_BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if calculated_hash != hash_value:
            raise HTTPException(status_code=401, detail="Invalid data")
        
        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/products")
async def get_products(
    category: str = None,
    search: str = None,
    db: Session = Depends(get_db)
):
    """Get products for Mini App"""
    query = db.query(Product).filter(Product.is_active == True)
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    products = query.limit(50).all()
    
    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "price": float(p.price),
                "image": p.image_url,
                "category": p.category
            }
            for p in products
        ]
    }


@router.post("/orders")
async def create_order_from_miniapp(
    order_data: dict,
    init_data: str,
    db: Session = Depends(get_db)
):
    """Create order from Telegram Mini App"""
    # Verify Telegram data
    telegram_data = verify_telegram_webapp_data(init_data)
    
    user_data = json.loads(telegram_data.get('user', ['{}'])[0])
    telegram_id = user_data.get('id')
    
    # Create order
    order = Order(
        telegram_id=telegram_id,
        items=order_data.get('items'),
        total=order_data.get('total'),
        status='pending'
    )
    
    db.add(order)
    db.commit()
    
    return {"order_id": order.id, "status": "success"}
