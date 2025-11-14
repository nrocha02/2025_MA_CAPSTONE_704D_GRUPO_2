import os
import json
import http.client
from apps.dashboard.models import CostoEnvioComuna


# ============================================================================
# CONFIGURACIÓN DE ORIGEN DE ENVÍOS
# ============================================================================
# IMPORTANTE: Todos los envíos se originan desde San Miguel, Región Metropolitana
#
# Esta configuración es FIJA y se utiliza automáticamente en:
# - Todas las llamadas a la API de Multicourier
# - Cálculo de costos para regiones fuera de Santiago
# - Descripciones de envío mostradas al cliente
#
# Para cambiar el origen, modificar estos valores:
ORIGEN_ENVIO = {
    "region": "RM",  # Código de región (RM = Región Metropolitana)
    "distrito": 30,  # Código de distrito en la API de Multicourier (30 = San Miguel)
    "nombre": "San Miguel",  # Nombre visible para el cliente
}
# ============================================================================


# Comunas de Santiago que usan costo fijo
COMUNAS_SANTIAGO = [
    "Quilicura",
    "Huechuraba",
    "Vitacura",
    "Providencia",
    "La Reina",
    "Ñuñoa",
    "Macul",
    "San Joaquín",
    "La Florida",
    "San Miguel",
    "Pedro Aguirre Cerda",
    "Cerro Navia",
    "Estación Central",
    "Quinta Normal",
    "Maipú",
    "Pudahuel",
    "Lo Prado",
    "Cerrillos",
    "La Pintana",
    "El Bosque",
    "San Bernardo",
    "La Cisterna",
    "San José de Maipo",
    "Peñalolén",
    "Lo Espejo",
    "Puente Alto",
    "San Ramón",
    "Conchalí",
    "Recoleta",
    "Renca",
    "Independencia",
    "La Granja",
    "Pirque",
    "Lo Barnechea",
    "Las Condes",
    "Padre Hurtado",
]


def normalizar_comuna(comuna):
    """Normaliza el nombre de la comuna para comparación"""
    if not comuna:
        return ""
    return comuna.strip().title()


def es_comuna_santiago(comuna):
    """Verifica si la comuna pertenece a Santiago"""
    comuna_normalizada = normalizar_comuna(comuna)
    comunas_normalizadas = [normalizar_comuna(c) for c in COMUNAS_SANTIAGO]
    return comuna_normalizada in comunas_normalizadas


def obtener_costo_fijo_comuna(comuna):
    """Obtiene el costo fijo de envío para una comuna de Santiago"""
    try:
        comuna_normalizada = normalizar_comuna(comuna)
        costo_envio = CostoEnvioComuna.objects.filter(
            comuna__iexact=comuna_normalizada, activo=True
        ).first()

        if costo_envio:
            return costo_envio.costo

        # Si no se encuentra en la BD, retornar None para usar API
        return None
    except Exception as e:
        print(f"Error al obtener costo fijo: {e}")
        return None


def calcular_envio_api(destino_state, destino_district, items_carrito):
    """
    Calcula el costo de envío usando la API de RapidAPI

    NOTA: El origen siempre es San Miguel, Región Metropolitana

    Args:
        destino_state: Estado/región de destino (ej: "RM", "V", etc.)
        destino_district: Distrito de destino
        items_carrito: Lista de items del carrito

    Returns:
        dict con información del envío o None si hay error
    """
    try:
        # Por ahora usamos valores fijos de prueba como especificó el usuario
        # El origen siempre es San Miguel, RM
        payload_data = {
            "from": {
                "state": ORIGEN_ENVIO["region"],
                "district": ORIGEN_ENVIO["distrito"],
            },
            "to": {"state": destino_state, "district": destino_district},
            "datosProducto": {
                "largo": "8",
                "ancho": "15",
                "alto": "12",
                "pesoFisico": "2",
            },
        }

        payload = json.dumps(payload_data)

        conn = http.client.HTTPSConnection("multicourier.p.rapidapi.com")

        headers = {
            "x-rapidapi-key": os.getenv("X_RAPIDAPI_KEY", ""),
            "x-rapidapi-host": "multicourier.p.rapidapi.com",
            "Content-Type": "application/json",
        }

        conn.request("POST", "/pricing", payload, headers)

        res = conn.getresponse()
        data = res.read()

        result = json.loads(data.decode("utf-8"))

        # Retornar la primera opción disponible (más barata generalmente)
        if result and len(result) > 0:
            return {
                "opciones": result,
                "costo_minimo": min(
                    [
                        item.get("data", {}).get("total", 0)
                        for item in result
                        if item.get("data", {}).get("total")
                    ]
                ),
                "servicio_recomendado": result[0],
            }

        return None

    except Exception as e:
        print(f"Error al calcular envío con API: {e}")
        return None


def calcular_costo_envio(ciudad, items_carrito=None):
    """
    Calcula el costo de envío basado en la ciudad de destino

    Args:
        ciudad: Ciudad/comuna de destino
        items_carrito: Items del carrito (opcional, para cálculos futuros)

    Returns:
        int: Costo de envío
    """
    # Verificar si es comuna de Santiago
    if es_comuna_santiago(ciudad):
        costo_fijo = obtener_costo_fijo_comuna(ciudad)
        if costo_fijo is not None:
            return costo_fijo

    # Si no es comuna de Santiago o no tiene costo fijo, usar API
    # Por ahora retornamos un costo por defecto si no podemos usar la API
    # En producción, aquí se llamaría a calcular_envio_api()
    # NOTA: Se necesitaría el código de región y distrito de destino
    try:
        # Ejemplo: destino en RM, distrito 4 (El Bosque)
        # En producción, estos valores deberían obtenerse dinámicamente
        resultado_api = calcular_envio_api("RM", 4, items_carrito or [])
        if resultado_api:
            return resultado_api.get("costo_minimo", 5000)
    except:
        pass

    # Costo por defecto si todo falla
    return 5000


def obtener_opciones_envio(ciudad, items_carrito=None):
    """
    Obtiene todas las opciones de envío disponibles para una ciudad

    Args:
        ciudad: Ciudad/comuna de destino
        items_carrito: Items del carrito

    Returns:
        list: Lista de opciones de envío
    """
    opciones = []

    # Verificar si es comuna de Santiago
    if es_comuna_santiago(ciudad):
        costo_fijo = obtener_costo_fijo_comuna(ciudad)
        if costo_fijo is not None:
            opciones.append(
                {
                    "tipo": "autogestionado",
                    "servicio": "Envío Autogestionado",
                    "costo": costo_fijo,
                    "tiempo_estimado": "1-2 días hábiles",
                    "descripcion": f"Envío desde {ORIGEN_ENVIO['nombre']} a {ciudad}",
                    "origen": ORIGEN_ENVIO["nombre"],
                }
            )
            return opciones

    # Si no es comuna de Santiago, usar API
    # NOTA: Se necesitaría el código de región y distrito de destino
    try:
        # Ejemplo: destino en RM, distrito 4 (El Bosque)
        # En producción, estos valores deberían obtenerse dinámicamente según la comuna
        resultado_api = calcular_envio_api("RM", 4, items_carrito or [])
        if resultado_api and "opciones" in resultado_api:
            for opcion in resultado_api["opciones"]:
                data = opcion.get("data", {})
                opciones.append(
                    {
                        "tipo": "courier",
                        "servicio": data.get("nameService", "Servicio de Courier"),
                        "costo": data.get("total", 0),
                        "tiempo_estimado": data.get("promiseDay", "N/A"),
                        "descripcion": data.get("serviceDescription", ""),
                        "origen": ORIGEN_ENVIO["nombre"],
                    }
                )
    except Exception as e:
        print(f"Error al obtener opciones de envío: {e}")

    # Si no hay opciones, agregar una por defecto
    if not opciones:
        opciones.append(
            {
                "tipo": "standard",
                "servicio": "Envío Standard",
                "costo": 5000,
                "tiempo_estimado": "3-5 días hábiles",
                "descripcion": f"Envío desde {ORIGEN_ENVIO['nombre']} a todo Chile",
                "origen": ORIGEN_ENVIO["nombre"],
            }
        )

    return opciones
