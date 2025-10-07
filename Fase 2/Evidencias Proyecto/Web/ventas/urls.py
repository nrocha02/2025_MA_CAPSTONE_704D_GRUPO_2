from django.urls import path
from . import views

urlpatterns = [
    # URLs públicas
    path("", views.index, name="index"),
    path("producto/<int:producto_id>/", views.producto, name="producto_detalle"),
    path("catalogo/", views.catalogo, name="catalogo"),
    path("carrito/", views.carrito, name="carrito"),
    path("perro/", views.perro, name="perro"),
    path("gato/", views.gato, name="gato"),
    path("arena/", views.arena, name="arena"),
    
    # URLs de administración/CRUD
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    
    # CRUD Categorías
    path("admin/categorias/", views.categoria_list, name="categoria_list"),
    path("admin/categorias/crear/", views.categoria_create, name="categoria_create"),
    path("admin/categorias/<int:categoria_id>/editar/", views.categoria_edit, name="categoria_edit"),
    path("admin/categorias/<int:categoria_id>/eliminar/", views.categoria_delete, name="categoria_delete"),
    
    # CRUD Productos
    path("admin/productos/", views.producto_list, name="producto_list"),
    path("admin/productos/crear/", views.producto_create, name="producto_create"),
    path("admin/productos/<int:producto_id>/editar/", views.producto_edit, name="producto_edit"),
    path("admin/productos/<int:producto_id>/eliminar/", views.producto_delete, name="producto_delete"),
]
