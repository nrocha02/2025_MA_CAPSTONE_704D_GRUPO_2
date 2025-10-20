# Documentación Arquitectónica - Cordillera Pets eCommerce

## Modelo Arquitectónico 4+1

Este documento contiene la arquitectura completa del sistema de eCommerce Cordillera Pets utilizando el modelo arquitectónico 4+1 de Philippe Kruchten.

## Información del Proyecto

- **Nombre**: Cordillera Pets eCommerce Platform
- **Versión**: 0.0.1
- **Descripción**: Plataforma web eCommerce para venta de productos para mascotas
- **Tecnología**: Django 5.2, PostgreSQL, DigitalOcean Spaces
- **Autores**:
  - Janiz Carreño (jan.carreno@duocuc.cl)
  - Carolina Sanchez (caro.sanchez@duocuc.cl)
  - Nicolás Rocha (nico.rocha@duocuc.cl)

## Estructura de la Documentación

### 1. Vista Lógica

Describe la funcionalidad que el sistema proporciona a los usuarios finales. Muestra los componentes principales del sistema y sus relaciones.

📁 [Ver Vista Lógica](./1-Vista-Lógica/)

### 2. Vista de Desarrollo

Describe la organización del código, los módulos, las capas y los paquetes del sistema.

📁 [Ver Vista de Desarrollo](./2-Vista-Desarrollo/)

### 3. Vista de Proceso

Describe los procesos del sistema, la concurrencia, la distribución y los aspectos dinámicos del sistema.

📁 [Ver Vista de Proceso](./3-Vista-Proceso/)

### 4. Vista Física

Describe el mapeo del software en el hardware y muestra la distribución física del sistema.

📁 [Ver Vista Física](./4-Vista-Física/)

### 5. Escenarios (Casos de Uso)

Describe los casos de uso principales que ilustran la arquitectura y validan el diseño.

📁 [Ver Escenarios](./5-Escenarios/)

## Resumen del Sistema

**Cordillera Pets** es una plataforma de comercio electrónico especializada en productos para mascotas. El sistema permite:

- Catálogo de productos con categorías y filtros
- Gestión de carrito de compras
- Proceso de checkout y pagos
- Panel de administración (dashboard) para gestión de productos, categorías y marcas
- Soporte para diferentes tipos de clientes (personas, empresas, invitados)
- Almacenamiento de imágenes en DigitalOcean Spaces
- Gestión de inventario y stock
- Sistema de pedidos y documentos tributarios

## Tecnologías Principales

- **Backend**: Django 5.2 (Python 3.12+)
- **Base de Datos**: PostgreSQL
- **Frontend**: Django Templates, Bootstrap 5
- **Almacenamiento**: DigitalOcean Spaces (S3-compatible)
- **Dependencias Principales**:
  - Pillow (procesamiento de imágenes)
  - psycopg (conector PostgreSQL)
  - django-bootstrap5
  - python-dotenv
  - boto3 (AWS SDK)

## Arquitectura General

El sistema sigue el patrón **MTV (Model-Template-View)** de Django:

- **Models**: Definición de entidades de negocio y acceso a datos
- **Templates**: Presentación y UI
- **Views**: Lógica de negocio y control de flujo

### Aplicaciones Django

1. **ventas**: Módulo público de catálogo y productos
2. **carrito**: Gestión del carrito de compras
3. **dashboard**: Panel administrativo
4. **checkout**: Proceso de pago (en desarrollo)

## Principios Arquitectónicos

1. **Separación de Responsabilidades**: Cada aplicación Django tiene una responsabilidad específica
2. **Modelos No Administrados**: Los modelos están marcados como `managed=False` para que Django no altere el esquema de BD existente
3. **Almacenamiento Externo**: Imágenes almacenadas en DigitalOcean Spaces para escalabilidad
4. **Validación en Base de Datos**: Constraints y checks definidos a nivel de BD y replicados en Django
5. **Diseño RESTful**: URLs semánticas y separación clara entre recursos

## Convenciones

- **Idioma**: Código y documentación en español/inglés mixto
- **Nomenclatura BD**: snake_case
- **Nomenclatura Python**: PascalCase para clases, snake_case para funciones/variables
- **Templates**: Estructura jerárquica con plantillas base por aplicación

---

**Última actualización**: Octubre 2025
