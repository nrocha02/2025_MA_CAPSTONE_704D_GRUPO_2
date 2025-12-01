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
    # Recuperar contraseña
    path("olvide-contrasena/", views.olvide_contrasena, name="olvide_contrasena"),
    path(
        "restablecer-contrasena/<uidb64>/<token>/",
        views.restablecer_contrasena,
        name="restablecer_contrasena",
    ),
    # Gestión de perfil de cliente
    path("mi-perfil/", views.mi_perfil, name="mi_perfil"),
    path("editar-perfil/", views.editar_perfil, name="editar_perfil"),
    path("cambiar-contrasena/", views.cambiar_contrasena, name="cambiar_contrasena"),
    # Gestión de direcciones
    path("agregar-direccion/", views.agregar_direccion, name="agregar_direccion"),
    path(
        "editar-direccion/<int:direccion_id>/",
        views.editar_direccion,
        name="editar_direccion",
    ),
    path(
        "eliminar-direccion/<int:direccion_id>/",
        views.eliminar_direccion,
        name="eliminar_direccion",
    ),
    # Gestión de métodos de pago
    path("agregar-metodo-pago/", views.agregar_metodo_pago, name="agregar_metodo_pago"),
    path(
        "editar-metodo-pago/<int:metodo_pago_id>/",
        views.editar_metodo_pago,
        name="editar_metodo_pago",
    ),
    path(
        "eliminar-metodo-pago/<int:metodo_pago_id>/",
        views.eliminar_metodo_pago,
        name="eliminar_metodo_pago",
    ),
    # Gestión de pedidos
    path("mis-pedidos/", views.mis_pedidos, name="mis_pedidos"),
    path(
        "pedido/<int:pedido_id>/",
        views.detalle_pedido,
        name="detalle_pedido",
    ),
]
