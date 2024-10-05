from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException,status
from app.api.auth.oauth import get_current_admin_user
from app.models import CreateProductResponseModel, Product, ProductBaseModel
from app.database import products_db

router = APIRouter()

@router.post("/products/", response_model=CreateProductResponseModel, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductBaseModel, current_user: dict = Depends(get_current_admin_user)):
  
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can create products")

    # Check for unique name
    if any(p.name.lower() == product.name.lower() for p in products_db.values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"Product name '{product.name}' already exists. Please use a unique name.")

    new_product = Product(
        **product.dict(),
        id=uuid4(),
        created_at=datetime.now(timezone.utc)
    )

    products_db[new_product.id] = new_product

    return CreateProductResponseModel(**new_product.dict())


