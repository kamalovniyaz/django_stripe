from django.contrib.auth.models import User
from django.db import models


class Item(models.Model):

    name = models.CharField("Название", max_length=255, null=False)
    description = models.CharField("Описание", max_length=255)
    price = models.IntegerField("Цена", default=0)

    def __str__(self):
        return self.name

    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="order")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    count = models.PositiveIntegerField("Количество", default=0)
