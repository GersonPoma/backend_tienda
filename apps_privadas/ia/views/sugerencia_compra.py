from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps_privadas.ia.models import SugerenciaCompra, SugerenciaCompraDetalle
from apps_privadas.ia.serializers import SugerenciaCompraSerializer, SugerenciaCompraDetalleSerializer
from apps_privadas.compras.services.compra.service import CompraService


class SugerenciaCompraViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """
    Sugerencias de reabastecimiento generadas automáticamente a partir de las
    alertas de `ia` (stock bajo / demanda alta). Requieren revisión manual:
    el usuario puede editar las líneas (vía sugerencias-compra-detalles),
    reasignar el proveedor y luego aprobar o descartar.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SugerenciaCompraSerializer

    def get_queryset(self):
        qs = SugerenciaCompra.objects.select_related('proveedor').prefetch_related(
            'detalles__variante__producto'
        )
        estado = self.request.query_params.get('estado')
        proveedor_id = self.request.query_params.get('proveedor')
        if estado:
            qs = qs.filter(estado=estado)
        if proveedor_id:
            qs = qs.filter(proveedor_id=proveedor_id)
        return qs

    @action(detail=True, methods=['post'])
    def aprobar(self, request, pk=None):
        sugerencia = self.get_object()
        if sugerencia.estado != 'pendiente':
            raise ValidationError('Solo se pueden aprobar sugerencias pendientes.')
        if not sugerencia.proveedor_id:
            raise ValidationError('Debe asignar un proveedor antes de aprobar.')

        detalles = list(sugerencia.detalles.select_related('variante').all())
        if not detalles:
            raise ValidationError('La sugerencia no tiene líneas de detalle.')

        with transaction.atomic():
            compra = CompraService.crear_compra(sugerencia.proveedor_id)
            CompraService.aplicar_detalles(compra, [
                {
                    'variante_producto_id': d.variante_id,
                    'cantidad': d.cantidad_sugerida,
                    'costo_unitario': d.costo_unitario_estimado,
                }
                for d in detalles
            ])

            sugerencia.estado = 'aprobada'
            sugerencia.compra_generada = compra
            sugerencia.fecha_resolucion = timezone.now()
            sugerencia.save(update_fields=['estado', 'compra_generada', 'fecha_resolucion'])

        return Response(SugerenciaCompraSerializer(sugerencia).data)

    @action(detail=True, methods=['post'])
    def descartar(self, request, pk=None):
        sugerencia = self.get_object()
        if sugerencia.estado != 'pendiente':
            raise ValidationError('Solo se pueden descartar sugerencias pendientes.')

        sugerencia.estado = 'descartada'
        sugerencia.fecha_resolucion = timezone.now()
        sugerencia.save(update_fields=['estado', 'fecha_resolucion'])
        return Response(SugerenciaCompraSerializer(sugerencia).data)


class SugerenciaCompraDetalleViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    Edición de líneas individuales de una sugerencia (ajustar cantidad/costo
    estimado, o quitar una línea) mientras la sugerencia siga pendiente.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SugerenciaCompraDetalleSerializer

    def get_queryset(self):
        qs = SugerenciaCompraDetalle.objects.select_related('sugerencia', 'variante__producto')
        sugerencia_id = self.request.query_params.get('sugerencia')
        if sugerencia_id:
            qs = qs.filter(sugerencia_id=sugerencia_id)
        return qs

    @staticmethod
    def _validar_pendiente(detalle):
        if detalle.sugerencia.estado != 'pendiente':
            raise ValidationError('Solo se pueden editar líneas de una sugerencia pendiente.')

    def perform_update(self, serializer):
        self._validar_pendiente(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self._validar_pendiente(instance)
        instance.delete()