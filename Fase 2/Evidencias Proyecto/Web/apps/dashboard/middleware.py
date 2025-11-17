"""
Middleware personalizado para el dashboard de administración
"""
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.contrib.auth.decorators import login_required


class DashboardAuthMiddleware:
    """
    Middleware que redirige automáticamente al login del dashboard
    cuando se intenta acceder a una URL del dashboard sin estar autenticado
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Procesar la solicitud antes de que llegue a la vista
        response = self.process_request(request)
        if response:
            return response
            
        response = self.get_response(request)
        return response

    def process_request(self, request):
        # Solo aplicar este middleware a las URLs del dashboard
        if not request.path.startswith('/dashboard/'):
            return None
            
        # Permitir acceso a la página de login sin restricciones
        if request.path == reverse('dashboard:login'):
            return None
            
        try:
            # Resolver la URL para obtener información de la vista
            resolver_match = resolve(request.path)
            
            # Verificar si es una vista del dashboard que requiere autenticación
            if (resolver_match.app_name == 'dashboard' and 
                resolver_match.url_name != 'login'):
                
                # Si no está autenticado o no es staff, redirigir al login
                if (not request.user.is_authenticated or 
                    not request.user.is_staff):
                    
                    login_url = reverse('dashboard:login')
                    # Agregar la URL actual como parámetro 'next'
                    if request.path != login_url:
                        return redirect(f"{login_url}?next={request.path}")
                    
        except Exception:
            # En caso de error, permitir que la vista maneje la situación
            pass
            
        return None