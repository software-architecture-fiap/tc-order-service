from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from enum import Enum
from ..database.database import Base

class Category(Base):
    """Representa uma Categoria de Produtos."""
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    enabled = Column(Boolean, default=True)

    products = relationship('Product', back_populates='category')

class Product(Base):
    """Representa um Produto."""
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    enabled = Column(Boolean, default=True)

    category = relationship('Category', back_populates='products')
    order_items = relationship('OrderItem', back_populates='product')

class Order(Base):
    """Representa um Pedido."""
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default='created', index=True)  
    payment_status = Column(String, default='pending', index=True)  
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    customer_id = Column(Integer, nullable=False)  

    order_items = relationship('OrderItem', back_populates='order', lazy='joined')  # Voltando para order_items
    tracking = relationship('Tracking', back_populates='order', cascade="all, delete-orphan")

class OrderItem(Base):
    """Relaciona um Pedido com seus Produtos."""
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, default=1)
    comment = Column(Text, nullable=True)  # ex: "sem cebola"

    order = relationship('Order', back_populates='order_items')
    product = relationship('Product', back_populates='order_items')

class Tracking(Base):
    """Registra o status de um Pedido."""
    __tablename__ = 'tracking'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    status = Column(String, index=True)  # ex: "pedido enviado", "entregue"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    order = relationship('Order', back_populates='tracking')

class PaymentStatus(str, Enum):
    pending = "pending"       # Aguardando pagamento
    approved = "approved"     # Pago
    rejected = "rejected"     # Recusado
    in_process = "in_process" # Em análise
    refunded = "refunded"

class OrderStatus(str, Enum):
    REQUESTED = "requested"                 # Pedido criado, aguardando pagamento
    PAID = "paid"                           # Pagamento confirmado, pedido será preparado
    PREPARING = "preparing"                 # Pedido sendo preparado
    READY_FOR_PICKUP = "ready_for_pickup"   # Pedido pronto para retirada/entrega
    OUT_FOR_DELIVERY = "out_for_delivery"   # Pedido saiu para entrega
    DELIVERED = "delivered"                 # Pedido entregue ao cliente
    CANCELLED = "cancelled"                 # Pedido cancelado antes do pagamento
    REFUNDED = "refunded"                   # Pedido cancelado e reembolsado
    REJECTED = "rejected"                   # Pedido recusado (por falta de estoque, erro, etc.)
