"""
URLs para SIPROSA MES
"""

from django.urls import path
from rest_framework import routers
from .views import (
    # Catálogos
    UbicacionViewSet, MaquinaViewSet, ProductoViewSet, FormulaViewSet,
    EtapaProduccionViewSet, TurnoViewSet,
    # Producción
    LoteViewSet, LoteEtapaViewSet, ParadaViewSet, ControlCalidadViewSet,
    # Inventario
    InsumoViewSet, LoteInsumoViewSet, RepuestoViewSet, ProductoTerminadoViewSet,
    # Mantenimiento
    TipoMantenimientoViewSet, OrdenTrabajoViewSet,
    # Incidentes
    TipoIncidenteViewSet, IncidenteViewSet,
    # Health check
    health_check,
)

router = routers.DefaultRouter()

# Catálogos Maestros
router.register(r'ubicaciones', UbicacionViewSet)
router.register(r'maquinas', MaquinaViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'formulas', FormulaViewSet)
router.register(r'etapas-produccion', EtapaProduccionViewSet)
router.register(r'turnos', TurnoViewSet)

# Producción
router.register(r'lotes', LoteViewSet)
router.register(r'lotes-etapas', LoteEtapaViewSet)
router.register(r'paradas', ParadaViewSet)
router.register(r'controles-calidad', ControlCalidadViewSet)

# Inventario
router.register(r'insumos', InsumoViewSet)
router.register(r'lotes-insumo', LoteInsumoViewSet)
router.register(r'repuestos', RepuestoViewSet)
router.register(r'productos-terminados', ProductoTerminadoViewSet)

# Mantenimiento
router.register(r'tipos-mantenimiento', TipoMantenimientoViewSet)
router.register(r'ordenes-trabajo', OrdenTrabajoViewSet)

# Incidentes
router.register(r'tipos-incidente', TipoIncidenteViewSet)
router.register(r'incidentes', IncidenteViewSet)

urlpatterns = [
    path("health/", health_check, name="health_check"),
] + router.urls