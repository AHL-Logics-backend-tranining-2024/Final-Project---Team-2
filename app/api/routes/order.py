from datetime import timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from app.database import *
from app.api.auth.oauth import get_current_user
from app.models import CreateOrderRequestModel, CreateOrderResponseModel, Order, OrderProduct, User

router = APIRouter()

@router.post("/", response_model=CreateOrderResponseModel, status_code=201)
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
           created_at=new_order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
           updated_at=new_order.updated_at,
           status=new_order.status,
           products=new_order.products
        )

        return response
