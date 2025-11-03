from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import List
import uuid
from pathlib import Path

from app.models import User
from app.auth import get_current_user
from app.services.minio_service import minio_service
from app.config import settings

router = APIRouter()


ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_image(file: UploadFile):
    """Validate uploaded image"""
    # Check extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check content type
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )


@router.post("/product-image")
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload product image to MinIO"""
    
    validate_image(file)
    
    # Generate unique filename
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    
    # Upload to MinIO
    file_url = minio_service.upload_file(
        bucket_name=settings.MINIO_BUCKET_PRODUCTS,
        file=file.file,
        file_name=unique_filename,
        content_type=file.content_type
    )
    
    if not file_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image"
        )
    
    return {
        "url": file_url,
        "filename": unique_filename
    }


@router.post("/product-images")
async def upload_product_images(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload multiple product images"""
    
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 images allowed"
        )
    
    uploaded_files = []
    
    for file in files:
        validate_image(file)
        
        file_ext = Path(file.filename).suffix.lower()
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"
        
        file_url = minio_service.upload_file(
            bucket_name=settings.MINIO_BUCKET_PRODUCTS,
            file=file.file,
            file_name=unique_filename,
            content_type=file.content_type
        )
        
        if file_url:
            uploaded_files.append({
                "url": file_url,
                "filename": unique_filename,
                "original_name": file.filename
            })
    
    return {"files": uploaded_files}


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload user avatar"""
    
    validate_image(file)
    
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}{file_ext}"
    
    file_url = minio_service.upload_file(
        bucket_name=settings.MINIO_BUCKET_AVATARS,
        file=file.file,
        file_name=unique_filename,
        content_type=file.content_type
    )
    
    if not file_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload avatar"
        )
    
    return {
        "url": file_url,
        "filename": unique_filename
    }


@router.delete("/image")
async def delete_image(
    bucket_name: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Delete image from MinIO"""
    
    success = minio_service.delete_file(bucket_name, filename)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete image"
        )
    
    return {"message": "Image deleted successfully"}
