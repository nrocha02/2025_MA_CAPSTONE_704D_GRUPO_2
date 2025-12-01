"""
Utilidades para la aplicación de ventas
"""

def validar_rut(rut_completo):
    """
    Valida un RUT chileno con formato XXXXXXXX-X
    
    Args:
        rut_completo (str): RUT en formato XXXXXXXX-X
        
    Returns:
        bool: True si el RUT es válido, False en caso contrario
    """
    import re
    
    # Verificar formato básico
    if not re.match(r'^[0-9]+[-|‐]{1}[0-9kK]{1}$', rut_completo):
        return False
    
    # Separar número y dígito verificador
    partes = rut_completo.split('-')
    if len(partes) != 2:
        return False
    
    rut = partes[0]
    dv = partes[1].upper()
    
    # Calcular dígito verificador esperado
    dv_esperado = calcular_dv(rut)
    
    return dv == dv_esperado


def calcular_dv(rut):
    """
    Calcula el dígito verificador de un RUT chileno
    
    Args:
        rut (str o int): Número de RUT sin dígito verificador
        
    Returns:
        str: Dígito verificador calculado ('0'-'9' o 'K')
    """
    rut = int(rut)
    m = 0
    s = 1
    
    while rut:
        s = (s + rut % 10 * (9 - m % 6)) % 11
        rut //= 10
        m += 1
    
    return str(s - 1) if s else 'K'


def formatear_rut(rut):
    """
    Formatea un RUT eliminando puntos y dejando solo números y guión
    
    Args:
        rut (str): RUT a formatear
        
    Returns:
        str: RUT formateado sin puntos
    """
    # Eliminar puntos, espacios y guiones
    rut = rut.replace('.', '').replace(' ', '').replace('-', '')
    
    # Separar dígito verificador
    if len(rut) < 2:
        return rut
    
    dv = rut[-1]
    numero = rut[:-1]
    
    return f"{numero}-{dv}"
