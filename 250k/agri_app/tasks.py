from celery import shared_task
from .models import Product, PriceHistory
from decimal import Decimal, ROUND_HALF_UP
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def update_product_prices():
    products = Product.objects.all()
    for product in products:
        new_price = calculate_dynamic_price(product.id)
        try:
            PriceHistory.objects.create(product=product, price=new_price)
            print(f"Updated price for {product.name} to {new_price}")
        except Exception as e:
            print(f"Error updating price for {product.name}: {e}")

@shared_task
def predict_demand(product_name):
    # Implement your demand prediction logic here
    # For now, we'll return a dummy value
    return 100.0

def calculate_dynamic_price(product_id, current_supply, predicted_demand):
    # Implement your dynamic pricing logic here
    # For now, we'll return a dummy value
    return Decimal('10.00').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

@shared_task
def update_product_price(product_id, new_price):
    product = Product.objects.get(id=product_id)
    product.price = new_price
    product.save()

    # Notify WebSocket clients
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"product_{product_id}",
        {
            "type": "price_update",
            "product_id": product_id,
            "new_price": str(new_price)
        }
    )
