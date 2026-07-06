from rest_framework import serializers
from apps_privadas.venta.models import ConfiguracionFidelizacion


class ConfiguracionFidelizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionFidelizacion
        fields = ['monto_minimo_acumulado', 'monto_descuento', 'activo', 'fecha_actualizacion']
        read_only_fields = ['fecha_actualizacion']
