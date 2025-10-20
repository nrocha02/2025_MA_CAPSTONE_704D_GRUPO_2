# 📊 Índice de Diagramas - Vista Física

Este archivo contiene el índice de todos los diagramas de la Vista Física.

## 🚀 Arquitectura de Despliegue

### [Diagramas de Despliegue](./diagramas-despliegue.md)

Contiene dos diagramas de arquitectura de despliegue:

#### 1. Despliegue Actual (Desarrollo)

- Django Development Server (puerto 8000)
- PostgreSQL Local (puerto 5432)
- DigitalOcean Spaces (cloud)
- Arquitectura simple para desarrollo

#### 2. Despliegue Propuesto (Producción)

- Load Balancer (Nginx/HAProxy)
- 2 Application Servers (Gunicorn)
- Database Server (PostgreSQL 16)
- Cache Server (Redis)
- CDN (DigitalOcean Spaces CDN)
- External Services (Transbank API)

**Zonas de red:**

- DMZ (Load Balancer)
- Application Tier (App Servers)
- Data Tier (DB, Redis)
- External Services

---

## 🌐 Topología de Red

### [Diagrama de Topología de Red](./diagrama-topologia-red.md)

Segmentación de red y políticas de firewall en producción.

**Subnets:**

- DMZ: 10.0.1.0/24 (Load Balancer)
- Application Tier: 10.0.2.0/24 (App Servers)
- Data Tier: 10.0.3.0/24 (PostgreSQL, Redis)

**Puertos y Protocolos:**
| Puerto | Servicio | Protocolo |
|--------|----------|-----------|
| 80/443 | HTTP/HTTPS | TCP |
| 8000 | Gunicorn | TCP |
| 5432 | PostgreSQL | TCP |
| 6379 | Redis | TCP |
| 22 | SSH | TCP |

**Seguridad:**

- Firewalls por zona
- Principio de mínimo privilegio
- Defensa en profundidad
- Bastion host para administración

---

## 💻 Componentes de Hardware

### [Diagramas de Componentes de Hardware](./diagramas-componentes-hardware.md)

Especificaciones de hardware para cada componente del sistema.

#### Desarrollo

- CPU: 4 cores, 2.5 GHz
- RAM: 8 GB
- Disco: 256 GB SSD
- Red: 100 Mbps

#### Producción

**1. Load Balancer**

- CPU: 2 cores, 2.4 GHz
- RAM: 4 GB
- Disco: 50 GB SSD
- Red: 1 Gbps (2x NIC)

**2. Application Servers (x2)**

- CPU: 4 cores, 2.8 GHz
- RAM: 16 GB
- Disco: 100 GB SSD
- Red: 1 Gbps

**3. Database Server**

- CPU: 8 cores, 3.0 GHz
- RAM: 32 GB
- Disco: 500 GB SSD NVMe RAID 1
- Backup: 1 TB HDD
- Red: 10 Gbps

**4. Cache Server (Redis)**

- CPU: 2 cores, 2.8 GHz
- RAM: 8 GB
- Disco: 50 GB SSD
- Red: 1 Gbps

**Configuraciones incluidas:**

- PostgreSQL tunning
- Redis configuration
- Gunicorn workers
- Nginx settings

**Costos estimados:** $629/mes (DigitalOcean)

---

## 📈 Escalabilidad

### [Diagrama de Escalabilidad](./diagrama-escalabilidad.md)

Estrategias de escalabilidad horizontal y vertical.

**Fases de Crecimiento:**

#### Fase 1 - Small (Actual)

- 1 Load Balancer
- 1-2 App Servers
- 1 Database
- Capacidad: 200 req/s

#### Fase 2 - Medium (10x tráfico)

- 1 Load Balancer
- 4 App Servers
- 1 Database + 1 Read Replica
- 2 Redis (HA)
- Capacidad: 800 req/s

#### Fase 3 - Large (50x tráfico)

- 2 Load Balancers (HA)
- 8 App Servers
- 1 DB Master + 3 Read Replicas
- Redis Cluster (3+3)
- Capacidad: 2,000 req/s

**Puntos de Escalabilidad:**

1. **Application Layer**

   - Stateless workers
   - Auto-scaling basado en métricas
   - Load balancing

2. **Database Layer**

   - Read replicas
   - Connection pooling (PgBouncer)
   - Partitioning por fecha

3. **Cache Layer**

   - Redis Cluster (sharding)
   - Redis Sentinel (HA)
   - Tiered caching (L1, L2, L3)

4. **Storage Layer**
   - DigitalOcean Spaces (escalabilidad infinita)
   - CDN global
   - Pay-as-you-go

**Multi-Region (Futuro):**

- US East + South America
- GeoDNS routing
- Database replication

---

## 📊 Resumen

| Categoría        | Cantidad de Diagramas         |
| ---------------- | ----------------------------- |
| Despliegue       | 2                             |
| Topología de Red | 1                             |
| Hardware         | 5 (desarrollo + 4 producción) |
| Escalabilidad    | 5 (fases + estrategias)       |
| **Total**        | **4 archivos**                |

---

## 🎯 Aspectos Cubiertos

### Infraestructura

- ✅ Arquitectura de despliegue actual y propuesta
- ✅ Segmentación de red y seguridad
- ✅ Especificaciones de hardware detalladas
- ✅ Estrategias de escalabilidad

### Configuración

- ✅ Nginx/HAProxy (Load Balancer)
- ✅ Gunicorn (WSGI Server)
- ✅ PostgreSQL (Database)
- ✅ Redis (Cache)
- ✅ Systemd (Services)

### Operaciones

- ✅ Backup y disaster recovery
- ✅ Monitoreo de infraestructura
- ✅ Auto-scaling policies
- ✅ Costos estimados

---

## 🔗 Relaciones con Otras Vistas

| Vista                   | Relación                                               |
| ----------------------- | ------------------------------------------------------ |
| **Vista Lógica**        | Los componentes se despliegan en la infraestructura    |
| **Vista de Desarrollo** | Los módulos se ejecutan en los servidores              |
| **Vista de Proceso**    | Los procesos requieren recursos de hardware            |
| **Escenarios**          | Los casos de uso demandan capacidad de infraestructura |

---

## 📈 Métricas de Capacidad

| Ambiente          | CPU Total | RAM Total | Disco Total | Servidores |
| ----------------- | --------- | --------- | ----------- | ---------- |
| Desarrollo        | 4 cores   | 8 GB      | 256 GB      | 1          |
| Producción Fase 1 | 18 cores  | 60 GB     | 1.7 TB      | 5          |
| Producción Fase 3 | 80+ cores | 200+ GB   | 5+ TB       | 15+        |

---

**Actualizado**: Octubre 2025  
**Versión**: 1.0
