from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("producto/<int:producto_id>/", views.producto, name="producto_detalle"),
    path("catalogo/", views.catalogo, name="catalogo"),
    path("iniciosesion/", views.iniciosesion, name="iniciosesion"),
    path("logout/", views.logout_view, name="logout"),
    path("registro/", views.registro_view, name="registro"),
    # Páginas legales
    path(
        "terminos-y-condiciones/",
        views.terminos_condiciones,
        name="terminos_condiciones",
    ),
    path(
        "politica-de-privacidad/", views.politica_privacidad, name="politica_privacidad"
    ),
    path(
        "politica-de-devoluciones/",
        views.politica_devoluciones,
        name="politica_devoluciones",
    ),
]
