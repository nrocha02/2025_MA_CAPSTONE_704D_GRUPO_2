"""
Utilidades para almacenamiento de archivos en DigitalOcean Spaces
"""
import os
import uuid
import mimetypes
import logging
from pathlib import Path
from django.conf import settings

# Configurar logger
logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 no está disponible. La carga de imágenes estará deshabilitada.")


class SpacesStorage:
    """
    Clase para manejar la subida de archivos a DigitalOcean Spaces
    Compatible con S3 usando boto3
    """
    
    def __init__(self):
        """Inicializa la conexión con DigitalOcean Spaces"""
        if not BOTO3_AVAILABLE:
            logger.error("boto3 no está instalado")
            raise ImportError(
                "boto3 no está instalado. Instálalo con: pip install boto3"
            )
        
        # Obtener configuración desde settings o variables de entorno
        self.access_key = getattr(settings, 'DO_SPACES_ACCESS_KEY', 
                                  os.getenv('DO_SPACES_ACCESS_KEY', '')).strip()
        self.secret_key = getattr(settings, 'DO_SPACES_SECRET_KEY',
                                  os.getenv('DO_SPACES_SECRET_KEY', '')).strip()
        self.region = getattr(settings, 'DO_SPACES_REGION',
                             os.getenv('DO_SPACES_REGION', 'nyc3')).strip()
        self.bucket_name = getattr(settings, 'DO_SPACES_BUCKET',
                                   os.getenv('DO_SPACES_BUCKET', '')).strip()
        self.endpoint_url = f'https://{self.region}.digitaloceanspaces.com'
        
        logger.info(f"Inicializando SpacesStorage - Bucket: {self.bucket_name}, Region: {self.region}")
        
        # Validar configuración
        if not all([self.access_key, self.secret_key, self.bucket_name]):
            error_msg = (
                "Configuración incompleta de DigitalOcean Spaces. "
                "Asegúrate de configurar DO_SPACES_ACCESS_KEY, "
                "DO_SPACES_SECRET_KEY y DO_SPACES_BUCKET en .env\n\n"
                f"Access Key: {'✅ configurado' if self.access_key else '❌ falta'}\n"
                f"Secret Key: {'✅ configurado' if self.secret_key else '❌ falta'}\n"
                f"Bucket: {'✅ configurado' if self.bucket_name else '❌ falta'}\n"
                f"Region: {self.region}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Verificar que no haya espacios ocultos
        if len(self.access_key) != len(self.access_key.strip()):
            error_msg = "DO_SPACES_ACCESS_KEY contiene espacios al inicio o final. Revisa tu archivo .env"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if len(self.secret_key) != len(self.secret_key.strip()):
            error_msg = "DO_SPACES_SECRET_KEY contiene espacios al inicio o final. Revisa tu archivo .env"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Crear cliente S3
        try:
            self.client = boto3.client(
                's3',
                region_name=self.region,
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )
            logger.info("Cliente de DigitalOcean Spaces creado exitosamente")
        except Exception as e:
            error_msg = (
                f"Error al crear cliente de DigitalOcean Spaces: {str(e)}\n\n"
                "Verifica que las credenciales sean correctas:\n"
                f"- Bucket: {self.bucket_name}\n"
                f"- Region: {self.region}\n"
                f"- Endpoint: {self.endpoint_url}\n\n"
                "Consulta: docs/ERROR_SIGNATURE_DOESNT_MATCH.md"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def generate_unique_filename(self, original_filename, prefix='productos'):
        """
        Genera un nombre único basado en slug + timestamp
        Combina el nombre legible con un identificador único
        
        Args:
            original_filename: Nombre original del archivo
            prefix: Prefijo/carpeta donde se guardará (productos, marcas, etc.)
        
        Returns:
            str: Ruta completa con nombre único pero legible
        """
        import re
        import unicodedata
        from datetime import datetime
        
        # Obtener nombre y extensión
        name = Path(original_filename).stem
        ext = Path(original_filename).suffix.lower()
        
        # Convertir nombre a slug
        slug = name.lower()
        slug = unicodedata.normalize('NFKD', slug)
        slug = slug.encode('ascii', 'ignore').decode('ascii')
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        slug = slug[:30]  # Limitar longitud para dejar espacio al timestamp
        
        # Si el slug quedó vacío, usar un nombre por defecto
        if not slug:
            slug = 'imagen'
        
        # Generar timestamp único (más legible que UUID)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        
        # Combinar slug + timestamp
        unique_name = f"{slug}-{timestamp}{ext}"
        
        # Limpiar prefijo
        prefix = prefix.strip('/')
        
        # Construir ruta completa
        return f"{prefix}/{unique_name}"
    
    def sanitize_filename(self, filename, prefix='productos'):
        """
        Limpia el nombre del archivo y lo convierte en slug
        Transforma el nombre a formato URL-friendly
        
        Args:
            filename: Nombre original del archivo
            prefix: Prefijo/carpeta donde se guardará
        
        Returns:
            str: Ruta completa con nombre en formato slug
        """
        import re
        import unicodedata
        
        # Obtener nombre y extensión
        name = Path(filename).stem
        ext = Path(filename).suffix.lower()
        
        # Convertir a minúsculas
        slug = name.lower()
        
        # Normalizar caracteres Unicode (á -> a, ñ -> n, etc.)
        slug = unicodedata.normalize('NFKD', slug)
        slug = slug.encode('ascii', 'ignore').decode('ascii')
        
        # Reemplazar espacios y guiones bajos por guiones
        slug = re.sub(r'[\s_]+', '-', slug)
        
        # Eliminar caracteres que no sean letras, números o guiones
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        
        # Eliminar guiones múltiples consecutivos
        slug = re.sub(r'-+', '-', slug)
        
        # Eliminar guiones al inicio y final
        slug = slug.strip('-')
        
        # Limitar longitud
        slug = slug[:50]
        
        # Si el slug quedó vacío, usar un nombre por defecto
        if not slug:
            slug = 'imagen'
        
        # Limpiar prefijo
        prefix = prefix.strip('/')
        
        # Construir ruta completa
        return f"{prefix}/{slug}{ext}"
    
    def upload_file(self, file_obj, destination_path=None, prefix='productos',
                   use_unique_name=True, acl='public-read'):
        """
        Sube un archivo a DigitalOcean Spaces
        
        Args:
            file_obj: Objeto de archivo de Django (request.FILES['campo'])
            destination_path: Ruta completa de destino (opcional)
            prefix: Carpeta donde guardar (productos, marcas, etc.)
            use_unique_name: Si True, genera nombre único; si False, sanitiza el original
            acl: Permisos del archivo ('public-read', 'private', etc.)
        
        Returns:
            dict: {
                'success': bool,
                'path': str (ruta del archivo en Spaces),
                'url': str (URL completa del archivo),
                'message': str
            }
        """
        try:
            # Determinar ruta de destino
            if destination_path:
                file_path = destination_path
            else:
                if use_unique_name:
                    file_path = self.generate_unique_filename(file_obj.name, prefix)
                else:
                    file_path = self.sanitize_filename(file_obj.name, prefix)
            
            logger.info(f"Intentando subir archivo: {file_obj.name} -> {file_path}")
            
            # Detectar tipo MIME
            content_type, _ = mimetypes.guess_type(file_obj.name)
            if not content_type:
                content_type = 'application/octet-stream'
            
            logger.debug(f"Content-Type detectado: {content_type}")
            
            # Configuración de subida
            extra_args = {
                'ACL': acl,
                'ContentType': content_type,
            }
            
            # Agregar caché para imágenes
            if content_type.startswith('image/'):
                extra_args['CacheControl'] = 'max-age=31536000'  # 1 año
            
            logger.debug(f"Subiendo a bucket: {self.bucket_name}, path: {file_path}")
            
            # Subir archivo
            self.client.upload_fileobj(
                file_obj,
                self.bucket_name,
                file_path,
                ExtraArgs=extra_args
            )
            
            logger.info(f"Archivo subido exitosamente: {file_path}")
            
            # Construir URL completa
            cdn_url = getattr(settings, 'DO_SPACES_CDN_URL', '')
            if cdn_url:
                base_url = cdn_url.rstrip('/')
            else:
                base_url = f"https://{self.bucket_name}.{self.region}.digitaloceanspaces.com"
            
            full_url = f"{base_url}/{file_path}"
            logger.info(f"URL completa: {full_url}")
            
            return {
                'success': True,
                'path': file_path,
                'url': full_url,
                'message': 'Archivo subido exitosamente'
            }
            
        except ClientError as e:
            error_msg = f'Error al subir archivo: {str(e)}'
            logger.error(f"ClientError: {error_msg}")
            logger.error(f"Detalles del error: {e.response if hasattr(e, 'response') else 'Sin detalles'}")
            return {
                'success': False,
                'path': None,
                'url': None,
                'message': error_msg
            }
        except Exception as e:
            error_msg = f'Error inesperado: {str(e)}'
            logger.error(f"Exception: {error_msg}", exc_info=True)
            return {
                'success': False,
                'path': None,
                'url': None,
                'message': error_msg
            }
    
    def delete_file(self, file_path):
        """
        Elimina un archivo de DigitalOcean Spaces
        
        Args:
            file_path: Ruta del archivo a eliminar
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            logger.info(f"Intentando eliminar archivo: {file_path}")
            
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            
            logger.info(f"Archivo eliminado exitosamente: {file_path}")
            
            return {
                'success': True,
                'message': 'Archivo eliminado exitosamente'
            }
            
        except ClientError as e:
            error_msg = f'Error al eliminar archivo: {str(e)}'
            logger.error(f"ClientError al eliminar {file_path}: {error_msg}")
            return {
                'success': False,
                'message': error_msg
            }
        except Exception as e:
            error_msg = f'Error inesperado: {str(e)}'
            logger.error(f"Exception al eliminar {file_path}: {error_msg}", exc_info=True)
            return {
                'success': False,
                'message': error_msg
            }
    
    def file_exists(self, file_path):
        """
        Verifica si un archivo existe en Spaces
        
        Args:
            file_path: Ruta del archivo
        
        Returns:
            bool: True si existe, False si no
        """
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
            logger.debug(f"Archivo existe: {file_path}")
            return True
        except ClientError:
            logger.debug(f"Archivo no existe: {file_path}")
            return False


def is_spaces_configured():
    """
    Verifica si DigitalOcean Spaces está configurado correctamente
    
    Returns:
        bool: True si está configurado, False si no
    """
    if not BOTO3_AVAILABLE:
        return False
    
    access_key = getattr(settings, 'DO_SPACES_ACCESS_KEY', 
                        os.getenv('DO_SPACES_ACCESS_KEY', '')).strip()
    secret_key = getattr(settings, 'DO_SPACES_SECRET_KEY',
                        os.getenv('DO_SPACES_SECRET_KEY', '')).strip()
    bucket = getattr(settings, 'DO_SPACES_BUCKET',
                    os.getenv('DO_SPACES_BUCKET', '')).strip()
    
    return all([access_key, secret_key, bucket])


def upload_product_image(file_obj, use_unique_name=True):
    """
    Función auxiliar para subir imágenes de productos
    
    Args:
        file_obj: Archivo de imagen
        use_unique_name: Si True, genera nombre único
    
    Returns:
        dict: Resultado de la subida
    """
    if not is_spaces_configured():
        logger.warning("Intento de subir imagen sin configuración de Spaces")
        return {
            'success': False,
            'path': None,
            'url': None,
            'message': 'DigitalOcean Spaces no está configurado'
        }
    
    try:
        logger.info(f"Subiendo imagen de producto: {file_obj.name}")
        storage = SpacesStorage()
        result = storage.upload_file(
            file_obj,
            prefix='productos',
            use_unique_name=use_unique_name
        )
        return result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error al subir imagen de producto: {error_msg}", exc_info=True)
        return {
            'success': False,
            'path': None,
            'url': None,
            'message': error_msg
        }


def delete_product_image(imagen_url):
    """
    Función auxiliar para eliminar imágenes de productos
    
    Args:
        imagen_url: Ruta de la imagen (ej: productos/imagen.jpg)
    
    Returns:
        dict: Resultado de la eliminación
    """
    if not imagen_url:
        return {
            'success': False,
            'message': 'No hay imagen para eliminar'
        }
    
    # Si la URL es completa (http/https), no eliminar (no está en nuestro Space)
    if imagen_url.startswith('http://') or imagen_url.startswith('https://'):
        logger.info(f"URL externa detectada, no se eliminará: {imagen_url}")
        return {
            'success': False,
            'message': 'URL externa, no se puede eliminar'
        }
    
    if not is_spaces_configured():
        logger.warning("Intento de eliminar imagen sin configuración de Spaces")
        return {
            'success': False,
            'message': 'DigitalOcean Spaces no está configurado'
        }
    
    try:
        logger.info(f"Eliminando imagen de producto: {imagen_url}")
        storage = SpacesStorage()
        result = storage.delete_file(imagen_url)
        return result
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error al eliminar imagen de producto: {error_msg}", exc_info=True)
        return {
            'success': False,
            'message': error_msg
        }


def upload_brand_logo(file_obj, use_unique_name=True):
    """
    Función auxiliar para subir logos de marcas
    
    Args:
        file_obj: Archivo de imagen
        use_unique_name: Si True, genera nombre único
    
    Returns:
        dict: Resultado de la subida
    """
    if not is_spaces_configured():
        return {
            'success': False,
            'path': None,
            'url': None,
            'message': 'DigitalOcean Spaces no está configurado'
        }
    
    try:
        storage = SpacesStorage()
        return storage.upload_file(
            file_obj,
            prefix='marcas',
            use_unique_name=use_unique_name
        )
    except Exception as e:
        return {
            'success': False,
            'path': None,
            'url': None,
            'message': str(e)
        }
