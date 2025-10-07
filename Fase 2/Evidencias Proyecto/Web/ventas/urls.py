from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("producto/", views.producto, name="producto"),
    path("catalogo/", views.catalogo, name="catalogo"),
    path("carrito/", views.carrito, name="carrito"),
    path("perro/", views.perro, name="perro"),
    path("gato/", views.gato, name="gato"),
    path("arena/", views.arena, name="arena")
]
