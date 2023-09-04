"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from portfolio import views


router = DefaultRouter()
router.register("transaction", views.TransactionViewSet)
router.register("cryptocurrency", views.CryptocurrencyViewSet)
app_name = "portfolio"

urlpatterns = [
    path("", include(router.urls)),
    path("holdings", views.UserCoinListView.as_view(), name="holdings"),
]
