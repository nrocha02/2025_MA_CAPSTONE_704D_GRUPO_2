# Arquitectura de Procesos del Sistema

Este diagrama muestra la arquitectura de procesos del sistema Cordillera Pets eCommerce, incluyendo el flujo desde el cliente web hasta los servicios externos.

```mermaid
graph TB
    subgraph "Navegador Web"
        Browser[Cliente HTTP]
    end

    subgraph "Servidor Web"
        WSGI[WSGI Server<br/>Gunicorn/uWSGI]
        Django[Django Application]
        Worker1[Worker Process 1]
        Worker2[Worker Process 2]
        WorkerN[Worker Process N]
    end

    subgraph "Servicios Externos"
        DB[(PostgreSQL<br/>Connection Pool)]
        Spaces[DigitalOcean Spaces<br/>S3 API]
        Transbank[Transbank API<br/>Payment Gateway]
    end

    Browser <--> WSGI
    WSGI --> Worker1
    WSGI --> Worker2
    WSGI --> WorkerN

    Worker1 --> Django
    Worker2 --> Django
    WorkerN --> Django

    Django <--> DB
    Django <--> Spaces
    Django <--> Transbank
```

## Descripción de Procesos

### 1. Cliente Web (Browser)

- **Proceso**: Navegador del usuario
- **Responsabilidad**: Renderizar UI, ejecutar JavaScript, manejar eventos

### 2. WSGI Server

- **Proceso**: Servidor WSGI (Gunicorn/uWSGI en producción)
- **Responsabilidad**: Gestionar conexiones HTTP, load balancing
- **Workers**: Múltiples procesos para concurrencia

### 3. Django Application

- **Proceso**: Aplicación Django en cada worker
- **Responsabilidad**: Procesar requests, ejecutar lógica de negocio
- **Thread**: Un thread por request (modelo síncrono)

### 4. PostgreSQL

- **Proceso**: Servidor de base de datos
- **Connection Pool**: Pool de conexiones gestionado por PostgreSQL

### 5. DigitalOcean Spaces

- **Proceso**: Servicio externo S3-compatible
- **API**: REST API para upload/download de imágenes
