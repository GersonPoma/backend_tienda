from rest_framework import serializers

from apps_privadas.inventario.models import Producto


class CompararProductosSerializer(serializers.Serializer):
    producto_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        min_length=2,
        max_length=4,
        error_messages={
            'min_length': 'Debes seleccionar al menos 2 muebles.',
            'max_length': 'Puedes comparar como maximo 4 muebles a la vez.',
        },
    )

    def validate_producto_ids(self, value):
        producto_ids = list(dict.fromkeys(value))
        if len(producto_ids) < 2:
            raise serializers.ValidationError('Debes seleccionar al menos 2 muebles diferentes.')

        encontrados = set(
            Producto.objects.filter(id__in=producto_ids, activo=True).values_list('id', flat=True)
        )
        faltantes = [producto_id for producto_id in producto_ids if producto_id not in encontrados]
        if faltantes:
            raise serializers.ValidationError(
                f'Los muebles no existen o no estan activos: {faltantes}'
            )

        return producto_ids
