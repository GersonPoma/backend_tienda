from django.db import models
from django.conf import settings
from apps_privadas.venta.models.venta import Venta


class BeneficioFidelizacionMensual(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='beneficios_fidelizacion'
    )
    periodo = models.DateField()
    usado = models.BooleanField(default=False)
    fecha_uso = models.DateTimeField(null=True, blank=True)
    venta = models.ForeignKey(
        Venta,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='beneficio_fidelizacion'
    )

    class Meta:
        unique_together = ('usuario', 'periodo')
        verbose_name = 'Beneficio de Fidelización Mensual'
        verbose_name_plural = 'Beneficios de Fidelización Mensual'

    def __str__(self):
        return f"Beneficio {self.usuario_id} - {self.periodo} - usado={self.usado}"
