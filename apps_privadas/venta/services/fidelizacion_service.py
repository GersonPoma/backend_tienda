from datetime import date

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps_privadas.venta.models import (
    Venta,
    ConfiguracionFidelizacion,
    BeneficioFidelizacionMensual,
)


def _periodo_actual():
    hoy = timezone.localdate()
    return date(hoy.year, hoy.month, 1)


def calcular_acumulado_mes(usuario, periodo=None, excluir_venta_id=None):
    periodo = periodo or _periodo_actual()

    queryset = Venta.objects.filter(
        usuario=usuario,
        estado='completado',
        fecha__year=periodo.year,
        fecha__month=periodo.month,
    )
    if excluir_venta_id is not None:
        queryset = queryset.exclude(pk=excluir_venta_id)

    return queryset.aggregate(total=Sum('precio_total'))['total'] or 0


def obtener_estado_beneficio(usuario):
    periodo = _periodo_actual()
    config = ConfiguracionFidelizacion.obtener()
    beneficio, _ = BeneficioFidelizacionMensual.objects.get_or_create(
        usuario=usuario,
        periodo=periodo,
    )
    acumulado = calcular_acumulado_mes(usuario, periodo=periodo)
    elegible = config.activo and not beneficio.usado and acumulado >= config.monto_minimo_acumulado

    return {
        'acumulado': acumulado,
        'monto_minimo': config.monto_minimo_acumulado,
        'monto_descuento': config.monto_descuento,
        'activo': config.activo,
        'usado': beneficio.usado,
        'elegible': elegible,
    }


def aplicar_descuento_si_corresponde(venta):
    if venta.estado != 'completado' or venta.descuento_fidelizacion:
        return 0

    periodo = _periodo_actual()

    with transaction.atomic():
        beneficio, _ = BeneficioFidelizacionMensual.objects.select_for_update().get_or_create(
            usuario=venta.usuario,
            periodo=periodo,
        )

        if beneficio.usado:
            return 0

        config = ConfiguracionFidelizacion.obtener()
        if not config.activo:
            return 0

        acumulado = calcular_acumulado_mes(venta.usuario, periodo=periodo, excluir_venta_id=venta.id)
        if acumulado < config.monto_minimo_acumulado:
            return 0

        descuento_aplicado = min(config.monto_descuento, venta.precio_total)
        venta.descuento_fidelizacion = descuento_aplicado
        venta.precio_total = venta.precio_total - descuento_aplicado
        venta.save(update_fields=['descuento_fidelizacion', 'precio_total'])

        beneficio.usado = True
        beneficio.fecha_uso = timezone.now()
        beneficio.venta = venta
        beneficio.save(update_fields=['usado', 'fecha_uso', 'venta'])

        return descuento_aplicado
