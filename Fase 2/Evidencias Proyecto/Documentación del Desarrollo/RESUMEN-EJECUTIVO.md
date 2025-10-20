# Resumen Ejecutivo - Arquitectura Cordillera Pets

## 📋 Documento de Referencia Rápida

---

## 🎯 Visión General del Proyecto

**Nombre**: Cordillera Pets eCommerce Platform  
**Versión**: 0.0.1  
**Tipo**: Plataforma de comercio electrónico B2C/B2B  
**Dominio**: Venta de productos para mascotas  
**Arquitectura**: Django MTV + PostgreSQL + Cloud Storage

---

## 🏗️ Arquitectura en Resumen

### Stack Tecnológico

| Capa                  | Tecnología                   | Versión       |
| --------------------- | ---------------------------- | ------------- |
| **Backend Framework** | Django                       | 5.2.x         |
| **Lenguaje**          | Python                       | 3.12+         |
| **Base de Datos**     | PostgreSQL                   | 16.x          |
| **Cache/Sessions**    | Redis                        | 7.x (futuro)  |
| **Almacenamiento**    | DigitalOcean Spaces          | S3-compatible |
| **Frontend**          | Django Templates + Bootstrap | 5.x           |
| **Servidor App**      | Gunicorn                     | -             |
| **Load Balancer**     | Nginx                        | -             |
| **Pagos**             | Transbank API                | Webpay Plus   |

### Aplicaciones Django

```
pets/                    # Proyecto principal
├── ventas/             # Catálogo público (15+ modelos)
├── carrito/            # Shopping cart (session-based)
├── dashboard/          # Panel administrativo (CRUD)
└── checkout/           # Proceso de pago (en desarrollo)
```

---

## 📊 Modelo de Datos - Entidades Principales

### Jerarquía de Entidades

```
Productos
├── Producto (producto_id)
├── Categoria (categoria_id) - Jerárquica 2 niveles
├── Marca (marca_id)
├── MovimientoStock
└── MovimientoEstado

Clientes (XOR)
├── ClientePersona (cliente_persona_id)
├── ClienteEmpresa (cliente_empresa_id)
└── SesionInvitado (cliente_invitado_id)

Pedidos
├── Pedido (pedido_id)
│   ├── PedidoItem
│   ├── Pago
│   ├── PedidoRegistro
│   └── DocumentoTributario
└── Direccion
```

### Estadísticas del Modelo

- **Total de Tablas**: 18
- **Relaciones**: 25+
- **Constraints**: 15+
- **Índices**: 20+
- **Tipos ENUM**: 6

---

## 🔄 Flujos de Proceso Críticos

### 1. Flujo de Compra (E2E)

```
Usuario → Catálogo → Producto → Carrito → Checkout → Pago → Confirmación
  ↓         ↓          ↓          ↓          ↓        ↓         ↓
 GET     Filtrar    Detalle   Session   Validar  Transbank  Pedido
               └─> Buscar     └─> AJAX    Stock     API    + Boleta
```

**Tiempo Esperado**: 2-5 minutos  
**Pasos**: 15-20  
**Sistemas Involucrados**: Django, PostgreSQL, Redis, Transbank, Spaces

### 2. Flujo de Administración

```
Admin → Login → Dashboard → CRUD Producto → Upload Imagen → Guardar
   ↓      ↓         ↓            ↓               ↓            ↓
  Auth  Session  Métricas   Formulario    boto3→Spaces   PostgreSQL
```

**Tiempo Esperado**: 30-60 segundos  
**Sistemas Involucrados**: Django, PostgreSQL, DigitalOcean Spaces

---

## 📈 Escalabilidad y Performance

### Capacidad Actual (Desarrollo)

- **Usuarios Concurrentes**: 10-20
- **Requests/segundo**: 50
- **Response Time**: <200ms
- **Almacenamiento**: Local + Spaces

### Capacidad Objetivo (Producción)

| Métrica                   | Objetivo           |
| ------------------------- | ------------------ |
| **Usuarios Concurrentes** | 100-500            |
| **Requests/segundo**      | 200-500            |
| **Response Time (p95)**   | <500ms             |
| **Uptime**                | 99.5%              |
| **Almacenamiento**        | Ilimitado (Spaces) |
| **Database Size**         | 100 GB+            |

### Estrategia de Escalado

```
Fase 1: Single Server (Actual)
  └─> 1 App Server + PostgreSQL + Spaces

Fase 2: Load Balanced (0-1000 usuarios)
  └─> 2 App Servers + PostgreSQL + Redis + Spaces

Fase 3: High Availability (1000-10000 usuarios)
  └─> 4+ App Servers + DB Master/Replica + Redis Cluster
```

---

## 🔒 Seguridad

### Medidas Implementadas

✅ **Autenticación y Autorización**

- Django authentication system
- Session-based auth para admin
- CSRF protection habilitado

✅ **Protección de Datos**

- Parametrized queries (Django ORM)
- Input validation
- XSS protection (template auto-escape)

✅ **Transacciones ACID**

- Row-level locks para stock
- Transacciones atómicas
- Rollback automático en errores

✅ **Seguridad de Red (Producción)**

- SSL/TLS (HTTPS)
- Firewall segmentación
- VPC para servicios internos

### Medidas Pendientes

⚠️ Rate limiting  
⚠️ 2FA para admin  
⚠️ Logs de auditoría  
⚠️ Encryption at rest

---

## 💾 Persistencia y Backup

### Estrategia de Datos

| Tipo de Dato              | Storage                      | Backup                          | Retención  |
| ------------------------- | ---------------------------- | ------------------------------- | ---------- |
| **Datos Transaccionales** | PostgreSQL                   | Daily full + Hourly incremental | 30 días    |
| **Imágenes Productos**    | DigitalOcean Spaces          | Replicación automática          | Permanente |
| **Sesiones**              | Django Sessions (DB) → Redis | No requerido                    | 24 horas   |
| **Logs**                  | Filesystem → ElasticSearch   | Rolling logs                    | 30 días    |

### RPO/RTO

- **RPO (Recovery Point Objective)**: 1 hora
- **RTO (Recovery Time Objective)**: 1 hora
- **Backup Location**: AWS S3 (región diferente)

---

## 🎨 Patrones de Diseño Aplicados

### Arquitectónicos

- ✅ **MTV (Model-Template-View)**: Patrón Django
- ✅ **Layered Architecture**: 5 capas (Presentación → Infraestructura)
- ✅ **Repository Pattern**: Django ORM como repositorio
- ✅ **Front Controller**: Django URL dispatcher

### Código

- ✅ **Strategy Pattern**: Tipos de clientes (Persona/Empresa/Invitado)
- ✅ **Observer Pattern**: Registros de movimientos
- ✅ **Singleton Pattern**: Context processors
- ✅ **Template Method**: Django class-based views (futuro)

---

## 📐 Decisiones Arquitectónicas Clave

### DAR-01: Modelos No Administrados

**Decisión**: Marcar todos los modelos como `managed=False`

**Razón**:

- Schema de BD ya existe y es administrado externamente
- Django solo debe leer/escribir datos, no modificar estructura
- Permite constraints complejos definidos en PostgreSQL

**Implicaciones**:

- Migraciones de Django no modifican BD
- Schema changes requieren scripts SQL manuales
- Mayor control sobre BD

---

### DAR-02: Almacenamiento Externo para Imágenes

**Decisión**: DigitalOcean Spaces en lugar de filesystem local

**Razón**:

- Escalabilidad ilimitada
- CDN integrado para distribución global
- No consumir espacio en servidores de aplicación
- Facilita scaling horizontal

**Implicaciones**:

- Dependencia de servicio externo
- Costos variables por almacenamiento y transferencia
- Latencia adicional en upload (mitigada por CDN)

---

### DAR-03: Carrito Basado en Sesión

**Decisión**: Session storage en lugar de base de datos

**Razón**:

- Mejor performance (no queries a BD por cada operación)
- Simplicidad para usuarios no registrados
- Limpieza automática (session expiry)

**Implicaciones**:

- No persiste entre dispositivos
- Se pierde si sesión expira
- Migración a Redis recomendada para producción

---

### DAR-04: Transacciones ACID para Pedidos

**Decisión**: Wrapping completo de checkout en transacción

**Razón**:

- Garantizar integridad de datos
- Evitar stock negativo o pedidos inconsistentes
- Rollback automático en errores

**Implicaciones**:

- Row locks pueden causar contención bajo alta carga
- Requiere connection pooling adecuado
- Necesita monitoreo de deadlocks

---

## 🔧 Configuraciones Críticas

### PostgreSQL (Producción)

```ini
max_connections = 200
shared_buffers = 8GB
effective_cache_size = 24GB
work_mem = 64MB
maintenance_work_mem = 2GB
```

### Gunicorn

```python
workers = 4  # (2 x CPU cores) + 1
worker_class = "sync"
timeout = 60
keepalive = 5
```

### Nginx Load Balancer

```nginx
upstream django_app {
    least_conn;
    server 10.0.2.10:8000;
    server 10.0.2.11:8000;
}
```

---

## 📊 Métricas de Monitoreo Clave

### Application Metrics

| Métrica             | Alerta    | Crítico   |
| ------------------- | --------- | --------- |
| Response Time (p95) | >500ms    | >1000ms   |
| Error Rate          | >1%       | >5%       |
| Throughput          | <50 req/s | <10 req/s |
| Active Sessions     | -         | >1000     |

### Infrastructure Metrics

| Métrica         | Alerta | Crítico |
| --------------- | ------ | ------- |
| CPU Utilization | >70%   | >90%    |
| Memory Usage    | >80%   | >95%    |
| Disk Usage      | >80%   | >95%    |
| DB Connections  | >150   | >180    |

---

## 🚀 Roadmap Técnico

### Q4 2025

- ✅ Implementación base (MVP)
- ✅ Integración Transbank
- ✅ Dashboard administrativo
- ⚠️ Completar módulo checkout

### Q1 2026

- ⬜ Migración a Redis para sesiones
- ⬜ Implementar cache layer
- ⬜ Autenticación de usuarios (registro/login)
- ⬜ Historial de pedidos

### Q2 2026

- ⬜ Optimización de performance
- ⬜ Setup CI/CD
- ⬜ Monitoreo completo (Prometheus + Grafana)
- ⬜ Testing automatizado

### Q3 2026

- ⬜ Multi-region deployment
- ⬜ API REST para mobile
- ⬜ Notificaciones por email
- ⬜ Sistema de recomendaciones

---

## 📚 Referencias Rápidas

### Documentación del Proyecto

- **Vista Lógica**: [1-Vista-Lógica/README.md](./1-Vista-Lógica/README.md)
- **Vista Desarrollo**: [2-Vista-Desarrollo/README.md](./2-Vista-Desarrollo/README.md)
- **Vista Proceso**: [3-Vista-Proceso/README.md](./3-Vista-Proceso/README.md)
- **Vista Física**: [4-Vista-Física/README.md](./4-Vista-Física/README.md)
- **Escenarios**: [5-Escenarios/README.md](./5-Escenarios/README.md)
- **Índice Completo**: [INDICE.md](./INDICE.md)

### Documentación Externa

- Django: https://docs.djangoproject.com/
- PostgreSQL: https://www.postgresql.org/docs/
- DigitalOcean Spaces: https://docs.digitalocean.com/products/spaces/
- Transbank: https://www.transbankdevelopers.cl/

---

## 👥 Contacto

**Equipo de Desarrollo**:

- Janiz Carreño - jan.carreno@duocuc.cl
- Carolina Sanchez - caro.sanchez@duocuc.cl
- Nicolás Rocha - nico.rocha@duocuc.cl

**Institución**: DuocUC  
**Proyecto**: Capstone 2025

---

**Última actualización**: Octubre 2025  
**Versión del documento**: 1.0
