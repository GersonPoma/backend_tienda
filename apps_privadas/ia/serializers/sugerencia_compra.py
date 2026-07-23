from decimal import Decimal
from rest_framework import serializers
from apps_privadas.ia.models import SugerenciaCompra, SugerenciaCompraDetalle


class SugerenciaCompraDetalleSerializer(serializers.ModelSerializer):
    sku = serializers.CharField(source='variante.sku', read_only=True)
    producto_nombre = serializers.CharField(source='variante.producto.nombre', read_only=True)

    class Meta:
        model = SugerenciaCompraDetalle
        fields = [
            'id',
            'sugerencia',
            'variante',
            'sku',
            'producto_nombre',
            'cantidad_sugerida',
            'costo_unitario_estimado',
            'alerta_origen',
        ]
        read_only_fields = ['id', 'sugerencia', 'variante', 'alerta_origen']


class SugerenciaCompraSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source='proveedor.nombre', read_only=True, default=None)
    detalles = SugerenciaCompraDetalleSerializer(many=True, read_only=True)
    total_estimado = serializers.SerializerMethodField()

    class Meta:
        model = SugerenciaCompra
        fields = [
            'id',
            'proveedor',
            'proveedor_nombre',
            'estado',
            'fecha_creacion',
            'fecha_resolucion',
            'compra_generada',
            'detalles',
            'total_estimado',
        ]
        read_only_fields = [
            'id', 'estado', 'fecha_creacion', 'fecha_resolucion',
            'compra_generada', 'detalles', 'total_estimado',
        ]

    def get_total_estimado(self, obj):
        return sum(
            (d.cantidad_sugerida * d.costo_unitario_estimado for d in obj.detalles.all()),
            Decimal('0'),
        )

    def validate_proveedor(self, value):
        if self.instance and self.instance.estado != 'pendiente':
            raise serializers.ValidationError('Solo se puede modificar el proveedor de una sugerencia pendiente.')
        return value