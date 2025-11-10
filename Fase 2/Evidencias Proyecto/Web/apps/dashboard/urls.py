from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # Dashboard principal
    path("", views.admin_dashboard, name="admin_dashboard"),
    # CRUD Categorías
    path("categorias/", views.categoria_list, name="categoria_list"),
    path("categorias/crear/", views.categoria_create, name="categoria_create"),
    path(
        "categorias/<int:categoria_id>/editar/",
        views.categoria_edit,
        name="categoria_edit",
    ),
    path(
        "categorias/<int:categoria_id>/eliminar/",
        views.categoria_delete,
        name="categoria_delete",
    ),
    # CRUD Productos
    path("productos/", views.producto_list, name="producto_list"),
    path("productos/crear/", views.producto_create, name="producto_create"),
    path(
        "productos/<int:producto_id>/editar/", views.producto_edit, name="producto_edit"
    ),
    path(
        "productos/<int:producto_id>/eliminar/",
        views.producto_delete,
        name="producto_delete",
    ),
    # CRUD Costos de Envío
    path("costos-envio/", views.costo_envio_list, name="costo_envio_list"),
    path("costos-envio/crear/", views.costo_envio_create, name="costo_envio_create"),
    path(
        "costos-envio/<int:costo_id>/editar/",
        views.costo_envio_edit,
        name="costo_envio_edit",
    ),
    path(
        "costos-envio/<int:costo_id>/eliminar/",
        views.costo_envio_delete,
        name="costo_envio_delete",
    ),
    path(
        "costos-envio/cargar-predeterminados/",
        views.costo_envio_cargar_predeterminados,
        name="costo_envio_cargar_predeterminados",
    ),
]
