from django.contrib import admin

from items.models import Item, Order

# Register your models here.

admin.site.register(Item)
admin.site.register(Order)
