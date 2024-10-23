from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

# ... copy all your model definitions here ...

class DemandForecast(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    predicted_demand = models.FloatField()
    last_updated = models.DateTimeField(auto_now=True)

    def is_outdated(self):
        return (timezone.now() - self.last_updated).days >= 1

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    seller = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
