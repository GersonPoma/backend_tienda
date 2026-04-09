from rest_framework import serializers
from apps_privadas.inventario.models import Multimedio, Producto


class MultimedioSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = Multimedio
        fields = ['id', 'nombre', 'tipo', 'producto', 'producto_nombre']
        read_only_fields = ['id']


class CrearMultimedioSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=255)
    tipo = serializers.ChoiceField(choices=Multimedio.TIPO_CHOICES)
    producto_id = serializers.IntegerField()

    def validate_producto_id(self, value):
        if not Producto.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'El producto con ID {value} no existe')
        return value


class ActualizarMultimedioSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=255, required=False)
    tipo = serializers.ChoiceField(choices=Multimedio.TIPO_CHOICES, required=False)
    producto_id = serializers.IntegerField(required=False)

    def validate_producto_id(self, value):
        if value and not Producto.objects.filter(id=value).exists():
            raise serializers.ValidationError(f'El producto con ID {value} no existe')
        return value
