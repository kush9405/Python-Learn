#type: ignore
from asyncio.log import logger as async_logger
from dataclasses import dataclass
from typing import List
from django.db import transaction  # type: ignore
from notifications.tasks import send_order_confirmation_task
from payments.services import initiate_uropay_order
from products.models import Product

from .models import Order, OrderItem

import logging
logger = logging.getLogger(__name__)


@dataclass
class OrderItemDTO:
    product_id: int
    quantity: int

# orders/services.py

def create_order_service(user, items: List[OrderItemDTO], address:str) -> Order:
    with transaction.atomic():
        # 1. Create the order header first
        order = Order.objects.create(user=user, status='pending',address=address)
        total_price = 0

        logger.info(f"ORDER_PLACEMENT: User {user.id} placing order for {len(items)} items")
        for item in items:
            # We use .get() which might throw a Product.DoesNotExist error
            try:
                product = Product.objects.select_for_update().get(id=item.product_id)
            except Product.DoesNotExist:
                raise ValueError(f"Product with ID {item.product_id} not found.")

            if product.stock_quantity < item.quantity:
                raise ValueError(f"Not enough stock for {product.name}. Available: {product.stock_quantity}")

            # Calculate and save Item
            price = product.price * item.quantity
            total_price += price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.price
            )

            # Deduct stock
            product.stock_quantity -= item.quantity
            product.save()

        # Update final total
        order.total_amount = total_price
        order.save()
    # Return the order only after the transaction is successfully committed
    logger.info(f"ORDER_SUCCESS: Order {order.order_id} created successfully")

    return order


@dataclass
class CheckoutData:
    user: str
    items: List[OrderItemDTO]
    address: str

def checkout_orchestrator(data: CheckoutData):
    """
    This is the COORDINATOR.
    Its only job is to manage the sequence of events.
    """
    # 1. Create Order (DB Logic)
    order = create_order_service(user=data.user, items=data.items, address=data.address)

    # 2. Initiate Payment (Third-party Logic)
    try:

        payment_response = initiate_uropay_order(order, data.user)
        send_order_confirmation_task.delay(order.id)
    except Exception as e:
        # Log failure but return the order (Per your requirement)
        async_logger.error(f"Payment failed for order {order.id}: {e}")
        payment_response = None

    return order, payment_response