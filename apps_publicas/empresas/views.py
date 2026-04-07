from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps_publicas.empresas.models import Empresa, Dominio
from apps_publicas.empresas.serializers import (
    EmpresaRegistroSerializer,
    EmpresaCreatedSerializer
)
from apps_publicas.empresas.services import (
    EmpresaRegistroService,
    EmpresaListaService
)


class EmpresaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar empresas.

    Endpoints:
    - POST /api/empresas/register/ - Registrar nueva empresa
    - GET /api/empresas/ - Listar todas las empresas
    - GET /api/empresas/{id}/ - Obtener empresa específica
    """

    queryset = Empresa.objects.filter(is_active=True)
    permission_classes = [AllowAny]  # En producción, cambiar a IsAuthenticated

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def registrar(self, request):
        """
        Endpoint para registrar una nueva empresa.

        Body JSON esperado:
        {
            "nombre": "Mi Tienda",
            "correo": "info@mitienda.com",
            "super_admin": {
                "username": "admin",
                "email": "admin@mitienda.com",
                "password": "Contraseña123!",
                "password_confirm": "Contraseña123!"
            }
        }

        Respuesta exitosa (201):
        {
            "success": true,
            "empresa_id": 1,
            "nombre": "Mi Tienda",
            "schema_name": "mi_tienda",
            "dominio": "mi-tienda.localhost",
            "super_admin_username": "admin",
            "mensaje": "Empresa creada..."
        }

        Respuesta de error (400):
        {
            "success": false,
            "errors": {
                "nombre": ["El nombre solo puede contener..."],
                "super_admin": {
                    "password": ["Las contraseñas no coinciden"]
                }
            }
        }
        """

        serializer = EmpresaRegistroSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    'success': False,
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener datos validados
        nombre = serializer.validated_data['nombre']
        correo = serializer.validated_data['correo']
        super_admin_data = serializer.validated_data['super_admin']

        # Remover password_confirm ya que no lo necesitamos
        super_admin_data.pop('password_confirm', None)

        # Crear empresa con el servicio
        resultado = EmpresaRegistroService.crear_empresa_con_admin(
            nombre,
            correo,
            super_admin_data
        )

        if resultado['success']:
            response_serializer = EmpresaCreatedSerializer(resultado)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {
                    'success': False,
                    'error': resultado.get('error', 'Error desconocido')
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def listar_todas(self, request):
        """
        Endpoint para listar todas las empresas activas.

        Respuesta:
        [
            {
                "id": 1,
                "nombre": "Tienda Amiga",
                "correo": "info@tienda-amiga.com",
                "schema_name": "tienda_amiga",
                "fecha_creacion": "2024-04-07T10:30:00Z"
            }
        ]
        """
        empresas = EmpresaListaService.obtener_todas_empresas()
        return Response(empresas, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        Obtener información detallada de una empresa específica.

        Respuesta:
        {
            "id": 1,
            "nombre": "Tienda Amiga",
            "correo": "info@tienda-amiga.com",
            "schema_name": "tienda_amiga",
            "dominio": "tienda-amiga.localhost",
            "fecha_creacion": "2024-04-07T10:30:00Z"
        }
        """
        empresa = EmpresaListaService.obtener_empresa_por_id(pk)

        if empresa is None:
            return Response(
                {'error': 'Empresa no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(empresa, status=status.HTTP_200_OK)

