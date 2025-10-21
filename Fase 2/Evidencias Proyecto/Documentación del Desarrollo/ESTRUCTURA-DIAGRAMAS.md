# 📁 Estructura de Diagramas - CordilleraPets

Este documento describe la organización de todos los diagramas del proyecto en subcarpetas temáticas.

## 🎯 Objetivo de la Organización

Los diagramas han sido organizados en subcarpetas para:

- ✅ Facilitar la navegación y búsqueda
- ✅ Agrupar diagramas por tipo/categoría
- ✅ Mantener una estructura escalable
- ✅ Mejorar la mantenibilidad de la documentación

---

## 📂 Estructura Completa

```
Documentación del Desarrollo/
│
├── 1-Vista-Lógica/
│   ├── DIAGRAMAS.md                    # Índice de diagramas
│   ├── README.md
│   └── diagramas/                      # 📁 Carpeta de diagramas
│       ├── README.md                   # Índice de la carpeta
│       ├── diagrama-clases-principal.md
│       ├── diagrama-componentes-principales.md
│       ├── diagrama-modelo-dominio.md
│       └── diagrama-subsistemas.md
│       └── (Total: 4 diagramas)
│
├── 2-Vista-Desarrollo/
│   ├── DIAGRAMAS.md
│   ├── README.md
│   └── diagramas/                      # 📁 Carpeta de diagramas
│       ├── README.md
│       ├── diagrama-arquitectura-capas.md
│       ├── diagrama-modulos-django.md
│       └── diagrama-paquetes.md
│       └── (Total: 3 diagramas)
│
├── 3-Vista-Proceso/
│   ├── DIAGRAMAS.md
│   ├── README.md
│   ├── diagramas-actividades/          # 📁 Diagramas de actividades
│   │   ├── README.md
│   │   ├── diagrama-actividad-autenticacion.md
│   │   ├── diagrama-actividad-compra-completa.md
│   │   ├── diagrama-actividad-gestion-inventario.md
│   │   ├── diagrama-actividad-gestion-productos.md
│   │   ├── diagrama-actividad-navegacion-catalogo.md
│   │   └── RESUMEN-DIAGRAMAS-ACTIVIDADES.md
│   │   └── (Total: 5 diagramas + 1 resumen)
│   │
│   ├── diagramas-arquitectura/         # 📁 Diagramas de arquitectura
│   │   ├── README.md
│   │   └── diagrama-arquitectura-procesos.md
│   │   └── (Total: 1 diagrama)
│   │
│   ├── diagramas-flujos/              # 📁 Diagramas de flujo
│   │   ├── README.md
│   │   ├── diagrama-flujo-carrito.md
│   │   ├── diagrama-flujo-catalogo.md
│   │   ├── diagrama-flujo-checkout.md
│   │   └── diagrama-flujo-crear-producto.md
│   │   └── (Total: 4 diagramas)
│   │
│   ├── diagramas-secuencia/           # 📁 Diagramas de secuencia
│   │   ├── README.md
│   │   ├── diagrama-secuencia-actualizar-carrito.md
│   │   └── diagrama-secuencia-busqueda.md
│   │   └── (Total: 2 diagramas)
│   │
│   ├── diagramas-estados/             # 📁 Diagramas de estados
│   │   ├── README.md
│   │   └── diagramas-estados.md
│   │   └── (Total: 1 archivo con 3 diagramas)
│   │
│   └── diagramas-concurrencia/        # 📁 Diagramas de concurrencia
│       ├── README.md
│       ├── diagrama-concurrencia.md
│       └── diagrama-sincronizacion.md
│       └── (Total: 2 diagramas)
│
├── 4-Vista-Física/
│   ├── DIAGRAMAS.md
│   ├── README.md
│   └── diagramas/                      # 📁 Carpeta de diagramas
│       ├── README.md
│       ├── diagrama-escalabilidad.md
│       ├── diagrama-topologia-red.md
│       ├── diagramas-componentes-hardware.md
│       └── diagramas-despliegue.md
│       └── (Total: 4 diagramas)
│
└── 5-Escenarios/
    ├── DIAGRAMAS.md
    ├── README.md
    ├── diagramas/                      # 📁 Diagramas de casos de uso
    │   ├── README.md
    │   ├── diagrama-actores.md
    │   ├── diagrama-casos-uso.md
    │   └── diagramas-flujos.md
    │   └── (Total: 3 diagramas)
    │
    └── escenarios/                     # 📁 Escenarios detallados
        ├── README.md
        ├── escenario-compra-completa.md
        ├── escenario-concurrencia-stock.md
        └── escenario-gestion-productos.md
        └── (Total: 3 escenarios)
```

---

## 📊 Resumen por Vista

| Vista                  | Subcarpetas | Diagramas | READMEs |
| ---------------------- | ----------- | --------- | ------- |
| **1-Vista-Lógica**     | 1           | 4         | 1       |
| **2-Vista-Desarrollo** | 1           | 3         | 1       |
| **3-Vista-Proceso**    | 6           | 15        | 6       |
| **4-Vista-Física**     | 1           | 4         | 1       |
| **5-Escenarios**       | 2           | 6         | 2       |
| **TOTAL**              | **11**      | **32**    | **11**  |

---

## 🗂️ Convenciones de Nomenclatura

### Carpetas

- `diagramas/` - Para vistas con una sola categoría de diagramas
- `diagramas-[tipo]/` - Para vistas con múltiples categorías
  - Ejemplos: `diagramas-actividades/`, `diagramas-flujos/`, `diagramas-secuencia/`
- `escenarios/` - Para documentos de escenarios detallados

### Archivos

- `diagrama-[nombre].md` - Diagramas individuales
- `diagramas-[nombre].md` - Archivos que contienen múltiples diagramas relacionados
- `escenario-[nombre].md` - Escenarios detallados
- `README.md` - Índice de cada subcarpeta
- `DIAGRAMAS.md` - Índice maestro en cada vista
- `RESUMEN-[nombre].md` - Documentos resumen

---

## 📑 Archivos de Índice

Cada vista y subcarpeta tiene archivos de índice para facilitar la navegación:

### Nivel 1: Vista Principal

- `DIAGRAMAS.md` - Índice maestro con descripción de todos los diagramas
- `README.md` - Documentación completa de la vista

### Nivel 2: Subcarpetas

- `README.md` - Índice específico con lista de diagramas en la carpeta

### Estructura de DIAGRAMAS.md

Todos los archivos `DIAGRAMAS.md` incluyen:

1. **Título**: `# 📊 Índice de Diagramas - [Nombre de Vista]`
2. **Enlaces a subcarpetas**: 📁 **[Ver carpeta completa](./carpeta/)**
3. **Secciones por categoría**: Agrupación lógica de diagramas
4. **Descripción de cada diagrama**: Resumen de contenido y propósito
5. **Resumen**: Tabla con estadísticas
6. **Relaciones**: Vínculos con otras vistas

---

## 🔗 Sistema de Referencias

### Referencias Absolutas vs Relativas

Todos los links usan rutas relativas desde el archivo actual:

```markdown
<!-- Desde DIAGRAMAS.md a subcarpeta -->

[Diagrama X](./diagramas/diagrama-x.md)

<!-- Desde README.md de subcarpeta al diagrama -->

[Diagrama X](./diagrama-x.md)

<!-- Desde diagrama a DIAGRAMAS.md padre -->

[← Volver al índice](../DIAGRAMAS.md)
```

### Cross-Referencias entre Vistas

```markdown
<!-- Desde Vista-Proceso a Vista-Lógica -->

[Ver modelo de dominio](../1-Vista-Lógica/diagramas/diagrama-modelo-dominio.md)
```

---

## ✅ Ventajas de esta Estructura

### 1. **Escalabilidad**

- Fácil agregar nuevos diagramas sin saturar carpetas raíz
- Nuevas categorías se pueden añadir sin afectar la estructura existente

### 2. **Mantenibilidad**

- Cambios en un tipo de diagrama no afectan otros
- Actualizaciones focalizadas por categoría

### 3. **Navegabilidad**

- Estructura clara y predecible
- READMEs en cada nivel facilitan el descubrimiento
- Índices maestros en cada vista

### 4. **Documentación Autodescriptiva**

- Nombres de carpetas descriptivos
- READMEs con contexto completo
- Enlaces bidireccionales (padre ↔ hijo)

### 5. **Separación de Responsabilidades**

- Cada subcarpeta tiene un propósito claro
- Vista de Proceso bien organizada con 6 categorías distintas

---

## 🎯 Uso Recomendado

### Para Desarrolladores Nuevos

1. Empezar por el `INDICE.md` de la raíz
2. Leer el `README.md` de cada vista
3. Consultar `DIAGRAMAS.md` para vista general
4. Profundizar en subcarpetas según necesidad

### Para Documentación

1. Crear nuevo diagrama en la subcarpeta apropiada
2. Actualizar el `README.md` de la subcarpeta
3. Actualizar el `DIAGRAMAS.md` de la vista
4. Verificar enlaces funcionan correctamente

### Para Búsqueda Rápida

```bash
# Buscar todos los diagramas de actividades
find . -path "*/diagramas-actividades/*.md"

# Buscar por nombre
grep -r "diagrama-flujo-carrito" --include="*.md"

# Listar todos los READMEs
find . -name "README.md" -type f
```

---

## 📈 Métricas del Proyecto

| Métrica                   | Cantidad |
| ------------------------- | -------- |
| **Total de Vistas**       | 5        |
| **Subcarpetas creadas**   | 11       |
| **Diagramas totales**     | 32       |
| **Archivos README**       | 11       |
| **Archivos DIAGRAMAS.md** | 5        |
| **Escenarios detallados** | 3        |

---

## 🔄 Historial de Cambios

| Fecha    | Versión | Cambios                                      |
| -------- | ------- | -------------------------------------------- |
| Oct 2025 | 1.0     | ✅ Organización inicial en subcarpetas       |
| Oct 2025 | 1.1     | ✅ Creación de READMEs en todas las carpetas |
| Oct 2025 | 1.2     | ✅ Actualización de todos los DIAGRAMAS.md   |

---

## 📝 Mantenimiento Futuro

### Al Agregar Nuevos Diagramas

1. Identificar la vista y categoría apropiada
2. Crear el archivo en la subcarpeta correspondiente
3. Actualizar el README.md de la subcarpeta
4. Actualizar el DIAGRAMAS.md de la vista
5. Verificar que todos los enlaces funcionen

### Al Crear Nueva Categoría

1. Crear nueva subcarpeta con nombre descriptivo
2. Crear README.md en la subcarpeta
3. Agregar sección en DIAGRAMAS.md
4. Documentar en este archivo (ESTRUCTURA-DIAGRAMAS.md)

---

**Actualizado**: Octubre 2025  
**Versión**: 1.2  
**Autor**: Equipo CordilleraPets
