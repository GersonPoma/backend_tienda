from django.db import models
from apps_privadas.inventario.models import Producto


class Multimedio(models.Model):
    TIPO_CHOICES = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('documento', 'Documento'),
    ]

    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='multimedios'
    )

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Multimedio'
        verbose_name_plural = 'Multimedios'

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"
