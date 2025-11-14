from django.db import models


class CostoEnvioComuna(models.Model):
    comuna = models.CharField(max_length=100, unique=True)
    costo = models.IntegerField()
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "costo_envio_comuna"
        ordering = ["comuna"]
        verbose_name = "Costo de Envío por Comuna"
        verbose_name_plural = "Costos de Envío por Comuna"

    def __str__(self):
        return f"{self.comuna} - ${self.costo}"
