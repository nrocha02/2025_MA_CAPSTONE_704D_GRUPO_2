# Diagrama de Actividad: Navegación y Búsqueda en Catálogo

## Descripción

Este diagrama de actividad muestra el flujo detallado de navegación por el catálogo de productos, incluyendo búsqueda, filtrado, y visualización de detalles de productos.

## Diagrama

```mermaid
flowchart TD
    Start([Inicio]) --> AccederSitio[Acceder al Sitio Web]
    AccederSitio --> PaginaInicio[Mostrar Página Inicio]
    PaginaInicio --> AccionInicial{¿Qué desea hacer?}

    %% ========== FLUJO: VER CATÁLOGO COMPLETO ==========
    AccionInicial -->|Ver Catálogo| CargarCatalogo[GET /catalogo/]
    CargarCatalogo --> QueryProductosActivos[Query: Productos Activos]
    QueryProductosActivos --> SelectRelated[SELECT_RELATED<br/>Categoría, Marca]
    SelectRelated --> CargarCategorias[Cargar Lista Categorías]
    CargarCategorias --> CargarMarcas[Cargar Lista Marcas]
    CargarMarcas --> RenderCatalogo[Render Template Catálogo]
    RenderCatalogo --> MostrarGrid[Mostrar Grid de Productos]
    MostrarGrid --> CargarImagenesCDN[Cargar Imágenes desde CDN]
    CargarImagenesCDN --> MostrarCatalogo[Catálogo Visible]

    %% ========== FLUJO: BUSCAR POR TEXTO ==========
    AccionInicial -->|Buscar Producto| IngresarTermino[Ingresar Término Búsqueda]
    IngresarTermino --> ValidarTermino{¿Término Válido?}

    ValidarTermino -->|No - Vacío| ErrorTermino[Mensaje: Ingrese Término]
    ErrorTermino --> IngresarTermino

    ValidarTermino -->|Sí| EnviarBusqueda[Submit Formulario]
    EnviarBusqueda --> QueryBusqueda[Query con ICONTAINS]
    QueryBusqueda --> BuscarNombre[Buscar en Nombre]
    BuscarNombre --> BuscarDescripcion[Buscar en Descripción]
    BuscarDescripcion --> VerificarResultados{¿Hay Resultados?}

    VerificarResultados -->|No| MostrarSinResultados[Mensaje: Sin Resultados]
    MostrarSinResultados --> SugerirOtraBusqueda[Sugerir Términos Similares]
    SugerirOtraBusqueda --> MostrarCatalogo

    VerificarResultados -->|Sí| ContarResultados[Contar Resultados]
    ContarResultados --> MostrarResultados[Mostrar Lista Resultados]
    MostrarResultados --> MostrarCatalogo

    %% ========== FLUJO: FILTRAR POR CATEGORÍA ==========
    MostrarCatalogo --> AccionCatalogo{¿Acción del Usuario?}

    AccionCatalogo -->|Filtrar Categoría| SeleccionarCategoria[Click en Categoría]
    SeleccionarCategoria --> AgregarParamCategoria[Agregar ?categoria=slug]
    AgregarParamCategoria --> QueryFiltroCategoria[Filter por Categoría]
    QueryFiltroCategoria --> ActualizarSidebarCat[Resaltar Categoría Activa]
    ActualizarSidebarCat --> MostrarFiltradosCat[Mostrar Productos Filtrados]
    MostrarFiltradosCat --> MostrarCatalogo

    %% ========== FLUJO: FILTRAR POR MARCA ==========
    AccionCatalogo -->|Filtrar Marca| SeleccionarMarca[Click en Marca]
    SeleccionarMarca --> AgregarParamMarca[Agregar ?marca=id]
    AgregarParamMarca --> QueryFiltroMarca[Filter por Marca]
    QueryFiltroMarca --> ActualizarSidebarMarca[Resaltar Marca Activa]
    ActualizarSidebarMarca --> MostrarFiltradosMarca[Mostrar Productos Filtrados]
    MostrarFiltradosMarca --> MostrarCatalogo

    %% ========== FLUJO: COMBINAR FILTROS ==========
    AccionCatalogo -->|Combinar Filtros| AplicarMultiplesFiltros[Aplicar Categoría + Marca]
    AplicarMultiplesFiltros --> QueryCombinada[Query con Múltiples Filters]
    QueryCombinada --> MostrarFiltradosCombinados[Mostrar Resultados Combinados]
    MostrarFiltradosCombinados --> VerificarVacio{¿Lista Vacía?}

    VerificarVacio -->|Sí| MensajeSinCoincidencias[Mensaje: Sin Coincidencias]
    MensajeSinCoincidencias --> SugerirQuitarFiltros[Sugerir Quitar Filtros]
    SugerirQuitarFiltros --> MostrarCatalogo

    VerificarVacio -->|No| MostrarCatalogo

    %% ========== FLUJO: LIMPIAR FILTROS ==========
    AccionCatalogo -->|Limpiar Filtros| RemoverParametros[Quitar Parámetros URL]
    RemoverParametros --> CargarCatalogo

    %% ========== FLUJO: VER DETALLE DE PRODUCTO ==========
    AccionCatalogo -->|Click en Producto| SeleccionarProducto[Seleccionar Producto]
    SeleccionarProducto --> NavDetalleProducto[GET /producto/{id}/]
    NavDetalleProducto --> QueryProductoDetalle[Query Producto por ID]
    QueryProductoDetalle --> VerificarExiste{¿Producto Existe?}

    VerificarExiste -->|No| Error404[Error 404: No Encontrado]
    Error404 --> MostrarCatalogo

    VerificarExiste -->|Sí| VerificarActivo{¿Estado Activo?}

    VerificarActivo -->|No| Error403[Error 403: No Disponible]
    Error403 --> MostrarCatalogo

    VerificarActivo -->|Sí| CargarDatosProducto[Cargar Datos Completos]
    CargarDatosProducto --> CargarImagenPrincipal[Cargar Imagen desde CDN]
    CargarImagenPrincipal --> CargarRelacionados[Query Productos Relacionados]
    CargarRelacionados --> FilterMismaCategoria[Filter: Misma Categoría]
    FilterMismaCategoria --> ExcluirActual[Exclude: Producto Actual]
    ExcluirActual --> Limitar4[Limit: 4 Productos]
    Limitar4 --> RenderDetalle[Render Template Detalle]
    RenderDetalle --> MostrarDetalle[Mostrar Página Detalle]

    MostrarDetalle --> AccionDetalle{¿Acción del Usuario?}

    AccionDetalle -->|Agregar al Carrito| SeleccionarCantidad[Seleccionar Cantidad]
    SeleccionarCantidad --> ValidarStockDisponible{¿Stock >= Cantidad?}

    ValidarStockDisponible -->|No| ErrorStockInsuficiente[Error: Stock Insuficiente]
    ErrorStockInsuficiente --> MostrarDetalle

    ValidarStockDisponible -->|Sí| AjaxAgregarCarrito[AJAX: Agregar al Carrito]
    AjaxAgregarCarrito --> ActualizarSesion[Actualizar Sesión Carrito]
    ActualizarSesion --> ActualizarContadorUI[Actualizar Contador UI]
    ActualizarContadorUI --> MostrarExitoAgregar[Mensaje: Agregado Exitosamente]
    MostrarExitoAgregar --> MostrarDetalle

    AccionDetalle -->|Ver Relacionados| ClickRelacionado[Click en Relacionado]
    ClickRelacionado --> NavDetalleProducto

    AccionDetalle -->|Volver al Catálogo| VolverCatalogo[Volver a /catalogo/]
    VolverCatalogo --> MostrarCatalogo

    AccionDetalle -->|Ir al Carrito| NavCarrito[Navegar a /carrito/]
    NavCarrito --> End1([Fin: Ver Carrito])

    %% ========== FLUJO: ORDENAR RESULTADOS ==========
    AccionCatalogo -->|Ordenar| SeleccionarOrden{Tipo de Orden}

    SeleccionarOrden -->|Precio: Menor a Mayor| OrdenPrecioAsc[ORDER BY precio ASC]
    OrdenPrecioAsc --> MostrarOrdenadosPrecioAsc[Mostrar Ordenados]
    MostrarOrdenadosPrecioAsc --> MostrarCatalogo

    SeleccionarOrden -->|Precio: Mayor a Menor| OrdenPrecioDesc[ORDER BY precio DESC]
    OrdenPrecioDesc --> MostrarOrdenadosPrecioDesc[Mostrar Ordenados]
    MostrarOrdenadosPrecioDesc --> MostrarCatalogo

    SeleccionarOrden -->|Nombre: A-Z| OrdenNombreAsc[ORDER BY nombre ASC]
    OrdenNombreAsc --> MostrarOrdenadosNombre[Mostrar Ordenados]
    MostrarOrdenadosNombre --> MostrarCatalogo

    SeleccionarOrden -->|Más Recientes| OrdenFechaDesc[ORDER BY fecha_creacion DESC]
    OrdenFechaDesc --> MostrarOrdenadosFecha[Mostrar Ordenados]
    MostrarOrdenadosFecha --> MostrarCatalogo

    %% ========== SALIR ==========
    AccionCatalogo -->|Salir| End2([Fin: Cerrar])
    AccionInicial -->|Salir| End2

    %% Estilos
    style Start fill:#90EE90
    style End1 fill:#90EE90
    style End2 fill:#90EE90
    style ErrorTermino fill:#FFB6C1
    style MostrarSinResultados fill:#FFD700
    style Error404 fill:#FFB6C1
    style Error403 fill:#FFB6C1
    style ErrorStockInsuficiente fill:#FFB6C1
    style MensajeSinCoincidencias fill:#FFD700
    style AjaxAgregarCarrito fill:#87CEEB
```

## Descripción de Actividades

### Fase 1: Acceso Inicial

| Actividad             | Descripción                   | Actor   |
| --------------------- | ----------------------------- | ------- |
| Acceder al Sitio      | Usuario ingresa URL del sitio | Usuario |
| Mostrar Página Inicio | Renderizar landing page       | Sistema |
| Acción Inicial        | Usuario decide qué hacer      | Usuario |

### Fase 2: Cargar Catálogo

| Actividad               | Descripción                               | Actor   |
| ----------------------- | ----------------------------------------- | ------- |
| GET /catalogo/          | Request HTTP a catálogo                   | Usuario |
| Query Productos Activos | SELECT productos WHERE estado='activo'    | Sistema |
| SELECT_RELATED          | JOIN con categoría y marca (optimización) | Sistema |
| Cargar Categorías       | Query categorías activas                  | Sistema |
| Cargar Marcas           | Query marcas activas                      | Sistema |
| Render Template         | Procesar template Django                  | Sistema |
| Mostrar Grid            | HTML con grid de productos                | Sistema |
| Cargar Imágenes CDN     | Fetch imágenes desde DigitalOcean         | Browser |

**Código de Vista:**

```python
def catalogo(request):
    # Obtener productos activos con optimización
    productos = Producto.objects.filter(
        estado_producto='activo'
    ).select_related('categoria', 'marca')

    # Filtros opcionales
    categoria_slug = request.GET.get('categoria')
    marca_id = request.GET.get('marca')
    orden = request.GET.get('orden', 'nombre')

    # Aplicar filtro de categoría
    if categoria_slug:
        productos = productos.filter(categoria__slug=categoria_slug)

    # Aplicar filtro de marca
    if marca_id:
        productos = productos.filter(marca_id=marca_id)

    # Aplicar ordenamiento
    orden_map = {
        'nombre': 'nombre',
        'precio_asc': 'precio',
        'precio_desc': '-precio',
        'fecha': '-fecha_creacion'
    }
    productos = productos.order_by(orden_map.get(orden, 'nombre'))

    # Obtener listas para filtros
    categorias = Categoria.objects.filter(activa=True)
    marcas = Marca.objects.filter(activa=True)

    context = {
        'productos': productos,
        'categorias': categorias,
        'marcas': marcas,
        'categoria_seleccionada': categoria_slug,
        'marca_seleccionada': marca_id,
        'orden_seleccionado': orden,
    }
    return render(request, 'ventas/catalogo.html', context)
```

### Fase 3: Búsqueda por Texto

| Actividad             | Descripción                          | Actor   |
| --------------------- | ------------------------------------ | ------- |
| Ingresar Término      | Usuario escribe en barra de búsqueda | Usuario |
| Validar Término       | Verificar que no esté vacío          | Sistema |
| Query con ICONTAINS   | Búsqueda case-insensitive            | Sistema |
| Buscar en Nombre      | WHERE nombre ILIKE '%término%'       | Sistema |
| Buscar en Descripción | OR descripcion ILIKE '%término%'     | Sistema |
| Verificar Resultados  | Contar productos encontrados         | Sistema |
| Mostrar Resultados    | Renderizar lista de resultados       | Sistema |

**Código de Búsqueda:**

```python
from django.db.models import Q

def buscar_productos(request):
    termino = request.GET.get('q', '').strip()

    if not termino:
        messages.warning(request, 'Por favor ingrese un término de búsqueda')
        return redirect('catalogo')

    # Búsqueda en nombre y descripción
    productos = Producto.objects.filter(
        Q(nombre__icontains=termino) |
        Q(descripcion__icontains=termino),
        estado_producto='activo'
    ).select_related('categoria', 'marca')

    # Contar resultados
    total_resultados = productos.count()

    if total_resultados == 0:
        messages.info(request, f'No se encontraron productos para "{termino}"')
    else:
        messages.success(request, f'Se encontraron {total_resultados} productos para "{termino}"')

    context = {
        'productos': productos,
        'termino_busqueda': termino,
        'total_resultados': total_resultados,
    }
    return render(request, 'ventas/catalogo.html', context)
```

### Fase 4: Filtrado por Categoría

| Actividad             | Descripción                      | Actor   |
| --------------------- | -------------------------------- | ------- |
| Seleccionar Categoría | Click en categoría del sidebar   | Usuario |
| Agregar Parámetro     | URL: ?categoria=slug             | Sistema |
| Filter por Categoría  | WHERE categoria\_\_slug = 'slug' | Sistema |
| Resaltar Activa       | CSS active class en sidebar      | Sistema |
| Mostrar Filtrados     | Productos de esa categoría       | Sistema |

### Fase 5: Filtrado por Marca

| Actividad         | Descripción               | Actor   |
| ----------------- | ------------------------- | ------- |
| Seleccionar Marca | Click en marca del filtro | Usuario |
| Agregar Parámetro | URL: ?marca=id            | Sistema |
| Filter por Marca  | WHERE marca_id = id       | Sistema |
| Resaltar Activa   | CSS active class          | Sistema |
| Mostrar Filtrados | Productos de esa marca    | Sistema |

### Fase 6: Combinar Filtros

| Actividad                 | Descripción                         | Actor   |
| ------------------------- | ----------------------------------- | ------- |
| Aplicar Múltiples         | Categoría + Marca simultáneamente   | Usuario |
| Query Combinada           | WHERE categoria AND marca           | Sistema |
| Verificar Vacío           | ¿Hay productos con esa combinación? | Sistema |
| Mensaje Sin Coincidencias | "No hay productos con esos filtros" | Sistema |
| Sugerir Quitar Filtros    | Botón para limpiar filtros          | Sistema |

### Fase 7: Ver Detalle de Producto

| Actividad               | Descripción                     | Actor   |
| ----------------------- | ------------------------------- | ------- |
| Seleccionar Producto    | Click en tarjeta de producto    | Usuario |
| GET /producto/{id}/     | Request a página de detalle     | Usuario |
| Query Producto          | SELECT producto WHERE id = {id} | Sistema |
| Verificar Existe        | ¿Producto existe en BD?         | Sistema |
| Verificar Activo        | ¿Estado = 'activo'?             | Sistema |
| Cargar Datos Completos  | Todos los campos del producto   | Sistema |
| Cargar Imagen Principal | Desde CDN de DigitalOcean       | Sistema |
| Query Relacionados      | Productos de misma categoría    | Sistema |
| Render Template         | Procesar template de detalle    | Sistema |
| Mostrar Página Detalle  | Página con información completa | Sistema |

**Código de Vista de Detalle:**

```python
from django.shortcuts import get_object_or_404

def producto_detalle(request, producto_id):
    # Obtener producto o 404
    producto = get_object_or_404(
        Producto,
        producto_id=producto_id,
        estado_producto='activo'
    )

    # Productos relacionados (misma categoría)
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        estado_producto='activo'
    ).exclude(
        producto_id=producto_id
    ).select_related('categoria', 'marca')[:4]

    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
    }
    return render(request, 'ventas/producto.html', context)
```

### Fase 8: Agregar al Carrito desde Detalle

| Actividad              | Descripción                        | Actor   |
| ---------------------- | ---------------------------------- | ------- |
| Seleccionar Cantidad   | Input numérico para cantidad       | Usuario |
| Validar Stock          | Verificar stock >= cantidad        | Sistema |
| AJAX Agregar Carrito   | POST asíncrono sin recargar página | Browser |
| Actualizar Sesión      | Modificar carrito en sesión Django | Sistema |
| Actualizar Contador UI | Badge con total de items           | Browser |
| Mensaje Éxito          | Toast "Agregado al carrito"        | Sistema |

**Código AJAX:**

```javascript
// Cliente (JavaScript)
function agregarAlCarrito(productoId, cantidad) {
  $.ajax({
    url: "/carrito/agregar/",
    type: "POST",
    data: {
      producto_id: productoId,
      cantidad: cantidad,
      action: "post",
      csrfmiddlewaretoken: csrftoken,
    },
    success: function (response) {
      if (response.success) {
        // Actualizar contador
        $("#carrito-count").text(response.total_productos);

        // Mostrar toast
        mostrarToast(
          `${response.nombre_producto} agregado al carrito`,
          "success"
        );
      }
    },
    error: function (xhr) {
      mostrarToast("Error al agregar producto", "error");
    },
  });
}
```

```python
# Servidor (Django)
from django.http import JsonResponse

def agregar_carrito(request):
    carrito = Carrito(request)

    if request.POST.get("action") == "post":
        producto_id = int(request.POST.get("producto_id"))
        cantidad = int(request.POST.get("cantidad", 1))

        producto = get_object_or_404(Producto, producto_id=producto_id)

        # Validar stock
        if producto.stock < cantidad:
            return JsonResponse({
                'success': False,
                'error': 'Stock insuficiente'
            }, status=400)

        carrito.agregar(producto=producto, cantidad=cantidad)

        return JsonResponse({
            "success": True,
            "nombre_producto": producto.nombre,
            "total_productos": carrito.get_total_productos()
        })
```

### Fase 9: Ordenar Resultados

| Actividad           | Descripción                           | Actor   |
| ------------------- | ------------------------------------- | ------- |
| Seleccionar Orden   | Dropdown con opciones de ordenamiento | Usuario |
| Orden Precio Asc    | ORDER BY precio ASC                   | Sistema |
| Orden Precio Desc   | ORDER BY precio DESC                  | Sistema |
| Orden Nombre A-Z    | ORDER BY nombre ASC                   | Sistema |
| Orden Más Recientes | ORDER BY fecha_creacion DESC          | Sistema |

## Optimizaciones de Performance

### 1. Query Optimization

```python
# ❌ Mal: N+1 Query Problem
productos = Producto.objects.all()
for p in productos:
    print(p.categoria.nombre)  # Query adicional por cada producto
    print(p.marca.nombre)       # Query adicional por cada producto

# ✅ Bien: Select Related (1 Query con JOINs)
productos = Producto.objects.select_related('categoria', 'marca').all()
for p in productos:
    print(p.categoria.nombre)  # Sin queries adicionales
    print(p.marca.nombre)       # Sin queries adicionales
```

### 2. Paginación

```python
from django.core.paginator import Paginator

def catalogo_paginado(request):
    productos = Producto.objects.filter(
        estado_producto='activo'
    ).select_related('categoria', 'marca')

    # Paginar (24 productos por página)
    paginator = Paginator(productos, 24)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'ventas/catalogo.html', context)
```

### 3. Caché de Categorías y Marcas

```python
from django.core.cache import cache

def obtener_categorias_cache():
    """Cachea lista de categorías por 1 hora"""
    categorias = cache.get('categorias_activas')

    if categorias is None:
        categorias = list(Categoria.objects.filter(activa=True))
        cache.set('categorias_activas', categorias, 3600)  # 1 hora

    return categorias
```

### 4. Lazy Loading de Imágenes

```html
<!-- Template con lazy loading -->
<img
  src="placeholder.jpg"
  data-src="{{ producto.imagen_url }}"
  class="lazy"
  alt="{{ producto.nombre }}"
/>

<script>
  // JavaScript: Intersection Observer para lazy loading
  const images = document.querySelectorAll("img.lazy");

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.remove("lazy");
        observer.unobserve(img);
      }
    });
  });

  images.forEach((img) => observer.observe(img));
</script>
```

## Métricas de UX

### Indicadores de Navegación

| Métrica                         | Objetivo      | Descripción                          |
| ------------------------------- | ------------- | ------------------------------------ |
| **Tiempo Carga Catálogo**       | < 1 segundo   | Desde request hasta render completo  |
| **Tiempo Carga Imágenes**       | < 2 segundos  | Todas las imágenes visibles cargadas |
| **Tasa de Rebote Catálogo**     | < 40%         | % usuarios que salen sin interactuar |
| **Productos Vistos por Sesión** | > 5 productos | Promedio de productos vistos         |
| **Tasa de Conversión Búsqueda** | > 60%         | % búsquedas que resultan en click    |
| **Filtros Usados por Sesión**   | > 1 filtro    | Promedio de filtros aplicados        |

### Eventos de Analytics

```javascript
// Google Analytics / Tracking
gtag("event", "view_item_list", {
  items: productos,
  list_name: "Catálogo",
});

gtag("event", "search", {
  search_term: termino_busqueda,
});

gtag("event", "view_item", {
  items: [
    {
      id: producto.id,
      name: producto.nombre,
      category: producto.categoria.nombre,
      price: producto.precio,
    },
  ],
});

gtag("event", "add_to_cart", {
  items: [
    {
      id: producto.id,
      name: producto.nombre,
      quantity: cantidad,
    },
  ],
});
```

## Conclusión

Este diagrama de actividad documenta el flujo completo de navegación y búsqueda en el catálogo, mostrando:

- **Múltiples formas de navegar**: Catálogo completo, búsqueda, filtros, ordenamiento
- **Optimizaciones de performance**: SELECT_RELATED, paginación, lazy loading
- **Experiencia de usuario**: Mensajes claros, sugerencias, interacciones AJAX
- **Integración con CDN**: Carga eficiente de imágenes desde DigitalOcean Spaces
- **Validaciones**: Productos activos, stock disponible, términos válidos

**Aspectos clave del diseño:**

✅ Múltiples opciones de navegación y búsqueda  
✅ Filtros combinables (categoría + marca)  
✅ Optimización de queries (N+1 problem resuelto)  
✅ Lazy loading de imágenes para performance  
✅ Interacciones AJAX para mejor UX  
✅ Manejo de errores y estados vacíos

---

**Actualizado**: Octubre 2025  
**Versión**: 1.0
