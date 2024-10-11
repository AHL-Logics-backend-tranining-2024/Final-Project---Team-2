from datetime import datetime
import uuid
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column,relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String


class User(Base):
    __tablename__ = 'users'

    id:Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username:Mapped[str] = mapped_column(String, unique=True, index=True)
    email:Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password:Mapped[str] = mapped_column(String)
    is_admin:Mapped[bool] = mapped_column(Boolean, default=False)
    is_active:Mapped[bool] = mapped_column(Boolean, default=True)
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at:Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    orders = relationship("Order", back_populates="user")
    
class Status(Base):
    __tablename__ = 'statuses'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="status")

# Product class
class Product(Base):
    __tablename__ = 'products'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name: Mapped[str] = mapped_column(String, index=True)
    price: Mapped[Numeric] = mapped_column(Numeric(10, 2))
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    isAvailable: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    order_products: Mapped[list["OrderProduct"]] = relationship("OrderProduct", back_populates="product")

# Order class
class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))

    user: Mapped["User"] = relationship("User", back_populates="orders")
    status_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('statuses.id'))
    total_price: Mapped[Numeric] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    status: Mapped["Status"] = relationship("Status", back_populates="orders")
    order_products: Mapped[list["OrderProduct"]] = relationship("OrderProduct", back_populates="order")

# OrderProduct class
class OrderProduct(Base):
    __tablename__ = 'order_products'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('orders.id'))
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('products.id'))
    quantity: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="order_products")
    product: Mapped["Product"] = relationship("Product", back_populates="order_products")
