import stripe
from django.db.models import Q, F
from django.shortcuts import redirect
from django.views import View
from django.conf import settings
from django.views.generic import TemplateView
from .models import Item, Order
from requests import request

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessView(TemplateView):
    """Шаблон при успешной оплате"""

    template_name = "success.html"


class CancelView(TemplateView):
    """Шаблон при отклоненной оплате"""

    template_name = "cancel.html"


class ItemsHomeView(TemplateView):
    """Домашняя страница со всеми товарами"""

    model = Item
    context_object_name = "items_item"
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        items = Item.objects.all()
        context = super(ItemsHomeView, self).get_context_data(**kwargs)
        context.update(
            {"items": items, "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY}
        )
        return context


class CreateCheckoutSessionView(View):
    """Создаем stripe checkout session для оплаты выбранного товара"""

    def post(self, request, *args, **kwargs):
        item_id = self.kwargs["pk"]
        item = Item.objects.get(id=item_id)
        YOUR_DOMAIN = "http://127.0.0.1:8000"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": item.price * 100,
                        "product_data": {
                            "name": item.name,
                            "description": item.description,
                        },
                    },
                    "quantity": 1,
                },
            ],
            metadata={"product_id": item.id},
            mode="payment",
            success_url=YOUR_DOMAIN + "/success/",
            cancel_url=YOUR_DOMAIN + "/cancel/",
        )

        return redirect(checkout_session.url, code=303)


class ItemInfoView(TemplateView):
    """Детальная информация о выбранном товаре"""

    model = Item
    context_object_name = "items_item"
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        item_id = self.kwargs["pk"]
        item = Item.objects.get(id=item_id)
        context = super(ItemInfoView, self).get_context_data(**kwargs)
        context.update({"item": item, "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY})
        return context


class OrderViewSet(TemplateView):
    """Корзина пользователя"""

    model = Order
    context_object_name = "items_order"
    template_name = "order.html"

    def get_context_data(self, **kwargs):
        user_id = self.kwargs["pk"]
        order = Order.objects.all().filter(user_id=user_id)
        context = super(OrderViewSet, self).get_context_data(**kwargs)
        context.update(
            {"order": order, "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY}
        )
        return context


def add_to_order(request, user_id, item_id):
    """Добавление товара в корзину"""
    if len(Order.objects.filter(Q(user_id=user_id) & Q(item_id=item_id))) == 0:
        db = Order.objects.create(user=request.user, item_id=item_id, count=1)
        db.save()
    else:
        db = Order.objects.get(Q(user_id=user_id) & Q(item_id=item_id))
        db.count = F("count") + 1
        db.save()
    return redirect("home")


def del_from_order(request, user_id, item_id):
    """Удаление товара из корзины"""
    if len(Order.objects.filter(Q(user_id=user_id) & Q(item_id=item_id))) == 0:
        db = Order.objects.create(user=request.user, item_id=item_id, count=1)
        db.save()
    else:
        db = Order.objects.get(Q(user_id=user_id) & Q(item_id=item_id))
        if db.count >= 2:
            db.count = F("count") - 1
            db.save()
            return redirect("home")
        else:
            db.count = F("count") - 1
            db.save()
            db = Order.objects.get(Q(user_id=user_id) & Q(item_id=item_id))
            if db.count == 0:
                db = Order.objects.get(Q(user_id=user_id) & Q(item_id=item_id))
                db.delete()
    return redirect("home")


class CreateBuySessionView(View):
    """Создаем stripe checkout session для оплаты всей корзины"""

    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        all_items = []
        items_ids = []
        order = Order.objects.select_related().filter(user_id=user_id)
        for object in order:
            new_str = {
                "price_data": {
                    "currency": "usd",
                    "unit_amount": object.item.price * 100,
                    "product_data": {
                        "name": object.item.name,
                    },
                },
                "quantity": object.count,
            }
            items_ids.append(object.item_id)
            all_items.append(new_str)

        YOUR_DOMAIN = "http://127.0.0.1:8000"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=all_items,
            mode="payment",
            success_url=YOUR_DOMAIN + "/success/",
            cancel_url=YOUR_DOMAIN + "/cancel/",
        )
        for i in items_ids:
            del_from_order(request, user_id=user_id, item_id=i)

        return redirect(checkout_session.url, code=303)
