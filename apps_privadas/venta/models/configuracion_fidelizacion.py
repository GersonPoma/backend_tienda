from django.db import models


class ConfiguracionFidelizacion(models.Model):
    monto_minimo_acumulado = models.DecimalField(max_digits=10, decimal_places=2, default=5000)
    monto_descuento = models.DecimalField(max_digits=10, decimal_places=2, default=200)
    activo = models.BooleanField(default=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración de Fidelización'
        verbose_name_plural = 'Configuración de Fidelización'

    def __str__(self):
        return f"Fidelización (min={self.monto_minimo_acumulado}, desc={self.monto_descuento})"

    @classmethod
    def obtener(cls):
        instancia, _ = cls.objects.get_or_create(pk=1)
        return instancia
