from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# ----------------- Categorias -----------------
class CategoryBase(BaseModel):
    name: str
    enabled: bool

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    name: str
    enabled: bool

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    enabled: Optional[bool] = None

# ----------------- Produtos -----------------
class ProductBase(BaseModel):
    name: str
    price: float
    category_id: int
    enabled: bool

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    id: int
    category: Optional[CategoryRead] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    enabled: Optional[bool] = None

# ----------------- Pedidos -----------------
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemRead(OrderItemBase):
    id: int
    product: Optional[ProductRead] = None

class OrderBase(BaseModel):
    customer_id: int
    status: str = "created"
    payment_status: str = "pending"

class OrderCreate(OrderBase):
    order_items: List[OrderItemCreate]
    email: Optional[str] = None

class OrderRead(OrderBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    items: List[OrderItemRead] = []

class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None

# ----------------- Rastreamento -----------------
class TrackingBase(BaseModel):
    status: str
    order_id: int

class TrackingRead(TrackingBase):
    id: int
    created_at: datetime
