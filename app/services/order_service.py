from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session,joinedload
from sqlalchemy.exc import SQLAlchemyError
from app.models import Order,Product,Status,OrderProduct
from app.schemas import CreateOrderRequestModel, CreateOrderResponseModel, GetOrderResponseModel, OrderProductBaseModel, UpdateOrderStatusResponseModel


class OrderService:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, user_id: UUID, order_request: CreateOrderRequestModel) -> CreateOrderResponseModel:
        # Step 1: Get pending status
        pending_status = self._get_pending_status()

        # Step 2: Fetch and validate products
        product_map, total_price = self._validate_products(order_request.products)

        # Step 3: Create new order
        new_order = self._create_new_order(user_id, pending_status.id, total_price)

        # Step 4: Create order products and update stock
        self._create_order_products(new_order.id, order_request.products, product_map)

        # Step 5: Create response model
        response_data = CreateOrderResponseModel(
            id=new_order.id,
            user_id=new_order.user_id,
            status=pending_status.name,
            total_price=new_order.total_price,
            created_at=new_order.created_at
        )

        return response_data

    def _get_pending_status(self):
        pending_status = self.db.query(Status).filter(Status.name == "Pending").first()
        if not pending_status:
            raise HTTPException(status_code=400, detail="Pending status not found")
        return pending_status

    def _validate_products(self, order_products):
        total_price = Decimal('0.00')
        product_ids = [item.product_id for item in order_products]
        db_products = self.db.query(Product).filter(Product.id.in_(product_ids)).all()

        # Create a dictionary for quick lookup
        product_map = {str(product.id): product for product in db_products}

        for item in order_products:
            product_id = str(item.product_id)
            product = product_map.get(product_id)

            if not product:
                raise HTTPException(status_code=400, detail=f"Product with id {product_id} not found")

            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock for product {product.name}. Available: {product.stock}, Requested: {item.quantity}"
                )

            item_price = product.price * item.quantity
            total_price += item_price

        return product_map, total_price

    def _create_new_order(self, user_id: UUID, status_id: UUID, total_price: Decimal):
        new_order = Order(
            user_id=user_id,
            status_id=status_id,
            total_price=total_price,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(new_order)
        self.db.commit()  # Commit to get the new order ID
        return new_order

    def _create_order_products(self, order_id: UUID, order_products, product_map):
        order_products_list = []

        for item in order_products:
            product_id = str(item.product_id)
            product = product_map[product_id]

            # Create the order product instance
            order_product = OrderProduct(
                order_id=order_id,  # Set the order ID here
                product_id=product.id,
                quantity=item.quantity,
                created_at=datetime.now(timezone.utc)
            )
            order_products_list.append(order_product)

            # Update product stock
            product.stock -= item.quantity

        # Update the total price of the order
        total_price = sum(product.price * item.quantity for item in order_products)
        self.db.add_all(order_products_list)
        self.db.commit()  # Commit the order products

        return total_price

    def update_order_status(self, order_id: UUID, new_status: str) -> UpdateOrderStatusResponseModel:
        order = self.db.query(Order).get(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        new_status_obj = self.db.query(Status).filter(Status.name == new_status).first()
        if not new_status_obj:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status provided")

        order.status_id = new_status_obj.id
        order.updated_at = datetime.now(timezone.utc)

        
        self.db.commit()
        self.db.refresh(order)

        response_data =  UpdateOrderStatusResponseModel(
            id=order.id,
            user_id=order.user_id,
            status=new_status_obj.name,  # Ensure status is a string
            total_price=order.total_price,
            created_at=order.created_at
            )
        
        return response_data

    def get_order_details(self, order_id: UUID) -> GetOrderResponseModel :
     order = self.db.query(Order).options(
         joinedload(Order.status),
        joinedload(Order.order_products).joinedload(OrderProduct.product)
        ).get(order_id)

     if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

     return GetOrderResponseModel(
        id=order.id,  # Use order.id instead of order_id
        user_id=order.user_id,
        status=order.status.name,  # Ensure status is the name of the status
        total_price=order.total_price,
        created_at=order.created_at,
        updated_at=order.updated_at,
        products=[OrderProductBaseModel(
            product_id=op.product_id,
            quantity=op.quantity
        ) for op in order.order_products]  # Create a list of OrderProductBaseModel
    )
     
    def cancel_order(self, order_id: UUID, user_id: UUID):
        order = self.db.query(Order).get(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if str(order.user_id) != str(user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You don't have permission to cancel this order")

        if order.status.name.lower() != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending orders can be canceled")

        canceled_status = self.db.query(Status).filter(Status.name == "Canceled").first()
        if not canceled_status:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Canceled status not found in the system")

        order.status_id = canceled_status.id
        order.updated_at = datetime.now(timezone.utc)

        # Restore product stock
        for order_product in order.order_products:
            product = order_product.product
            product.stock += order_product.quantity

        
        self.db.commit()
        self.db.refresh(order)

        return order