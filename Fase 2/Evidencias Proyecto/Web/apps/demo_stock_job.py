#!/usr/bin/env python3

import sys
import os
from datetime import datetime

# Simular datos de productos para la demostración
productos_simulados = [
    {
        'nombre': 'Alimento Premium Gato Adulto 7kg',
        'sku': 'CAT-PREM-7K',
        'stock': 2,
        'categoria': 'Alimentos',
        'marca': 'Royal Canin',
        'precio': 35000
    },
    {
        'nombre': 'Collar Antipulgas Mediano',
        'sku': 'COL-AP-MED',
        'stock': 5,
        'categoria': 'Accesorios',
        'marca': 'Bayer',
        'precio': 8500
    },
    {
        'nombre': 'Arena Silica Gel 5kg',
        'sku': 'ARE-SIL-5K',
        'stock': 1,
        'categoria': 'Higiene',
        'marca': 'Cat Litter',
        'precio': 12000
    },
    {
        'nombre': 'Juguete Cuerda Perro Grande',
        'sku': 'JUG-CUE-GRA',
        'stock': 8,
        'categoria': 'Juguetes',
        'marca': 'Kong',
        'precio': 6500
    },
    {
        'nombre': 'Shampoo Antipulgas 250ml',
        'sku': 'SHA-AP-250',
        'stock': 3,
        'categoria': 'Higiene',
        'marca': 'Virbac',
        'precio': 15000
    }
]


def demo_stock_job():
    """Demostración del job diario de stock"""
    print("=" * 60)
    print("DEMO - JOB DIARIO DE STOCK - CORDILLERA PETS")
    print("=" * 60)
    print(f"Fecha/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Simular análisis de stock
    print("📊 ANALIZANDO INVENTARIO...")
    print("   • Conectando a base de datos... ✓")
    print("   • Consultando productos activos... ✓")
    print("   • Aplicando filtros de stock... ✓")
    print()
    
    # Clasificar productos
    productos_criticos = [p for p in productos_simulados if p['stock'] <= 3]
    productos_bajos = [p for p in productos_simulados if 4 <= p['stock'] <= 9]
    
    print(f"📦 RESUMEN DE STOCK:")
    print(f"   • Productos críticos (≤3): {len(productos_criticos)}")
    print(f"   • Productos bajos (4-9): {len(productos_bajos)}")
    print(f"   • Total productos alertados: {len(productos_simulados)}")
    print()
    
    # Mostrar productos críticos
    if productos_criticos:
        print("🔴 PRODUCTOS CRÍTICOS (REQUIEREN ATENCIÓN INMEDIATA):")
        for producto in productos_criticos:
            print(f"   • {producto['nombre']} ({producto['sku']}) - Stock: {producto['stock']} - ${producto['precio']:,}")
        print()
    
    # Mostrar productos con stock bajo
    if productos_bajos:
        print("🟡 PRODUCTOS CON STOCK BAJO:")
        for producto in productos_bajos:
            print(f"   • {producto['nombre']} ({producto['sku']}) - Stock: {producto['stock']} - ${producto['precio']:,}")
        print()
    
    # Simular envío de email
    print("📧 ENVIANDO REPORTE POR EMAIL...")
    
    # Aquí usaríamos el servicio real de Brevo
    try:
        # Simulamos el envío
        print("   • Preparando template HTML... ✓")
        print("   • Configurando destinatario... ✓")
        print("   • Enviando via Brevo API... ✓")
        print("   • Confirmación recibida... ✓")
        print()
        print("✅ REPORTE ENVIADO EXITOSAMENTE")
        print("   📧 Destinatario: cordillerapetschile@gmail.com")
        print("   📊 Productos alertados: 5")
        print("   🚨 Productos críticos: 3")
        print()
        
    except Exception as e:
        print(f"❌ ERROR AL ENVIAR REPORTE: {e}")
        print("   • Reintentando en 5 minutos...")
        print()
    
    # Mostrar próximas acciones
    print("📋 ACCIONES RECOMENDADAS:")
    print("   1. Contactar proveedores para productos críticos")
    print("   2. Programar reposición de productos con stock bajo")
    print("   3. Revisar patrones de venta para ajustar alertas")
    print("   4. Actualizar niveles mínimos de stock")
    print()
    
    print("🕐 PRÓXIMO JOB: Mañana a las 10:00 AM")
    print("=" * 60)
    print("DEMO COMPLETADA")
    print("=" * 60)


def demo_email_template():
    """Mostrar cómo se vería el email"""
    print("\n" + "=" * 60)
    print("PREVIEW DEL EMAIL QUE SE ENVIARÍA")
    print("=" * 60)
    
    print("Para: cordillerapetschile@gmail.com")
    print("De: Cordillera Pets <cordillerapetschile@gmail.com>")
    print("Asunto: 🚨 REPORTE DIARIO DE STOCK - 5 productos requieren atención")
    print()
    print("--- CONTENIDO DEL EMAIL ---")
    print()
    print("🚨 REPORTE DIARIO DE STOCK")
    print("Cordillera Pets - Sistema de Gestión de Inventario")
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    print("📊 RESUMEN EJECUTIVO")
    print("   Productos Críticos (≤3): 3")
    print("   Productos Bajos (4-9): 2")  
    print("   Total Alertados: 5")
    print()
    print("⚠️ ATENCIÓN URGENTE")
    print("Hay 3 productos en estado CRÍTICO que requieren reposición inmediata")
    print()
    print("📦 DETALLE DE PRODUCTOS")
    print("-" * 40)
    
    for producto in productos_simulados:
        if producto['stock'] <= 3:
            nivel = "CRÍTICO"
            icono = "🔴"
        elif producto['stock'] <= 5:
            nivel = "MUY BAJO" 
            icono = "🟠"
        else:
            nivel = "BAJO"
            icono = "🟡"
            
        print(f"{icono} {producto['nombre']}")
        print(f"   SKU: {producto['sku']} | Stock: {producto['stock']} | Nivel: {nivel}")
        print(f"   Categoría: {producto['categoria']} | Precio: ${producto['precio']:,}")
        print()
    
    print("📋 ACCIONES RECOMENDADAS")
    print("• Inmediato: Contactar proveedores para productos críticos")
    print("• Esta semana: Programar reposición de productos con stock bajo")
    print("• Seguimiento: Revisar patrones de venta para ajustar niveles mínimos")
    print()
    print("Sistema de Gestión de Inventario - Cordillera Pets")
    print("Próximo reporte: mañana 10:00 AM")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--email-preview":
        demo_email_template()
    else:
        demo_stock_job()
        
    if len(sys.argv) == 1:
        print("\nPara ver el preview del email, ejecuta:")
        print("python demo_stock_job.py --email-preview")