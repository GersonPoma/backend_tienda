from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps_privadas.ia.views.alertas import AlertaReabastecimientoViewSet
from apps_privadas.ia.views.dashboard import DashboardVentasView
from apps_privadas.ia.views.prediccion_detalle import PrediccionDetalleView
from apps_privadas.ia.views.reentrenar import ReentrenarView
from apps_privadas.ia.views.sugerencia_compra import (
    SugerenciaCompraViewSet,
    SugerenciaCompraDetalleViewSet,
)

router = DefaultRouter()
router.register('ia/alertas', AlertaReabastecimientoViewSet, basename='alertas-reabastecimiento')
router.register('ia/sugerencias-compra', SugerenciaCompraViewSet, basename='sugerencias-compra')
router.register(
    'ia/sugerencias-compra-detalles',
    SugerenciaCompraDetalleViewSet,
    basename='sugerencias-compra-detalles',
)

urlpatterns = [
    path('', include(router.urls)),
    path('ia/dashboard/', DashboardVentasView.as_view(), name='ia-dashboard'),
    path('ia/prediccion-detalle/', PrediccionDetalleView.as_view(), name='ia-prediccion-detalle'),
    path('ia/reentrenar/', ReentrenarView.as_view(), name='ia-reentrenar'),
]
