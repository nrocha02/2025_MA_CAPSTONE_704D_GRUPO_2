# Diagramas de Despliegue

Este archivo contiene los diagramas de arquitectura de despliegue tanto para desarrollo como para producción.

## Despliegue Actual (Desarrollo)

```mermaid
graph TB
    subgraph "Máquina de Desarrollo"
        Dev[Django Development Server<br/>puerto 8000]
        DevDB[(PostgreSQL Local<br/>puerto 5432)]
        DevFiles[Archivos Estáticos Locales]
    end

    subgraph "DigitalOcean Cloud"
        Spaces[DigitalOcean Spaces<br/>nyc3 region<br/>S3-compatible storage]
    end

    Browser[Navegador Web] -->|HTTP| Dev
    Dev -->|TCP/IP| DevDB
    Dev -->|boto3 SDK<br/>HTTPS| Spaces
    Browser -->|HTTPS| Spaces
```

### Características del Entorno de Desarrollo

- **Servidor**: Django Development Server (manage.py runserver)
- **Base de Datos**: PostgreSQL local en puerto 5432
- **Archivos Estáticos**: Servidos directamente por Django
- **Imágenes**: DigitalOcean Spaces (compartido con producción)
- **Puerto**: 8000 (HTTP sin SSL)

---

## Despliegue Propuesto (Producción)

```mermaid
graph TB
    subgraph "Internet"
        Users[Usuarios Web]
        AdminUsers[Administradores]
    end

    subgraph "CDN/Edge"
        CDN[CDN<br/>DigitalOcean Spaces CDN<br/>Distribución global]
    end

    subgraph "DMZ - Load Balancer"
        LB[Nginx/HAProxy<br/>Load Balancer<br/>SSL Termination<br/>puerto 80/443]
    end

    subgraph "Zona de Aplicación"
        subgraph "App Server 1"
            App1[Gunicorn<br/>4 Workers<br/>puerto 8000]
            Django1[Django App]
        end

        subgraph "App Server 2"
            App2[Gunicorn<br/>4 Workers<br/>puerto 8000]
            Django2[Django App]
        end
    end

    subgraph "Zona de Datos"
        subgraph "Database Server"
            DB[(PostgreSQL 16<br/>puerto 5432)]
            DBBackup[(Backup<br/>Daily)]
        end

        subgraph "Cache Server"
            Redis[(Redis<br/>puerto 6379<br/>Sessions & Cache)]
        end
    end

    subgraph "External Services"
        Spaces[DigitalOcean Spaces<br/>Object Storage<br/>Imágenes de Productos]

        Transbank[Transbank API<br/>Payment Gateway<br/>HTTPS]
    end

    Users -->|HTTPS| CDN
    AdminUsers -->|HTTPS| LB
    CDN -->|Cache Miss| LB

    LB -->|Round Robin| App1
    LB -->|Round Robin| App2

    App1 --> Django1
    App2 --> Django2

    Django1 -->|Connection Pool| DB
    Django2 -->|Connection Pool| DB

    Django1 -->|Sessions| Redis
    Django2 -->|Sessions| Redis

    Django1 -->|boto3| Spaces
    Django2 -->|boto3| Spaces

    Django1 -->|API REST| Transbank
    Django2 -->|API REST| Transbank

    DB --> DBBackup
```

### Componentes de Producción

#### 1. Load Balancer

- **Software**: Nginx o HAProxy
- **Funciones**:
  - SSL/TLS termination
  - Load balancing (Round Robin)
  - Health checks
  - Rate limiting

#### 2. Application Servers (x2)

- **WSGI Server**: Gunicorn
- **Workers**: 4 por servidor
- **Alta Disponibilidad**: Redundancia activo-activo

#### 3. Database Server

- **DBMS**: PostgreSQL 16
- **Replicación**: Futura (Master-Replica)
- **Backup**: Diario automático

#### 4. Cache Server

- **Software**: Redis
- **Uso**: Sesiones y cache de aplicación
- **Persistencia**: RDB + AOF

#### 5. CDN

- **Proveedor**: DigitalOcean Spaces CDN
- **Contenido**: Imágenes de productos
- **Distribución**: Global edge locations
