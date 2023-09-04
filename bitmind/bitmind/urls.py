"""
URL configuration for bitmind project.
"""
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView

from core import views as core_views


urlpatterns = [
    path("", RedirectView.as_view(url="/api/docs", permanent=False), name="root"),
    path("admin/", admin.site.urls),
    path("api/user/", include("user.urls")),
    path("api/portfolio/", include("portfolio.urls")),
    path("api/health/", core_views.HealthCheckView.as_view(), name="health-check"),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
