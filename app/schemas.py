from datetime import datetime, timezone
from decimal import Decimal
import re
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field, validator
from app.utils import get_password_hash, verify_password


# ------------ Token Model -----------------#
# Token Model for handling authentication tokens
class Token(BaseModel):
    access_token: str  # The access token for authentication
    token_type: str  # The type of the token (e.g., "bearer")


# TokenData Model for storing user information associated with the token
class TokenData(BaseModel):
    sub: Optional[UUID] = None


# ------------ User Model -----------------#
class UserBaseModel(BaseModel):
    username: str
    email: EmailStr


class UserCreateRequestModel(UserBaseModel):
    password: str = Field(
        ...,
        min_length=8,
        example="Jibreen123@",
    )

    @validator("password")
    def validate_password(cls, password: str):
        # Check for at least one lowercase letter
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter.")
        # Check for at least one uppercase letter
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")
        # Check for at least one digit
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit.")
        # Check for at least one special character
        if not re.search(r"[@$!%*?&]", password):
            raise ValueError("Password must contain at least one special character.")

        return password


class User(UserBaseModel):
    id: UUID = Field(default_factory=uuid4)
    hashed_password: str
    is_admin: bool = False  # Default values for admin status
    is_active: bool = True  # Default values for active status
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    def set_password(self, password: str):
        self.hashed_password = get_password_hash(password)

    def verify_password(self, password: str):
        return verify_password(password, self.hashed_password)

    class Config:
        orm_mode = True


class CreateUserResponseModel(UserBaseModel):
    id: UUID
    is_admin: bool
    is_active: bool
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
        from_attributes = True


class UpdateUserRequestModel(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(min_length=8, example="Jibreen123@")

    @validator("password")
    def validate_password(cls, password: str):
        # Check for at least one lowercase letter
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter.")
        # Check for at least one uppercase letter
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter.")
        # Check for at least one digit
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit.")
        # Check for at least one special character
        if not re.search(r"[@$!%*?&]", password):
            raise ValueError("Password must contain at least one special character.")

        return password


class UpdatedUserResponseModel(UserBaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
        from_attributes = True


class GetUserResponseModel(UserBaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
        from_attributes = True


class ChangeRoleRequestModel(BaseModel):
    user_id: str = Field(..., description="The unique identifier of the user")
    is_admin: bool = Field(..., description="The new admin status for the user")


# ------------ Status Model -----------------#
# Models
class StatusBaseModel(BaseModel):
    name: str = Field(
        ...,
        examples=["Pending", "Processing", "Completed", "Canceled"],
        description="Status name, e.g. Pending, Processing, Completed, Canceled",
    )


class CreateStatusRequestModel(StatusBaseModel):
    pass


class UpdateStatusRequestModel(StatusBaseModel):
    pass


class Status(StatusBaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    class Config:
        orm_mode = True


class CreateStatusResponseModel(Status):
    pass

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
        from_attributes = True


class UpdateStatusResponseModel(Status):
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
        from_attributes = True


# ------------ Prodcut Model -----------------#
class ProductBaseModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: Decimal = Field(
        ..., description="Product price", ge=Decimal("0.01"), decimal_places=2
    )
    description: Optional[str] = Field(None, max_length=1000)
    stock: Optional[int] = Field(default=0, ge=0)
    isAvailable: Optional[bool] = Field(default=True)


class Product(ProductBaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)

    class Config:
        orm_mode = True


class CreateProductRequestModel(ProductBaseModel):
    pass  # All fields are inherited from ProductBaseModel


class CreateProductResponseModel(ProductBaseModel):
    id: UUID
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
        from_attributes = True


class UpdatedProductRequestModel(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(
        None, description="Product price", ge=Decimal("0.01"), decimal_places=2
    )
    description: Optional[str] = Field(None, max_length=1000)
    stock: Optional[int] = Field(None, ge=0)
    isAvailable: Optional[bool] = Field(default=None)


class UpdatedProductResponseModel(ProductBaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
        from_attributes = True


class SearchRequest(BaseModel):
    name: Optional[str] = Field(default="")
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    isAvailable: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1)
    sort_by: str = Field(default="name")
    sort_order: str = Field(default="asc")


class GetProductBySearchResponseModel(ProductBaseModel):
    id: UUID
    name: str
    price: Decimal
    stock: int
    isAvailable: bool

    class Config:
        from_attributes = True


class SearchResult(BaseModel):
    page: int
    total_pages: int
    products_per_page: int
    total_products: int
    products: list[GetProductBySearchResponseModel]


class GetProductResponseModel(ProductBaseModel):
    id: UUID
    name: str
    price: Decimal
    stock: int
    isAvailable: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
        from_attributes = True


# ------------------------ Order ------------------------- #
# Order Product Models
class OrderProductBaseModel(BaseModel):
    product_id: UUID
    quantity: int = Field(..., ge=1)

class OrderProduct(OrderProductBaseModel):
    id: UUID = Field(default_factory=uuid4)
    order_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
    
    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
    
    

class OrderProductResponseModel(OrderProduct):
    product: 'Product'  # This will be defined later or imported from another module
    
    class Config:
        from_attributes = True
    
# Order Models
class OrderBaseModel(BaseModel):
    user_id: UUID
    status_id: UUID
    total_price: Decimal = Field(..., ge=Decimal('0.01'), max_digits=10, decimal_places=2)

class Order(OrderBaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
    status: Optional[Status] = None
    products: list[OrderProduct] = []
    
    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}

# Request Models
class CreateOrderProductRequestModel(OrderProductBaseModel):
    pass

class CreateOrderRequestModel(BaseModel):
    products: list[CreateOrderProductRequestModel]

class UpdateOrderStatusRequestModel(BaseModel):
    status: str = Field(..., description="New status for the order")

# Response Models
class CreateOrderResponseModel(BaseModel):
    id:UUID
    user_id:UUID
    status:str
    total_price:Decimal
    created_at:datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
            Decimal: lambda v: str(v)
        }
    

class UpdateOrderStatusResponseModel(BaseModel):
    id: UUID
    user_id: UUID
    total_price: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S'),
            Decimal: lambda v: str(v)
        }
    

        
class GetOrderResponseModel(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    total_price: Decimal = Field(..., description="Total price of the order", decimal_places=2)
    created_at: datetime
    updated_at: Optional[datetime]
    products: list[OrderProductBaseModel]

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }
        
class GetOrderToUserResponseModel(BaseModel):
    id: UUID
    status: str
    total_price: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = Field(default=None)
    
    class Config:
        from_attributes=True
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }