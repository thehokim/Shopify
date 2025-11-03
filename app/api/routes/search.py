from fastapi import APIRouter, Depends, Query
from typing import Optional, List

from app.schemas import ProductSearchRequest
from app.services.elasticsearch_service import es_service

router = APIRouter()


@router.post("/products")
async def search_products(
    search_request: ProductSearchRequest,
    tenant_id: int = Query(..., description="Tenant ID")
):
    """
    Search products with advanced filters
    
    - **query**: Search query (searches in name, description)
    - **filters**: Category, price range, attributes, stock status
    - **sort_by**: relevance, price_asc, price_desc, newest, popular, rating
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    """
    
    filters = search_request.filters.dict() if search_request.filters else {}
    
    results = es_service.search_products(
        tenant_id=tenant_id,
        query=search_request.query,
        filters=filters,
        page=search_request.page,
        page_size=search_request.page_size,
        sort_by=search_request.sort_by
    )
    
    return results


@router.get("/suggest")
async def suggest_products(
    q: str = Query(..., min_length=2, description="Search query"),
    tenant_id: int = Query(..., description="Tenant ID"),
    limit: int = Query(default=5, ge=1, le=10)
):
    """
    Get product suggestions for autocomplete
    """
    suggestions = es_service.suggest_products(
        tenant_id=tenant_id,
        query=q,
        size=limit
    )
    
    return {"suggestions": suggestions}
