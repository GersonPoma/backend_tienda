from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps_privadas.venta.views import VentaViewSet, ConfiguracionFidelizacionView

router = DefaultRouter()
router.register(r'ventas', VentaViewSet, basename='venta')

app_name = 'venta'

urlpatterns = [
    path('configuracion-fidelizacion/', ConfiguracionFidelizacionView.as_view(), name='configuracion-fidelizacion'),
    path('', include(router.urls)),
]