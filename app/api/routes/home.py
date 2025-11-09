from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Product
from app.models import Category
from app.models import Order, OrderItem
from app.schemas import ProductResponse
from app.schemas import CategoryResponse

router = APIRouter(prefix="/home", tags=["Home Page"])


@router.get("", response_model=Dict[str, Any])
async def get_homepage_data(
    featured_limit: int = Query(default=8, ge=1, le=50),
    new_arrivals_limit: int = Query(default=8, ge=1, le=50),
    best_sellers_limit: int = Query(default=8, ge=1, le=50),
    deals_limit: int = Query(default=8, ge=1, le=50),
    categories_limit: int = Query(default=6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    🏠 Получить все данные для главной страницы одним запросом
    
    Возвращает:
    - featured_products: Популярные товары
    - new_arrivals: Новые поступления
    - best_sellers: Бестселлеры
    - discounted_products: Товары со скидками
    - categories: Популярные категории
    - banners: Баннеры для слайдера
    - stats: Статистика магазина
    """
    
    # 🌟 Featured Products - по рейтингу
    featured_products = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.stock > 0)
        .order_by(desc(Product.rating))
        .limit(featured_limit)
        .all()
    )
    
    # 🆕 New Arrivals - последние 30 дней
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_arrivals = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.stock > 0)
        .filter(Product.created_at >= thirty_days_ago)
        .order_by(desc(Product.created_at))
        .limit(new_arrivals_limit)
        .all()
    )
    
    # 🔥 Best Sellers - с наибольшим количеством продаж
    best_sellers_query = (
        db.query(
            Product,
            func.count(OrderItem.id).label('order_count')
        )
        .join(OrderItem, Product.id == OrderItem.product_id, isouter=True)
        .filter(Product.is_active == True)
        .filter(Product.stock > 0)
        .group_by(Product.id)
        .order_by(desc('order_count'))
        .limit(best_sellers_limit)
        .all()
    )
    best_sellers = [product for product, _ in best_sellers_query]
    
    # 💰 Discounted Products - со скидками
    discounted_products = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.stock > 0)
        .filter(Product.discount_price.isnot(None))
        .filter(Product.discount_price < Product.price)
        .order_by(desc((Product.price - Product.discount_price) / Product.price))
        .limit(deals_limit)
        .all()
    )
    
    # 📁 Popular Categories
    categories_query = (
        db.query(
            Category,
            func.count(Product.id).label('product_count')
        )
        .join(Product, Category.id == Product.category_id, isouter=True)
        .filter(Product.is_active == True)
        .group_by(Category.id)
        .order_by(desc('product_count'))
        .limit(categories_limit)
        .all()
    )
    categories = [category for category, _ in categories_query]
    
    # 📊 Stats
    total_products = db.query(func.count(Product.id)).filter(
        Product.is_active == True,
        Product.stock > 0
    ).scalar() or 0
    
    total_categories = db.query(func.count(Category.id)).scalar() or 0
    
    active_deals = db.query(func.count(Product.id)).filter(
        Product.is_active == True,
        Product.discount_price.isnot(None),
        Product.discount_price < Product.price
    ).scalar() or 0
    
    # 🎨 Banners
    banners = [
        {
            "id": 1,
            "title": "Летняя распродажа",
            "subtitle": "Скидки до 50% на избранные товары",
            "image_url": "/banners/summer-sale.jpg",
            "link": "/category/summer-collection",
            "button_text": "Смотреть товары"
        },
        {
            "id": 2,
            "title": "Новая коллекция",
            "subtitle": "Откройте для себя последние тренды",
            "image_url": "/banners/new-collection.jpg",
            "link": "/new-arrivals",
            "button_text": "Узнать больше"
        },
        {
            "id": 3,
            "title": "Бесплатная доставка",
            "subtitle": "При заказе от $50",
            "image_url": "/banners/free-shipping.jpg",
            "link": "/products",
            "button_text": "Начать покупки"
        }
    ]
    
    return {
        "featured_products": [ProductResponse.from_orm(p) for p in featured_products],
        "new_arrivals": [ProductResponse.from_orm(p) for p in new_arrivals],
        "best_sellers": [ProductResponse.from_orm(p) for p in best_sellers],
        "discounted_products": [ProductResponse.from_orm(p) for p in discounted_products],
        "categories": [CategoryResponse.from_orm(c) for c in categories],
        "banners": banners,
        "stats": {
            "total_products": total_products,
            "total_categories": total_categories,
            "active_deals": active_deals,
            "new_arrivals_count": len(new_arrivals)
        }
    }


# Оставляем отдельные endpoints для гибкости
@router.get("/featured-products", response_model=List[ProductResponse])
async def get_featured_products(
    limit: int = Query(default=8, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """🌟 Получить только популярные товары"""
    products = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.stock > 0)
        .order_by(desc(Product.rating))
        .limit(limit)
        .all()
    )
    return products
