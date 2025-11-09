from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import Product
from app.models import Category
from app.models import Order, OrderItem
from app.schemas import ProductResponse
from app.schemas import CategoryResponse

router = APIRouter(prefix="/home", tags=["Home Page"])


@router.get("/featured-products", response_model=List[ProductResponse])
async def get_featured_products(
    limit: int = Query(default=8, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    🌟 Получить избранные/популярные товары для главной страницы
    
    - Возвращает топ товары по рейтингу и количеству заказов
    """
    products = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.stock > 0)
        .order_by(desc(Product.rating))
        .order_by(desc(Product.created_at))
        .limit(limit)
        .all()
    )
    
    return products


@router.get("/new-arrivals", response_model=List[ProductResponse])
async def get_new_arrivals(
    limit: int = Query(default=8, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    🆕 Получить новые поступления
    
    - Товары добавленные за последние 30 дней
    """
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    products = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.stock > 0)
        .filter(Product.created_at >= thirty_days_ago)
        .order_by(desc(Product.created_at))
        .limit(limit)
        .all()
    )
    
    return products


@router.get("/best-sellers", response_model=List[ProductResponse])
async def get_best_sellers(
    limit: int = Query(default=8, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    🔥 Получить бестселлеры
    
    - Товары с наибольшим количеством продаж
    """
    # Подсчитываем количество заказов для каждого товара
    best_sellers = (
        db.query(
            Product,
            func.count(OrderItem.id).label('order_count')
        )
        .join(OrderItem, Product.id == OrderItem.product_id)
        .join(Order, OrderItem.order_id == Order.id)
        .filter(Product.is_active == True)
        .filter(Product.stock > 0)
        .group_by(Product.id)
        .order_by(desc('order_count'))
        .limit(limit)
        .all()
    )
    
    return [product for product, _ in best_sellers]


@router.get("/discounted-products", response_model=List[ProductResponse])
async def get_discounted_products(
    limit: int = Query(default=8, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    💰 Получить товары со скидками
    
    - Товары у которых discount_price меньше чем price
    """
    products = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.stock > 0)
        .filter(Product.discount_price.isnot(None))
        .filter(Product.discount_price < Product.price)
        .order_by(desc((Product.price - Product.discount_price) / Product.price))
        .limit(limit)
        .all()
    )
    
    return products


@router.get("/categories", response_model=List[CategoryResponse])
async def get_popular_categories(
    limit: int = Query(default=8, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    📁 Получить популярные категории для главной страницы
    
    - Категории с наибольшим количеством активных товаров
    """
    categories = (
        db.query(
            Category,
            func.count(Product.id).label('product_count')
        )
        .join(Product, Category.id == Product.category_id)
        .filter(Product.is_active == True)
        .group_by(Category.id)
        .order_by(desc('product_count'))
        .limit(limit)
        .all()
    )
    
    return [category for category, _ in categories]


@router.get("/trending", response_model=List[ProductResponse])
async def get_trending_products(
    limit: int = Query(default=8, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    📈 Получить трендовые товары
    
    - Товары с наибольшим количеством просмотров за последние 7 дней
    - (если нет системы просмотров, возвращает по рейтингу)
    """
    products = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.stock > 0)
        .order_by(desc(Product.rating))
        .order_by(desc(Product.created_at))
        .limit(limit)
        .all()
    )
    
    return products


@router.get("/flash-deals", response_model=List[ProductResponse])
async def get_flash_deals(
    limit: int = Query(default=4, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    ⚡ Получить флеш-распродажи
    
    - Товары с самыми большими скидками
    """
    products = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.stock > 0)
        .filter(Product.discount_price.isnot(None))
        .filter(Product.discount_price < Product.price)
        .order_by(desc((Product.price - Product.discount_price) / Product.price))
        .limit(limit)
        .all()
    )
    
    return products


@router.get("/recommendations", response_model=List[ProductResponse])
async def get_recommendations(
    limit: int = Query(default=8, ge=1, le=50),
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    💡 Получить рекомендованные товары
    
    - Если указана категория, возвращает товары из этой категории
    - Иначе возвращает случайные популярные товары
    """
    query = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.stock > 0)
    )
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    products = (
        query
        .order_by(desc(Product.rating))
        .order_by(func.random())
        .limit(limit)
        .all()
    )
    
    return products

@router.get("/banners")
async def get_homepage_banners():
    """
    🎨 Получить баннеры для главной страницы
    
    - Временные баннеры (в будущем можно добавить модель Banner)
    """
    return [
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