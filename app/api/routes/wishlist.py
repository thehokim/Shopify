from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Wishlist, User, Product
from app.schemas import WishlistCreate, WishlistResponse
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    wishlist_data: WishlistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add product to wishlist"""
    
    # Check if product exists
    product = db.query(Product).filter(Product.id == wishlist_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if already in wishlist
    existing = (
        db.query(Wishlist)
        .filter(
            Wishlist.customer_id == current_user.id,
            Wishlist.product_id == wishlist_data.product_id
        )
        .first()
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already in wishlist"
        )
    
    # Add to wishlist
    wishlist_item = Wishlist(
        customer_id=current_user.id,
        product_id=wishlist_data.product_id
    )
    
    db.add(wishlist_item)
    
    # Increment product wishlist count
    product.wishlist_count += 1
    
    db.commit()
    db.refresh(wishlist_item)
    
    return wishlist_item


@router.get("/", response_model=List[WishlistResponse])
async def get_wishlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's wishlist"""
    items = (
        db.query(Wishlist)
        .filter(Wishlist.customer_id == current_user.id)
        .all()
    )
    return items


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove product from wishlist"""
    wishlist_item = (
        db.query(Wishlist)
        .filter(
            Wishlist.customer_id == current_user.id,
            Wishlist.product_id == product_id
        )
        .first()
    )
    
    if not wishlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not in wishlist"
        )
    
    # Decrement product wishlist count
    product = db.query(Product).filter(Product.id == product_id).first()
    if product and product.wishlist_count > 0:
        product.wishlist_count -= 1
    
    db.delete(wishlist_item)
    db.commit()
    
    return None
