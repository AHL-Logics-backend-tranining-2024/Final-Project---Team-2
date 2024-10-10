from datetime import timezone
from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path,status
from app.database import *
from app.api.auth.oauth import get_current_admin_user, get_current_user
from app.models import *

router = APIRouter()

@router.post("/", response_model=CreateOrderResponseModel, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_request: CreateOrderRequestModel,
    current_user: User = Depends(get_current_user)
):

        # Calculate total price and validate products
        total_price = Decimal('0.00')
        product_details: list[dict] = []
        for item in order_request.products:
            product = products_db.get(str(item.product_id))
            if not product:
                raise HTTPException(status_code=400, detail=f"Product with id {item.product_id} not found")
            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
            item_price = product.price * item.quantity
            total_price += item_price
            product_details.append({
                "product_id": item.product_id,
                "quantity": item.quantity
            })

        pending_status_id = [status["id"] for status in statusOrders_db.values() if status["name"] == "Pending"][0]

        # Create new order
        new_order = Order(
            id=uuid4(),
            user_id=current_user["id"],
            status_id=pending_status_id,
            total_price=total_price,
            created_at=datetime.now(timezone.utc),
            updated_at=None,
            status=statusOrders_db[pending_status_id],
            products=[]  # We'll add products after creating the order
        )

        # Add order to fake database
        orders_db[new_order.id] = new_order

        # Create OrderProduct instances
        for product_detail in product_details:
            order_product = OrderProduct(
                id=uuid4(),
                order_id=new_order.id,
                product_id=product_detail["product_id"],
                quantity=product_detail["quantity"],
                created_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                updated_at=None
            )
            new_order.products.append(order_product)

            # Update product stock (in a real scenario, this should be done in a transaction)
            product = products_db[str(product_detail["product_id"])]
            if product:
              if product.stock < product_detail["quantity"]:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
              product.stock -= product_detail["quantity"]
              products_db[str(product_detail["product_id"])] = product  # Update the product stock in the database

        # Prepare response
        response = CreateOrderResponseModel(
           id=new_order.id,
           user_id=new_order.user_id,
           status_id=new_order.status_id,
           total_price=new_order.total_price,
           created_at=new_order.created_at,
           updated_at=new_order.updated_at,
           status=new_order.status,
           products=new_order.products
        )

        return response
    
    
@router.put("/{order_id}/status", response_model=UpdateOrderStatusResponseModel,status_code=status.HTTP_200_OK)
async def update_order_status(
    order_id: UUID,
    status_update: UpdateOrderStatusRequestModel,
    current_admin: User = Depends(get_current_admin_user)
):

       # Step 2: Input Validation
    if order_id not in orders_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    valid_statuses = ["Pending", "Processing", "Completed", "Canceled"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status provided")

    # Step 3: Order Status Update Logic
    order = orders_db[order_id]
    new_status_id = next((status["id"] for status in statusOrders_db.values() if status["name"].lower() == status_update.status.lower()), None)
    
    if not new_status_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status not found in the system")

    order.status_id = new_status_id
    order.status = StatusModel(id=new_status_id, name=statusOrders_db[new_status_id]["name"])
    order.updated_at = datetime.now(timezone.utc)

    # Update the order in the database
    orders_db[order_id] = order

    # Step 4: Prepare and return the response
    response = UpdateOrderStatusResponseModel(
        id=order.id,
        user_id=order.user_id,
        total_price=order.total_price,
        created_at=order.created_at,
        updated_at=order.updated_at,
        status=order.status.name
                )

    return response

  
@router.get("/{order_id}", response_model=GetOrderResponseModel,status_code=status.HTTP_200_OK)
async def get_order_details(
    order_id: UUID = Path(..., description="The ID of the order to retrieve")
):
    
        # Retrieve the order from the fake database
        order = orders_db.get(order_id)

        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        # Construct the response
        response = GetOrderResponseModel(
            id=order.id,
            user_id=order.user_id,
            status=order.status.name,
            total_price=Decimal(order.total_price),
            created_at=order.created_at,
            updated_at=order.updated_at,
            products=[
                OrderProductBaseModel(
                    product_id=product.product_id,
                    quantity=product.quantity
                )
                for product in order.products
            ]
        )

        return response    


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    order_id: UUID = Path(..., description="The ID of the order to be canceled"),
    current_user: User = Depends(get_current_user)
):

    # Step 1: Order Status Check
    if order_id not in orders_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    order = orders_db[order_id]

    # Check if the order belongs to the current user
    if str(order.user_id) != str(current_user.get("id")):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to cancel this order")

    # Check if the order status is "pending"
    if order.status.name.lower() != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending orders can be canceled")

    # Step 2: Cancel Order Logic
    canceled_status = next((status for status in statusOrders_db.values() if status["name"].lower() == "canceled"), None)
    if not canceled_status:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Canceled status not found in the system")

    order.status_id = canceled_status["id"]
    order.status = StatusModel(**canceled_status)
    order.updated_at = datetime.now(timezone.utc)

    # Update the order in the database
    orders_db[order_id] = order

    # Step 3: Response
    # FastAPI will automatically return a 204 No Content status
    return None
