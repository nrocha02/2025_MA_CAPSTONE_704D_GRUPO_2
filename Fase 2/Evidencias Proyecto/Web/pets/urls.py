from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.ventas.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("admin/", admin.site.urls),
]