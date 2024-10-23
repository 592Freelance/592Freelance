from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import json
from .models import Product, DemandForecast
from .serializers import ProductSerializer
from .tasks import predict_demand, calculate_dynamic_price
from dynamic_pricing.pricing import real_time_pricing_system

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['get'])
    def get_dynamic_price(self, request, pk=None):
        product = self.get_object()
        try:
            price = calculate_dynamic_price(product.id, 100, 100)  # Dummy values for supply and demand
            return Response({'price': price})
        except ValueError as e:
            return Response({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def update_product_price(request):
    # ... copy the update_product_price function from your original file ...

def update_price(request, product_id):
    product = Product.objects.get(id=product_id)
    new_price = real_time_pricing_system(product.name)
    update_product_price.delay(product_id, new_price)
    return JsonResponse({'status': 'Price update scheduled'})

def get_product(request, product_id):
    product = Product.objects.get(id=product_id)
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'price': str(product.price),
        'quantity': product.quantity,
        'seller': product.seller.username
    })
