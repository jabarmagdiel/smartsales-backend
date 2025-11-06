from django.contrib import admin
from .models import Category, Product, Price, AtributoProducto, InventoryMovement

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Price)
admin.site.register(AtributoProducto)
admin.site.register(InventoryMovement)
