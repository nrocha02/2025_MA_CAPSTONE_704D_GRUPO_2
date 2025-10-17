from django import template
from django.conf import settings
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def product_image_url(imagen_url):
    """
    Template tag para generar la URL completa de una imagen.
    
    Soporta imágenes de productos, marcas, categorías, etc.
    La ruta en la BD debe incluir el prefijo: productos/imagen.jpg, marcas/logo.png
    
    Si existe DO_SPACES_URL configurado, usa DigitalOcean Spaces.
    Si no, intenta usar la ruta estática local.
    
    Uso en templates:
        {% load image_tags %}
        <img src="{% product_image_url producto.imagen_url %}" alt="{{ producto.nombre }}">
        <img src="{% product_image_url marca.logo_url %}" alt="{{ marca.nombre }}">
    
    Args:
        imagen_url: La URL/ruta de la imagen. Debe incluir el prefijo del tipo.
                   Ejemplos: 'productos/alimento.jpg', 'marcas/royal-canin.png'
    
    Returns:
        URL completa de la imagen (DigitalOcean Spaces o static local)
    """
    if not imagen_url:
        return ''
    
    # Obtener configuración de DigitalOcean Spaces
    spaces_url = getattr(settings, 'DO_SPACES_URL', '')
    spaces_cdn_url = getattr(settings, 'DO_SPACES_CDN_URL', '')
    
    # Si está configurado DigitalOcean Spaces
    if spaces_url or spaces_cdn_url:
        base_url = spaces_cdn_url if spaces_cdn_url else spaces_url
        
        # Eliminar trailing slash del base_url
        base_url = base_url.rstrip('/')
        
        # Eliminar leading slash de la imagen_url
        imagen_url = imagen_url.lstrip('/')
        
        # Sin prefijo global, usar directamente la ruta con su prefijo específico
        # Ej: productos/imagen.jpg, marcas/logo.png
        return f"{base_url}/{imagen_url}"
    
    # Si no hay DigitalOcean configurado, usar static local
    # Si la imagen_url ya tiene 'static/' al inicio, no duplicarlo
    if imagen_url.startswith('static/'):
        imagen_url = imagen_url[7:]  # Remover 'static/'
    
    try:
        return static(imagen_url)
    except:
        # Si falla, devolver la URL tal cual
        return f"/static/{imagen_url}"


@register.filter
def has_remote_image(producto):
    """
    Verifica si un producto tiene una imagen almacenada remotamente.
    
    Uso:
        {% if producto|has_remote_image %}
            <img src="{% product_image_url producto.imagen_url %}">
        {% endif %}
    """
    if not producto or not hasattr(producto, 'imagen_url') or not producto.imagen_url:
        return False
    
    imagen_url = producto.imagen_url
    
    # Si comienza con http:// o https://, es una URL remota completa
    if imagen_url.startswith('http://') or imagen_url.startswith('https://'):
        return True
    
    # Si hay DigitalOcean Spaces configurado, consideramos que usa imágenes remotas
    spaces_url = getattr(settings, 'DO_SPACES_URL', '')
    spaces_cdn_url = getattr(settings, 'DO_SPACES_CDN_URL', '')
    
    return bool(spaces_url or spaces_cdn_url)


@register.simple_tag
def spaces_base_url():
    """
    Retorna la URL base de DigitalOcean Spaces.
    Útil para mostrar en formularios o documentación.
    """
    spaces_cdn_url = getattr(settings, 'DO_SPACES_CDN_URL', '')
    spaces_url = getattr(settings, 'DO_SPACES_URL', '')
    
    return spaces_cdn_url if spaces_cdn_url else spaces_url


@register.simple_tag
def is_spaces_configured():
    """
    Verifica si DigitalOcean Spaces está configurado.
    """
    spaces_url = getattr(settings, 'DO_SPACES_URL', '')
    spaces_cdn_url = getattr(settings, 'DO_SPACES_CDN_URL', '')
    
    return bool(spaces_url or spaces_cdn_url)
