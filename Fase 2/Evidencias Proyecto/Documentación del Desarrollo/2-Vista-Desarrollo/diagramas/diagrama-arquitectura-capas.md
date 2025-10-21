# Arquitectura en Capas

El sistema implementa una arquitectura en capas clara de 5 niveles.

```mermaid
graph TB
    subgraph "Capa de Presentación"
        Templates[Django Templates]
        StaticFiles[Archivos Estáticos CSS/JS/Images]
        ContextProcessors[Context Processors]
    end

    subgraph "Capa de Aplicación"
        Views[Views - Controladores]
        URLs[URL Routing]
        Forms[Forms - Validación]
        TemplateTags[Template Tags/Filters]
    end

    subgraph "Capa de Lógica de Negocio"
        Models[Models - Entidades]
        Carrito[Carrito - Lógica de Sesión]
        BusinessLogic[Lógica de Negocio]
    end

    subgraph "Capa de Acceso a Datos"
        ORM[Django ORM]
        QuerySets[QuerySets]
        Managers[Model Managers]
    end

    subgraph "Capa de Infraestructura"
        PostgreSQL[(PostgreSQL)]
        DOSpaces[DigitalOcean Spaces]
        Session[Session Storage]
    end

    Templates --> Views
    StaticFiles --> Templates
    ContextProcessors --> Templates

    Views --> URLs
    Views --> Models
    Views --> Carrito
    Views --> BusinessLogic

    Models --> ORM
    Carrito --> Session

    ORM --> PostgreSQL
    BusinessLogic --> DOSpaces
```

## Descripción de Capas

### 1. Capa de Presentación

- **Templates Django**: Vistas HTML dinámicas
- **Archivos estáticos**: CSS, JavaScript, imágenes locales
- **Context Processors**: Datos globales disponibles en todos los templates

### 2. Capa de Aplicación

- **Views**: Controladores que manejan requests HTTP
- **URLs**: Enrutamiento de peticiones
- **Forms**: Validación y procesamiento de formularios
- **Template Tags**: Filtros y tags personalizados

### 3. Capa de Lógica de Negocio

- **Models**: Entidades del dominio con validaciones
- **Carrito**: Gestión del estado del carrito
- **Business Logic**: Reglas de negocio complejas

### 4. Capa de Acceso a Datos

- **Django ORM**: Abstracción de base de datos
- **QuerySets**: Consultas optimizadas
- **Managers**: Lógica de consultas reutilizable

### 5. Capa de Infraestructura

- **PostgreSQL**: Base de datos relacional
- **DigitalOcean Spaces**: Almacenamiento de objetos
- **Session Storage**: Almacenamiento de sesiones
