from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import Product
from app.schemas import (
    CreateProductRequestModel,
    SearchRequest,
    UpdatedProductRequestModel,
)


class ProductService:
    def __init__(self, db: Session):
        self.db = db

    def create_product(self, product: CreateProductRequestModel) -> Product:
        # Check for unique name
        if self.db.query(Product).filter(Product.name.ilike(product.name)).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product name '{product.name}' already exists. Please use a unique name.",
            )

        new_product = Product(**product.dict())
        self.db.add(new_product)
        self.db.commit()
        self.db.refresh(new_product)
        return new_product

    def update_product(
        self, product_id: UUID, product_update: UpdatedProductRequestModel
    ) -> Product:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
            )

        update_data = product_update.dict(exclude_unset=True)

        # Check for unique name if it's being updated
        if "name" in update_data:
            existing_product = (
                self.db.query(Product)
                .filter(
                    Product.name.ilike(update_data["name"]), Product.id != product_id
                )
                .first()
            )
            if existing_product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product name '{update_data['name']}' already exists. Please use a unique name.",
                )

        for key, value in update_data.items():
            setattr(product, key, value)

        product.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete_product(self, product_id: UUID):
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found.",
            )
        self.db.delete(product)
        self.db.commit()

    def get_all_products(self):
        return self.db.query(Product).all()

    def get_product(self, product_id: UUID) -> Product:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {product_id} not found.",
            )
        return product

    def search_products(self, search_request: SearchRequest):
        query = self.db.query(Product)

        if search_request.name:
            query = query.filter(Product.name.ilike(f"%{search_request.name}%"))
        if search_request.min_price:
            query = query.filter(Product.price >= search_request.min_price)
        if search_request.max_price:
            query = query.filter(Product.price <= search_request.max_price)
        if search_request.isAvailable is not None:
            query = query.filter(Product.isAvailable == search_request.isAvailable)

        # Sort
        if search_request.sort_by == "price":
            query = query.order_by(
                desc(Product.price)
                if search_request.sort_order == "desc"
                else asc(Product.price)
            )
        else:
            query = query.order_by(
                desc(Product.name)
                if search_request.sort_order == "desc"
                else asc(Product.name)
            )

        # Paginate
        total_products = query.count()
        total_pages = -(-total_products // search_request.page_size)
        products = (
            query.offset((search_request.page - 1) * search_request.page_size)
            .limit(search_request.page_size)
            .all()
        )

        return {
            "page": search_request.page,
            "total_pages": total_pages,
            "products_per_page": search_request.page_size,
            "total_products": total_products,
            "products": products,
        }
