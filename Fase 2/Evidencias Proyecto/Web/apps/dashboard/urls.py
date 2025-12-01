from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    # Autenticación
    path("", views.dashboard_login, name="login"),
    path("logout/", views.dashboard_logout, name="logout"),
    path("acceso_denegado/", views.acceso_denegado, name="acceso_denegado"),
    # Dashboard principal
    path("index", views.admin_dashboard, name="admin_dashboard"),
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
    # urls brevo servicio
    path("brevo/", views.brevo_dashboard, name="brevo_dashboard"),
    path(
        "brevo/send-custom/",
        views.brevo_send_custom_email,
        name="brevo_send_custom_email",
    ),
    path(
        "brevo/send-stock-alert/",
        views.brevo_send_stock_alert,
        name="brevo_send_stock_alert",
    ),
    path(
        "brevo/send-order-confirmation/",
        views.brevo_send_order_confirmation,
        name="brevo_send_order_confirmation",
    ),
    path("brevo/test-api/", views.brevo_test_api, name="brevo_test_api"),
    # Reportes
    path("reportes/ventas/", views.reportes_ventas, name="reportes_ventas"),
    path("reportes/productos/", views.reportes_productos, name="reportes_productos"),
    # APIs para gráficos
    path("api/ventas-chart/", views.api_ventas_chart, name="api_ventas_chart"),
    path(
        "api/categorias-chart/", views.api_categorias_chart, name="api_categorias_chart"
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
    # Gestión de Pedidos
    path("pedidos/", views.pedido_list, name="pedido_list"),
    path("pedidos/<int:pedido_id>/", views.pedido_detail, name="pedido_detail"),
    path("pedidos/<int:pedido_id>/editar/", views.pedido_edit, name="pedido_edit"),
    path(
        "pedidos/<int:pedido_id>/cambiar-estado/",
        views.pedido_cambiar_estado,
        name="pedido_cambiar_estado",
    ),
    path(
        "pedidos/<int:pedido_id>/agregar-tracking/",
        views.pedido_agregar_tracking,
        name="pedido_agregar_tracking",
    ),
    path("pedidos/exportar/", views.pedido_export, name="pedido_export"),
]
