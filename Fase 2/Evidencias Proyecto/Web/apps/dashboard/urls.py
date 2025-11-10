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
    #urls brevo servicio
    path("brevo/", views.brevo_dashboard, name="brevo_dashboard"),
    path("brevo/send-custom/", views.brevo_send_custom_email, name="brevo_send_custom_email"),
    path("brevo/send-stock-alert/", views.brevo_send_stock_alert, name="brevo_send_stock_alert"),
    path("brevo/send-order-confirmation/", views.brevo_send_order_confirmation, name="brevo_send_order_confirmation"),
    path("brevo/test-api/", views.brevo_test_api, name="brevo_test_api"),
    
    
]