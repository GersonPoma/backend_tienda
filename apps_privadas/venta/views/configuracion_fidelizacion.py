from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, BasePermission
from apps_privadas.venta.models import ConfiguracionFidelizacion
from apps_privadas.venta.serializers import ConfiguracionFidelizacionSerializer


class PuedeGestionarFidelizacion(BasePermission):
    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return request.user.has_perm('venta.view_configuracionfidelizacion')
        return request.user.has_perm('venta.change_configuracionfidelizacion')


class ConfiguracionFidelizacionView(generics.RetrieveUpdateAPIView):
    serializer_class = ConfiguracionFidelizacionSerializer
    permission_classes = [IsAuthenticated, PuedeGestionarFidelizacion]

    def get_object(self):
        return ConfiguracionFidelizacion.obtener()
