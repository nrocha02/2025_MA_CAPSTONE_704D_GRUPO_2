from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("ventas.urls")),  # URLs públicas en la raíz
    path("dashboard/", include("dashboard.urls")),  # Dashboard administrativo
    path("admin/", admin.site.urls),
]