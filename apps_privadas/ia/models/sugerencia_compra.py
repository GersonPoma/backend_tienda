from django.db import models
from apps_privadas.compras.models import Proveedor, Compra
from apps_privadas.inventario.models import VarianteProducto
from apps_privadas.ia.models.alerta import AlertaReabastecimiento


class SugerenciaCompra(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('descartada', 'Descartada'),
    ]

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sugerencias_compra'
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    compra_generada = models.ForeignKey(
        Compra,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sugerencia_origen'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Sugerencia de Compra'
        verbose_name_plural = 'Sugerencias de Compra'

    def __str__(self):
        proveedor = self.proveedor.nombre if self.proveedor_id else 'Sin proveedor'
        return f"Sugerencia {self.id} - {proveedor} [{self.estado}]"


class SugerenciaCompraDetalle(models.Model):
    sugerencia = models.ForeignKey(
        SugerenciaCompra,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    variante = models.ForeignKey(
        VarianteProducto,
        on_delete=models.CASCADE,
        related_name='sugerencias_compra_detalle'
    )
    alerta_origen = models.ForeignKey(
        AlertaReabastecimiento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sugerencias_generadas'
    )
    cantidad_sugerida = models.PositiveIntegerField()
    costo_unitario_estimado = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['id']
        unique_together = ('sugerencia', 'variante')
        verbose_name = 'Detalle de Sugerencia de Compra'
        verbose_name_plural = 'Detalles de Sugerencia de Compra'

    def __str__(self):
        return f"Detalle {self.id} - {self.variante.sku} x{self.cantidad_sugerida}"