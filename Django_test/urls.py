from django.contrib import admin
from django.urls import path

from items.views import (
    CreateCheckoutSessionView,
    ItemsHomeView,
    CancelView,
    SuccessView,
    ItemInfoView,
    OrderViewSet,
    add_to_order,
    del_from_order,
    CreateBuySessionView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cancel/", CancelView.as_view(), name="cancel"),
    path("success/", SuccessView.as_view(), name="success"),
    path("", ItemsHomeView.as_view(), name="home"),
    path("buy/<pk>/", CreateCheckoutSessionView.as_view(), name="buy-id"),
    path("item/<pk>/", ItemInfoView.as_view(), name="item-id"),
    path("order/<pk>/", OrderViewSet.as_view(), name="order"),
    path("add-to-order/<user_id>/<item_id>/", add_to_order, name="add-to-order"),
    path("del-from-order/<user_id>/<item_id>/", del_from_order, name="del-from-order"),
    path(
        "buy-all-order/<user_id>/",
        CreateBuySessionView.as_view(),
        name="buy-all-order",
    ),
]
