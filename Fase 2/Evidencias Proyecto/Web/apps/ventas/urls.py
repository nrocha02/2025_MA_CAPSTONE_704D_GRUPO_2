from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("producto/<int:producto_id>/", views.producto, name="producto_detalle"),
    path("catalogo/", views.catalogo, name="catalogo"),
    path("carrito/", views.carrito, name="carrito"),
    path("iniciosesion/", views.iniciosesion, name="iniciosesion"),
    path("registro/", views.registro_view, name="registro"),
]
