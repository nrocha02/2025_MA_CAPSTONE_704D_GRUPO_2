from django.urls import path
from . import views

app_name = 'carrito'

urlpatterns = [
    path("", views.ver_carrito, name="ver_carrito"),
    path("add/", views.agregar_carrito, name="agregar_al_carrito"),
    path("remove/", views.eliminar_carrito, name="eliminar_del_carrito"),
    path("update/", views.actualizar_carrito, name="actualizar_el_carrito"),
]
