from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, update_product_price, update_price, get_product

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('update-product-price/', update_product_price, name='update_product_price'),
    path('update-price/<int:product_id>/', update_price, name='update_price'),
    path('get-product/<int:product_id>/', get_product, name='get_product'),
]
