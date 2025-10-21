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
    path("iniciosesion/", views.iniciosesion, name="iniciosesion"),
    path("logout/", views.logout_view, name="logout"),
    path("registro/", views.registro_view, name="registro"),

]
 