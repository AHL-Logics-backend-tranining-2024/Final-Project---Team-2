from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends,Query, status
from app.api.auth.oauth import get_current_admin_user
from app.connection_to_db import get_db
from app.schemas import (
    CreateProductRequestModel,
    CreateProductResponseModel,
    GetProductResponseModel,
    SearchRequest,
    SearchResult,
    UpdatedProductRequestModel,
    UpdatedProductResponseModel,
)
from sqlalchemy.orm import Session
from app.models import User
from app.services.product_service import ProductService

router = APIRouter()


@router.post(
    "/", response_model=CreateProductResponseModel, status_code=status.HTTP_201_CREATED
)
async def create_product(
    product: CreateProductRequestModel,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    product_service = ProductService(db)
    new_product = product_service.create_product(product)
    return CreateProductResponseModel.from_orm(new_product)


@router.put(
    "/{product_id}",
    response_model=UpdatedProductResponseModel,
    status_code=status.HTTP_200_OK,
)
async def update_product(
    product_id: UUID,
    product_update: UpdatedProductRequestModel,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):

    product_service = ProductService(db)
    updated_product = product_service.update_product(product_id, product_update)
    return UpdatedProductResponseModel.from_orm(updated_product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    product_service = ProductService(db)
    product_service.delete_product(product_id)


@router.get(
    "/", response_model=list[GetProductResponseModel], status_code=status.HTTP_200_OK
)
def get_all_products(db: Session = Depends(get_db)):
    product_service = ProductService(db)
    products = product_service.get_all_products()
    return [GetProductResponseModel.from_orm(product) for product in products]


@router.get("/search", response_model=SearchResult, status_code=status.HTTP_200_OK)
async def search_products(
    search_request: Annotated[SearchRequest, Query()], db: Session = Depends(get_db)
):
    product_service = ProductService(db)
    search_result = product_service.search_products(search_request)
    return search_result


@router.get(
    "/{product_id}",
    response_model=GetProductResponseModel,
    status_code=status.HTTP_200_OK,
)
async def get_product(product_id: UUID, db: Session = Depends(get_db)):

    product_service = ProductService(db)
    product = product_service.get_product(product_id)
    return GetProductResponseModel.from_orm(product)
