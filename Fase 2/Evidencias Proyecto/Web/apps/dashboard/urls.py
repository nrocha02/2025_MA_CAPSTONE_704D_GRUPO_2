from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path("", views.admin_dashboard, name="admin_dashboard"),
    
    # CRUD Categorías
    path("categorias/", views.categoria_list, name="categoria_list"),
    path("categorias/crear/", views.categoria_create, name="categoria_create"),
    path("categorias/<int:categoria_id>/editar/", views.categoria_edit, name="categoria_edit"),
    path("categorias/<int:categoria_id>/eliminar/", views.categoria_delete, name="categoria_delete"),
    
    # CRUD Productos
    path("productos/", views.producto_list, name="producto_list"),
    path("productos/crear/", views.producto_create, name="producto_create"),
    path("productos/<int:producto_id>/editar/", views.producto_edit, name="producto_edit"),
    path("productos/<int:producto_id>/eliminar/", views.producto_delete, name="producto_delete"),

    # Reportes
    path("reportes/ventas/", views.reportes_ventas, name="reportes_ventas"),
    path("reportes/productos/", views.reportes_productos, name="reportes_productos"),
    
    # APIs para gráficos
    path("api/ventas-chart/", views.api_ventas_chart, name="api_ventas_chart"),
    path("api/categorias-chart/", views.api_categorias_chart, name="api_categorias_chart"),
]