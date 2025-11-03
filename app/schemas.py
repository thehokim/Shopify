from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ========== ENUMS ==========
class UserRoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    TENANT_OWNER = "tenant_owner"
    TENANT_STAFF = "tenant_staff"
    CUSTOMER = "customer"


class ProductStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class OrderStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


# ========== AUTH ==========
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    phone: Optional[str] = None


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str]
    full_name: Optional[str]
    phone: Optional[str]
    avatar_url: Optional[str]
    role: UserRoleEnum
    is_active: bool
    is_verified: bool
    tenant_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ========== TENANT ==========
class TenantCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    slug: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    owner_email: EmailStr
    owner_password: str = Field(..., min_length=8)
    owner_full_name: str


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class TenantResponse(BaseModel):
    id: int
    name: str
    slug: str
    domain: Optional[str]
    description: Optional[str]
    logo_url: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ========== CATEGORY ==========
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    category_type: Optional[str] = "general"
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    image_url: Optional[str]
    parent_id: Optional[int]
    category_type: Optional[str]
    sort_order: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ========== PRODUCT ATTRIBUTE ==========
class ProductAttributeCreate(BaseModel):
    name: str
    attribute_type: str  # select, multiselect, text, number
    options: Optional[List[str]] = None
    is_required: bool = False
    is_variant: bool = False
    sort_order: int = 0


class ProductAttributeResponse(BaseModel):
    id: int
    category_id: int
    name: str
    attribute_type: str
    options: Optional[List[str]]
    is_required: bool
    is_variant: bool
    sort_order: int

    class Config:
        from_attributes = True


# ========== PRODUCT ==========
class ProductAttributeValueCreate(BaseModel):
    attribute_id: int
    value: str


class ProductImageCreate(BaseModel):
    image_url: str
    alt_text: Optional[str] = None
    is_primary: bool = False
    sort_order: int = 0


class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(..., min_length=3, max_length=500)
    slug: str = Field(..., min_length=3, max_length=500)
    description: Optional[str] = None
    short_description: Optional[str] = None
    sku: str
    base_price: float = Field(..., gt=0)
    discount_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = None
    stock_quantity: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=10, ge=0)
    track_inventory: bool = True
    status: ProductStatusEnum = ProductStatusEnum.DRAFT
    is_featured: bool = False
    attributes: Optional[List[ProductAttributeValueCreate]] = []
    images: Optional[List[ProductImageCreate]] = []

    @validator('discount_price')
    def discount_less_than_base(cls, v, values):
        if v and 'base_price' in values and v >= values['base_price']:
            raise ValueError('Discount price must be less than base price')
        return v


class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    sku: Optional[str] = None
    base_price: Optional[float] = Field(None, gt=0)
    discount_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    status: Optional[ProductStatusEnum] = None
    is_featured: Optional[bool] = None


class ProductImageResponse(BaseModel):
    id: int
    image_url: str
    alt_text: Optional[str]
    is_primary: bool
    sort_order: int

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    tenant_id: int
    category_id: int
    name: str
    slug: str
    description: Optional[str]
    short_description: Optional[str]
    sku: str
    base_price: float
    discount_price: Optional[float]
    stock_quantity: int
    status: ProductStatusEnum
    is_featured: bool
    views_count: int
    sales_count: int
    wishlist_count: int
    created_at: datetime
    images: List[ProductImageResponse] = []

    class Config:
        from_attributes = True


# ========== DISCOUNT ==========
class DiscountCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=100)
    name: str
    description: Optional[str] = None
    discount_type: str  # percentage, fixed, free_shipping
    value: float = Field(..., gt=0)
    min_purchase_amount: float = Field(default=0, ge=0)
    max_discount_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    valid_from: datetime
    valid_to: datetime


class DiscountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    value: Optional[float] = Field(None, gt=0)
    min_purchase_amount: Optional[float] = None
    usage_limit: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class DiscountResponse(BaseModel):
    id: int
    code: str
    name: str
    description: Optional[str]
    discount_type: str
    value: float
    min_purchase_amount: float
    max_discount_amount: Optional[float]
    usage_limit: Optional[int]
    usage_count: int
    valid_from: datetime
    valid_to: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ========== CART ==========
class CartItemCreate(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(default=1, ge=1)
    selected_attributes: Optional[Dict[str, Any]] = None


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    selected_attributes: Optional[Dict[str, Any]]
    added_at: datetime

    class Config:
        from_attributes = True


# ========== WISHLIST ==========
class WishlistCreate(BaseModel):
    product_id: int


class WishlistResponse(BaseModel):
    id: int
    product_id: int
    added_at: datetime

    class Config:
        from_attributes = True


# ========== ORDER ==========
class OrderItemCreate(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = Field(..., ge=1)
    selected_attributes: Optional[Dict[str, Any]] = None


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    discount_code: Optional[str] = None
    shipping_address: Dict[str, Any]
    billing_address: Optional[Dict[str, Any]] = None
    payment_method: str
    notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    total_price: float
    product_attributes: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    subtotal: float
    discount_amount: float
    shipping_cost: float
    tax_amount: float
    total: float
    status: OrderStatusEnum
    payment_status: str
    payment_method: str
    shipping_address: Dict[str, Any]
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


# ========== SEARCH ==========
class ProductSearchFilters(BaseModel):
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    is_featured: Optional[bool] = None
    in_stock: Optional[bool] = None
    attributes: Optional[List[Dict[str, str]]] = None


class ProductSearchRequest(BaseModel):
    query: str = ""
    filters: Optional[ProductSearchFilters] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "relevance"  # relevance, price_asc, price_desc, newest, popular, rating


# ========== ANALYTICS ==========
class AnalyticsSummary(BaseModel):
    total_products: int
    active_products: int
    total_orders: int
    total_revenue: float
    total_customers: int
    popular_products: List[Dict[str, Any]]
    recent_orders: List[Dict[str, Any]]
