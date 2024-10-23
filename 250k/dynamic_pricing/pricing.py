from agri_app.models import Product

def real_time_pricing_system(product_name):
    # ... existing code ...
    
    # Update the price in the database
    product = Product.objects.get(name=product_name)
    product.price = final_price
    product.save()
    
    return final_price
