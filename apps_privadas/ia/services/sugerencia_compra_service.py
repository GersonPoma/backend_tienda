from decimal import Decimal
from django.db import transaction
from django.db.models import Count

from apps_privadas.compras.models import DetalleCompra
from apps_privadas.ia.models import SugerenciaCompra, SugerenciaCompraDetalle

MARGEN_REPOSICION = 2


def _proveedor_habitual(variante_id):
    """Proveedor que más veces surtió esa variante según el historial de compras."""
    fila = (
        DetalleCompra.objects
        .filter(variante_producto_id=variante_id)
        .values('compra__proveedor_id')
        .annotate(total=Count('id'))
        .order_by('-total')
        .first()
    )
    return fila['compra__proveedor_id'] if fila else None


def _cantidad_sugerida(alerta):
    if alerta.tipo == 'demanda_alta' and alerta.demanda_proyectada is not None:
        return max(1, alerta.demanda_proyectada - alerta.stock_actual)
    return max(1, (alerta.limite_minimo * MARGEN_REPOSICION) - alerta.stock_actual)


@transaction.atomic
def generar_sugerencia_compra(alerta):
    """
    Convierte una AlertaReabastecimiento recién creada en una línea de
    sugerencia de compra, agrupada por proveedor habitual (el que más veces
    surtió esa variante según el historial de DetalleCompra). Si ya existe
    una sugerencia pendiente para ese proveedor, agrega/actualiza la línea
    en vez de duplicarla.
    """
    variante = alerta.variante
    proveedor_id = _proveedor_habitual(variante.id)
    cantidad = _cantidad_sugerida(alerta)

    sugerencia, _ = SugerenciaCompra.objects.get_or_create(
        proveedor_id=proveedor_id,
        estado='pendiente',
    )

    detalle = sugerencia.detalles.filter(variante=variante).first()
    if detalle:
        detalle.cantidad_sugerida = max(detalle.cantidad_sugerida, cantidad)
        detalle.alerta_origen = alerta
        detalle.save(update_fields=['cantidad_sugerida', 'alerta_origen'])
    else:
        SugerenciaCompraDetalle.objects.create(
            sugerencia=sugerencia,
            variante=variante,
            alerta_origen=alerta,
            cantidad_sugerida=cantidad,
            costo_unitario_estimado=variante.costo_ponderado or Decimal('0'),
        )

    return sugerencia