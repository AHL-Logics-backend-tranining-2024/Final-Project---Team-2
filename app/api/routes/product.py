from datetime import datetime, timezone
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException,status
from app.api.auth.oauth import get_current_admin_user
from app.models import CreateProductRequestModel, CreateProductResponseModel, GetProductBySearchResponseModel, GetProductResponseModel, Product, ProductBaseModel, SearchRequest, SearchResult, UpdatedProductRequestModel, UpdatedProductResponseModel, User
from app.database import products_db

router = APIRouter()

@router.post("/", response_model=CreateProductResponseModel, status_code=status.HTTP_201_CREATED)
async def create_product(product: CreateProductRequestModel, current_user: User = Depends(get_current_admin_user)): 
    # Check for unique name
    if any(p.name.lower() == product.name.lower() for p in products_db.values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail=f"Product name '{product.name}' already exists. Please use a unique name.")

    new_product = Product(
        **product.dict()
    )

    products_db[str(new_product.id)] = new_product

    return CreateProductResponseModel(
        id = new_product.id,
        name=new_product.name,
        price= new_product.price,
        description= new_product.description,
        stock= new_product.stock,
        isAvailable= new_product.isAvailable,
        created_at= new_product.created_at
        )


   
@router.put("/{product_id}",response_model=UpdatedProductResponseModel, status_code=status.HTTP_200_OK)
async def update_product(product_id: UUID, product_update: UpdatedProductRequestModel, current_user: User = Depends(get_current_admin_user)):
     
    product_data = products_db.get(str(product_id))
    
    if not product_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    # Convert product_data to a dictionary if it's a Product object
    if isinstance(product_data, Product):
        product_dict = product_data.dict()
    else:
        product_dict = product_data
    
    # Apply the updates (only update fields that were provided)
    update_data = product_update.dict(exclude_unset=True)
    
    # Check for unique name if it's being updated
    if 'name' in update_data and any(p.name.lower() == update_data['name'].lower() for p in products_db.values() if str(p.id) != str(product_id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Product name '{update_data['name']}' already exists. Please use a unique name."
        )
    
    # Update product's attributes with new data
    product_dict.update(update_data)
    
    # Update the 'updated_at' timestamp
    product_dict["updated_at"] = datetime.now(timezone.utc)
    
    # Create a new Product object with updated data
    updated_product = Product(**product_dict)
    
    # Update the product in the database
    products_db[str(product_id)] = updated_product
    
    return UpdatedProductResponseModel(**updated_product.dict())



@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: UUID, current_user: User = Depends(get_current_admin_user)):
    if str(product_id) in products_db:
        del products_db[str(product_id)]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error":f"Product with ID {product_id} not found."})
    

@router.get("/", response_model=list[GetProductResponseModel],status_code=status.HTTP_200_OK)
def get_all_products():
    
    if not products_db:
       return []
    
    return [
           GetProductResponseModel(
                 id=product.id,
                 name=product.name,
                 price=product.price,
                 stock=product.stock,
                 isAvailable=product.isAvailable,
                 created_at=product.created_at,
                 updated_at=product.updated_at,
            )
            for product in products_db.values()
        ]
    
    
@router.get("/search", response_model=SearchResult , status_code=status.HTTP_200_OK)
async def search_products(search_request: SearchRequest = Depends(SearchRequest)):
    # Filter products based on search criteria
    filtered_products = []
    for product in products_db.values():
        if (search_request.name is None or product.name.lower().find(search_request.name.lower()) != -1) and \
           (search_request.min_price is None or product.price >= search_request.min_price) and \
           (search_request.max_price is None or product.price <= search_request.max_price) and \
           (search_request.isAvailable is None or product.isAvailable == search_request.isAvailable):
            filtered_products.append(product)

    # Sort products based on sort_by and sort_order
    if search_request.sort_by == "price":
        filtered_products.sort(key=lambda x: x.price, reverse=(search_request.sort_order == "desc"))
    elif search_request.sort_by == "name":
        filtered_products.sort(key=lambda x: x.name, reverse=(search_request.sort_order == "desc"))

    # Paginate products
    total_pages = -(-len(filtered_products) // search_request.page_size)  # Calculate total pages
    products = filtered_products[(search_request.page-1)*search_request.page_size:search_request.page*search_request.page_size]

    # Return search result
    return SearchResult(
        page=search_request.page,
        total_pages=total_pages,
        products_per_page=search_request.page_size,
        total_products=len(filtered_products),
        products=[
            GetProductBySearchResponseModel(
        id=p.id,
        name=p.name,
        price=p.price,
        stock=p.stock,
        isAvailable=p.isAvailable,
    )
    for p in products
        ]
    )
    
@router.get("/{product_id}",response_model = GetProductResponseModel, status_code=status.HTTP_200_OK)
async def get_product(product_id: UUID):
    
        product = products_db.get(str(product_id))
        
        if product is None:
            raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found.".format(product_id))
        
        return GetProductResponseModel(
            id=product.id,
            name=product.name,
            price=product.price,
            stock=product.stock,
            isAvailable=product.isAvailable,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )
        
    