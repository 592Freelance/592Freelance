import os
import json
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Avg, Sum
from django.utils import timezone
from datetime import timedelta
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import ProductSerializer
from celery import shared_task
from .models import Product, UpdateProductPrices, DemandForecast
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from .tasks import predict_demand, calculate_dynamic_price


#PostgreSQL connection settings (ensure these are set in your Django settings.py)
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql',
#        'NAME': os.environ.get('DB_NAME', 'agri_market'),
#        'USER': os.environ.get('DB_USER', 'postgres'),
#        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#        'HOST': os.environ.get('DB_HOST', 'localhost'),
#        'PORT': os.environ.get('DB_PORT', '5432'),
#    }
#}

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=50)

class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

class Listing(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    date_listed = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')

class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

# Dynamic Price Allocation System
def calculate_dynamic_price(product_id):
    # Get the average price for the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    avg_price = PriceHistory.objects.filter(
        product_id=product_id,
        date__gte=thirty_days_ago
    ).aggregate(Avg('price'))['price__avg']

    # Get current supply and demand
    supply = Listing.objects.filter(product_id=product_id).aggregate(Sum('quantity'))['quantity__sum'] or 0
    demand = Order.objects.filter(listing__product_id=product_id, status='Pending').aggregate(Sum('quantity'))['quantity__sum'] or 0

    # Calculate price adjustment factor based on supply and demand
    if supply > 0:
        adjustment_factor = (demand / supply) - 1
    else:
        adjustment_factor = 0

    # Adjust price (max 20% change)
    if avg_price:
        new_price = Decimal(avg_price) * Decimal(1 + min(max(adjustment_factor, -0.2), 0.2))
    else:
        latest_listing = Listing.objects.filter(product_id=product_id).order_by('-date_listed').first()
        if latest_listing:
            new_price = Decimal(latest_listing.price)
        else:
            # If no historical data and no listings exist, return a default price or raise an exception
            raise ValueError(f"No price data available for product_id: {product_id}")
        
    return new_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# API views (using Django Rest Framework)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['get'])
    def get_dynamic_price(self, request, pk=None):
        product = self.get_object()
        try:
            price = calculate_dynamic_price(product.id)
            return Response({'price': price})
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        

#Celery Task
class UpdateProductPrices(models.Model):
    def handle(self, *args, **kwargs):
        self.update_product_prices()

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
        
    update_product_prices.delay()


# Express.js server for real-time updates (you'll need to set this up separately)
"""
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

io.on('connection', (socket) => {
    console.log('New client connected');
    
    socket.on('subscribe', (productId) => {
        socket.join(`product_${productId}`);
    });

    socket.on('disconnect', () => {
        console.log('Client disconnected');
    });
});

function updateProductPrice(productId, newPrice) {
    io.to(`product_${productId}`).emit('price_update', { productId, newPrice });
}

server.listen(3000, () =>
 console.log('Listening on port 3000'));
"""



@csrf_exempt
@require_http_methods(["POST"])
def update_product_price(request):
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        current_supply = data.get('current_supply')

        if not product_id or current_supply is None:
            return JsonResponse({'error': 'Missing required parameters'}, status=400)

        product = Product.objects.get(id=product_id)

        # Try to get the predicted demand from cache
        cache_key = f'predicted_demand_{product_id}'
        predicted_demand = cache.get(cache_key)

        if predicted_demand is None:
            # If not in cache, fetch from database
            demand_forecast, created = DemandForecast.objects.get_or_create(product=product)
            
            if created or demand_forecast.is_outdated():
                # If newly created or outdated, predict new demand
                predicted_demand = predict_demand(product.name)
                demand_forecast.predicted_demand = predicted_demand
                demand_forecast.save()
            else:
                predicted_demand = demand_forecast.predicted_demand

            # Store in cache for future use
            cache.set(cache_key, predicted_demand, timeout=3600)  # Cache for 1 hour

        # Calculate the dynamic price based on the pricing model
        new_price = calculate_dynamic_price(product_id, current_supply, predicted_demand)

        # Update the product price in the database
        product.price = new_price
        product.save()

        # Return the updated price to the frontend
        return JsonResponse({
            'product_id': product_id,
            'new_price': new_price,
            'predicted_demand': predicted_demand
        })

    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Add this URL pattern to your urls.py
# path('api/update-product-price/', update_product_price, name='update_product_price'),

# Test the API locally
if __name__ == '__main__':
    import requests

    # Assuming you're running the Django development server on localhost:8000
    url = 'http://localhost:8000/api/update-product-price/'
    
    # Test data
    data = {
        'product_id': 1,  # Replace with a valid product ID from your database
        'current_supply': 100
    }

    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

# Deployment instructions for Heroku
"""
1. Install the Heroku CLI and login:
   $ heroku login

2. Create a new Heroku app:
   $ heroku create your-app-name

3. Add a Procfile to your project root:
   web: gunicorn your_project_name.wsgi

4. Update your settings.py:
   import django_heroku
   django_heroku.settings(locals())

5. Add the following to your requirements.txt:
   gunicorn
   django-heroku

6. Commit your changes:
   $ git add .
   $ git commit -m "Prepare for Heroku deployment"

7. Push to Heroku:
   $ git push heroku main

8. Set up your database:
   $ heroku run python manage.py migrate

9. Create a superuser (if needed):
   $ heroku run python manage.py createsuperuser

10. Open your app:
    $ heroku open
"""

# Environment variables for deployment
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')

# Update database configuration for production
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}

# Add this to your models.py

class DemandForecast(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    predicted_demand = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)

    def is_outdated(self):
        # Consider the forecast outdated if it's more than 24 hours old
        return (timezone.now() - self.last_updated).days >= 1


