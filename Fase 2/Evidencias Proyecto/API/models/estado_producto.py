from enum import Enum

class EstadoProducto(str, Enum):
    activo = "activo"
    inactivo = "inactivo"
    eliminado = "eliminado"
