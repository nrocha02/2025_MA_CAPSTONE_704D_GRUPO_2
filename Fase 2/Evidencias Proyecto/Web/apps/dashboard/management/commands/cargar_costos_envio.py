from django.core.management.base import BaseCommand
from apps.dashboard.models import CostoEnvioComuna


class Command(BaseCommand):
    help = "Carga los costos de envío predeterminados para las comunas de Santiago"

    def handle(self, *args, **options):
        costos_predeterminados = {
            "Quilicura": 4000,
            "Huechuraba": 4500,
            "Vitacura": 4500,
            "Providencia": 4000,
            "La Reina": 4000,
            "Ñuñoa": 4000,
            "Macul": 3500,
            "San Joaquín": 2000,
            "La Florida": 3500,
            "San Miguel": 0,
            "Pedro Aguirre Cerda": 2000,
            "Cerro Navia": 4000,
            "Estación Central": 3500,
            "Quinta Normal": 4000,
            "Maipú": 4000,
            "Pudahuel": 4000,
            "Lo Prado": 4000,
            "Cerrillos": 3500,
            "La Pintana": 3500,
            "El Bosque": 3500,
            "San Bernardo": 4000,
            "La Cisterna": 1500,
            "San José de Maipo": 3500,
            "Peñalolén": 4000,
            "Lo Espejo": 3500,
            "Puente Alto": 3500,
            "San Ramón": 2000,
            "Conchalí": 4000,
            "Recoleta": 4000,
            "Renca": 4000,
            "Independencia": 4000,
            "La Granja": 3000,
            "Pirque": 3500,
            "Lo Barnechea": 4500,
            "Las Condes": 4500,
            "Padre Hurtado": 4000,
        }

        self.stdout.write(self.style.SUCCESS("Iniciando carga de costos de envío..."))

        creados = 0
        actualizados = 0

        for comuna, costo in costos_predeterminados.items():
            costo_obj, created = CostoEnvioComuna.objects.update_or_create(
                comuna=comuna, defaults={"costo": costo, "activo": True}
            )

            if created:
                creados += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Creado: {comuna} - ${costo}")
                )
            else:
                actualizados += 1
                self.stdout.write(
                    self.style.WARNING(f"  ↻ Actualizado: {comuna} - ${costo}")
                )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Proceso completado: {creados} creados, {actualizados} actualizados"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Total de costos en la base de datos: {creados + actualizados}"
            )
        )
