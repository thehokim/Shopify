from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Product, ProductImage, ProductAttributeValue, User, UserRole
from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductImageResponse
)
from app.auth import get_current_user, get_tenant_owner
from app.services.elasticsearch_service import es_service
from app.services.redis_service import redis_service

router = APIRouter()


def check_tenant_access(user: User, tenant_id: int):
    """Check if user has access to tenant"""
    if user.role == UserRole.SUPER_ADMIN:
        return True
    if user.role in [UserRole.TENANT_OWNER, UserRole.TENANT_STAFF]:
        if user.tenant_id == tenant_id:
            return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions"
    )


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_tenant_owner)
):
    """Create new product"""
    
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any tenant"
        )
    
    # Check if SKU is unique
    existing_product = db.query(Product).filter(Product.sku == product_data.sku).first()
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists"
        )
    
    # Create product
    new_product = Product(
        tenant_id=current_user.tenant_id,
        category_id=product_data.category_id,
        name=product_data.name,
        slug=product_data.slug,
        description=product_data.description,
        short_description=product_data.short_description,
        sku=product_data.sku,
        base_price=product_data.base_price,
        discount_price=product_data.discount_price,
        cost_price=product_data.cost_price,
        stock_quantity=product_data.stock_quantity,
        low_stock_threshold=product_data.low_stock_threshold,
        track_inventory=product_data.track_inventory,
        status=product_data.status,
        is_featured=product_data.is_featured
    )
    
    db.add(new_product)
    db.flush()
    
    # Add images
    if product_data.images:
        for img_data in product_data.images:
            image = ProductImage(
                product_id=new_product.id,
                image_url=img_data.image_url,
                alt_text=img_data.alt_text,
                is_primary=img_data.is_primary,
                sort_order=img_data.sort_order
            )
            db.add(image)
    
    # Add attribute values
    if product_data.attributes:
        for attr_data in product_data.attributes:
            attr_value = ProductAttributeValue(
                product_id=new_product.id,
                attribute_id=attr_data.attribute_id,
                value=attr_data.value
            )
            db.add(attr_value)
    
    db.commit()
    db.refresh(new_product)
    
    # Index in Elasticsearch
    if new_product.status.value == "active":
        _index_product_to_elasticsearch(new_product, db)
    
    # Clear cache
    redis_service.flush_pattern(f"products:tenant:{current_user.tenant_id}:*")
    
    return new_product


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    tenant_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    # АВТОРИЗАЦИЯ УДАЛЕНА. ЭНДПОИНТ ТЕПЕРЬ ПУБЛИЧНЫЙ.
    # current_user: User = Depends(get_current_user)
):
    """List products (PUBLIC)"""
    
    # Build query
    query = db.query(Product)
    
    # Public access can filter by tenant_id
    if tenant_id:
        query = query.filter(Product.tenant_id == tenant_id)
        
    # Дополнительная фильтрация (например, показ только "активных" продуктов для публики)
    # Это важно для публичного эндпоинта.
    if status:
        query = query.filter(Product.status == status)
    else:
        # По умолчанию показывать только активные продукты, если статус не указан
        # Если вы хотите показывать все, удалите этот блок else
        query = query.filter(Product.status == "active")

    # Filter by category
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db)
    # Здесь авторизация уже отсутствовала
):
    """Get product by ID (PUBLIC)"""
    
    # Try cache first
    cache_key = f"product:{product_id}"
    cached = redis_service.get(cache_key)
    if cached:
        # Убедитесь, что кешированный продукт активен, если это публичный доступ.
        # В данном случае предполагаем, что в кеше только активные продукты.
        return cached
    
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Если публичный доступ, возможно, стоит запретить просмотр неактивных продуктов
    if product.status.value != "active":
         raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found" # Или "Product is not available"
        )
    
    # Increment views
    product.views_count += 1
    db.commit()
    
    # Cache for 1 hour
    product_dict = ProductResponse.from_orm(product).dict()
    redis_service.set(cache_key, product_dict, expire=3600)
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_tenant_owner)
):
    """Update product"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check access
    check_tenant_access(current_user, product.tenant_id)
    
    # Update fields
    update_data = product_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    # Update in Elasticsearch
    if product.status.value == "active":
        _index_product_to_elasticsearch(product, db)
    else:
        es_service.delete_product(product.id)
    
    # Clear cache
    redis_service.delete(f"product:{product_id}")
    redis_service.flush_pattern(f"products:tenant:{product.tenant_id}:*")
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_tenant_owner)
):
    """Delete product"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check access
    check_tenant_access(current_user, product.tenant_id)
    
    # Delete from Elasticsearch
    es_service.delete_product(product.id)
    
    # Delete from database
    db.delete(product)
    db.commit()
    
    # Clear cache
    redis_service.delete(f"product:{product_id}")
    redis_service.flush_pattern(f"products:tenant:{product.tenant_id}:*")
    
    return None


def _index_product_to_elasticsearch(product: Product, db: Session):
    """Helper function to index product to Elasticsearch"""
    
    # Get category name
    category_name = product.category.name if product.category else ""
    
    # Get attributes
    attributes = []
    for attr_val in product.attribute_values:
        attributes.append({
            "name": attr_val.attribute.name,
            "value": attr_val.value
        })
    
    # Prepare document
    doc = {
        "id": product.id,
        "tenant_id": product.tenant_id,
        "name": product.name,
        "description": product.description,
        "short_description": product.short_description,
        "category_name": category_name,
        "category_id": product.category_id,
        "base_price": product.base_price,
        "discount_price": product.discount_price,
        "sku": product.sku,
        "status": product.status.value,
        "is_featured": product.is_featured,
        "stock_quantity": product.stock_quantity,
        "attributes": attributes,
        "created_at": product.created_at.isoformat(),
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        "views_count": product.views_count,
        "sales_count": product.sales_count,
        "wishlist_count": product.wishlist_count
    }
    
    # Index to Elasticsearch
    es_service.index_product(doc)