from rest_framework import serializers
from apps_privadas.venta.models import Venta, DetalleVenta
from apps_privadas.inventario.models import VarianteProducto
from apps_privadas.seguridad.models.usuario import Usuario


class DetalleVentaOutputSerializer(serializers.ModelSerializer):
    variante_producto_sku = serializers.CharField(source='variante_producto.sku', read_only=True)
    variante_producto_nombre = serializers.CharField(source='variante_producto.producto.nombre', read_only=True)

    class Meta:
        model = DetalleVenta
        fields = [
            'id', 'cantidad', 'precio_subtotal', 'precio_unitario',
            'variante_producto', 'variante_producto_sku', 'variante_producto_nombre',
            'venta'
        ]


class DetalleVentaInputSerializer(serializers.Serializer):
    variante_producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField()
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_variante_producto_id(self, value):
        if not VarianteProducto.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'La variante con ID {value} no existe')
        return value


class ActualizarDetalleVentaInputSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    variante_producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField()
    precio_unitario = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_variante_producto_id(self, value):
        if not VarianteProducto.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'La variante con ID {value} no existe')
        return value


class VentaSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    detalles = DetalleVentaOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Venta
        fields = [
            'id', 'tipo', 'estado', 'fecha', 'precio_total', 'descuento_fidelizacion',
            'usuario', 'usuario_username', 'detalles',
        ]
        read_only_fields = ['id', 'fecha', 'descuento_fidelizacion']


class HistorialCompraDetalleSerializer(serializers.ModelSerializer):
    producto_id = serializers.IntegerField(source='variante_producto.producto.id', read_only=True)
    producto_nombre = serializers.CharField(source='variante_producto.producto.nombre', read_only=True)
    variante_id = serializers.IntegerField(source='variante_producto.id', read_only=True)
    variante_sku = serializers.CharField(source='variante_producto.sku', read_only=True)

    class Meta:
        model = DetalleVenta
        fields = [
            'id',
            'producto_id',
            'producto_nombre',
            'variante_id',
            'variante_sku',
            'cantidad',
            'precio_unitario',
            'precio_subtotal',
        ]


class HistorialCompraSerializer(serializers.ModelSerializer):
    compra_id = serializers.IntegerField(source='id', read_only=True)
    total = serializers.DecimalField(source='precio_total', max_digits=10, decimal_places=2, read_only=True)
    productos = HistorialCompraDetalleSerializer(source='detalles', many=True, read_only=True)
    cantidad_productos = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = [
            'compra_id',
            'fecha',
            'total',
            'estado',
            'tipo',
            'cantidad_productos',
            'productos',
            'descuento_fidelizacion',
        ]

    def get_cantidad_productos(self, obj):
        return sum(detalle.cantidad for detalle in obj.detalles.all())


class CrearVentaSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=Venta.TIPO_CHOICES)
    estado = serializers.ChoiceField(choices=Venta.ESTADO_CHOICES, default='pendiente')
    precio_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    usuario_id = serializers.IntegerField()
    detalles = serializers.ListField(
        child=DetalleVentaInputSerializer(),
        required=False,
        allow_empty=True
    )

    def validate_usuario_id(self, value):
        if not Usuario.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'El usuario con ID {value} no existe')
        return value


class ActualizarVentaSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=Venta.TIPO_CHOICES, required=False)
    estado = serializers.ChoiceField(choices=Venta.ESTADO_CHOICES, required=False)
    precio_total = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    usuario_id = serializers.IntegerField(required=False)
    detalles = serializers.ListField(
        child=ActualizarDetalleVentaInputSerializer(),
        required=False
    )

    def validate_usuario_id(self, value):
        if value:
            if not Usuario.objects.filter(id=value).exists():
                raise serializers.ValidationError(f'El usuario con ID {value} no existe')
        return value
