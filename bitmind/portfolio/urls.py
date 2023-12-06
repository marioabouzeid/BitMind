"""
URL mappings for the recipe app.
"""
from django.urls import include, path
from portfolio import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(
    "transaction",
    views.TransactionViewSet,
    basename="transaction",
)
router.register(
    "cryptocurrency",
    views.CryptocurrencyViewSet,
    basename="cryptocurrency",
)
router.register(
    "holdings",
    views.UserHoldingsViewSet,
    basename="holdings",
)
app_name = "portfolio"

urlpatterns = [
    path("", include(router.urls)),
]
