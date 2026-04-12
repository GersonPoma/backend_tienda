from rest_framework import serializers
from apps_privadas.inventario.models import Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']


class CrearCategoriaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100)

    def validate_nombre(self, value):
        if Categoria.objects.filter(nombre=value).exists():
            raise serializers.ValidationError(f'La categoría "{value}" ya existe')
        return value


class ActualizarCategoriaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=100, required=False)

    def validate_nombre(self, value):
        if value:
            existe = Categoria.objects.filter(nombre=value).exclude(
                id=self.instance.id if self.instance else None
            ).exists()
            if existe:
                raise serializers.ValidationError(f'La categoría "{value}" ya existe')
        return value
