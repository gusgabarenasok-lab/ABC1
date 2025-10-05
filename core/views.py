"""
Views (ViewSets) para SIPROSA MES
"""

from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.http import JsonResponse
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
from datetime import datetime, timedelta
import django

from .models import (
    # Catálogos
    Ubicacion, Maquina, Producto, Formula, EtapaProduccion, Turno,
    # Producción
    Lote, LoteEtapa, Parada, ControlCalidad,
    # Inventario
    Insumo, LoteInsumo, Repuesto, ProductoTerminado,
    # Mantenimiento
    TipoMantenimiento, OrdenTrabajo,
    # Incidentes
    TipoIncidente, Incidente,
)

from .serializers import (
    # Catálogos
    UbicacionSerializer, MaquinaSerializer, ProductoSerializer,
    FormulaSerializer, EtapaProduccionSerializer, TurnoSerializer,
    # Producción
    LoteSerializer, LoteListSerializer, LoteEtapaSerializer,
    ParadaSerializer, ControlCalidadSerializer,
    # Inventario
    InsumoSerializer, LoteInsumoSerializer, RepuestoSerializer,
    ProductoTerminadoSerializer,
    # Mantenimiento
    TipoMantenimientoSerializer, OrdenTrabajoSerializer, OrdenTrabajoListSerializer,
    # Incidentes
    TipoIncidenteSerializer, IncidenteSerializer, IncidenteListSerializer,
)

from .permissions import (
    IsAdmin, IsAdminOrSupervisor, IsAdminOrOperario
)


# ============================================
# CATÁLOGOS
# ============================================

class UbicacionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Ubicaciones"""
    queryset = Ubicacion.objects.all().order_by('codigo')
    serializer_class = UbicacionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre']
    ordering_fields = ['codigo', 'nombre', 'tipo']
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [IsAdminOrSupervisor]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]


class MaquinaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Máquinas"""
    queryset = Maquina.objects.select_related('ubicacion').all().order_by('codigo')
    serializer_class = MaquinaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre', 'fabricante', 'modelo']
    ordering_fields = ['codigo', 'nombre', 'tipo']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por estado activo/inactivo
        activa = self.request.query_params.get('activa', None)
        if activa is not None:
            activa = activa.lower() == 'true'
            queryset = queryset.filter(activa=activa)
        
        # Filtro por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo.upper())
        
        return queryset

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [IsAdminOrSupervisor]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]
    
    @action(detail=True, methods=['get'])
    def lotes_recientes(self, request, pk=None):
        """Endpoint: /api/maquinas/{id}/lotes_recientes/"""
        maquina = self.get_object()
        lotes = Lote.objects.filter(
            etapas__maquina=maquina
        ).distinct().order_by('-fecha_creacion')[:10]
        serializer = LoteListSerializer(lotes, many=True)
        return Response(serializer.data)


class ProductoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Productos"""
    queryset = Producto.objects.all().order_by('codigo')
    serializer_class = ProductoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre', 'principio_activo']
    ordering_fields = ['codigo', 'nombre']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por forma farmacéutica
        forma = self.request.query_params.get('forma', None)
        if forma:
            queryset = queryset.filter(forma_farmaceutica=forma.upper())
        
        # Filtro por activo
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            activo = activo.lower() == 'true'
            queryset = queryset.filter(activo=activo)
        
        return queryset
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [IsAdminOrSupervisor]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]


class FormulaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Fórmulas"""
    queryset = Formula.objects.select_related('producto', 'aprobada_por').all()
    serializer_class = FormulaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['producto__nombre', 'version']
    ordering_fields = ['fecha_vigencia_desde']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por producto
        producto_id = self.request.query_params.get('producto', None)
        if producto_id:
            queryset = queryset.filter(producto_id=producto_id)
        
        # Filtro por activa
        activa = self.request.query_params.get('activa', None)
        if activa is not None:
            activa = activa.lower() == 'true'
            queryset = queryset.filter(activa=activa)
        
        return queryset
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [IsAdminOrSupervisor]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]


class EtapaProduccionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Etapas de Producción"""
    queryset = EtapaProduccion.objects.all().order_by('orden_tipico')
    serializer_class = EtapaProduccionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre']
    ordering_fields = ['orden_tipico', 'codigo']
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [IsAdminOrSupervisor]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]


class TurnoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Turnos"""
    queryset = Turno.objects.all().order_by('codigo')
    serializer_class = TurnoSerializer
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [permissions.IsAuthenticated]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]


# ============================================
# PRODUCCIÓN
# ============================================

class LoteViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Lotes de Producción"""
    queryset = Lote.objects.select_related(
        'producto', 'formula', 'turno', 'supervisor', 'creado_por'
    ).all().order_by('-fecha_creacion')
    serializer_class = LoteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo_lote', 'producto__nombre']
    ordering_fields = ['fecha_creacion', 'fecha_planificada_inicio', 'codigo_lote']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado.upper())
        
        # Filtro por producto
        producto_id = self.request.query_params.get('producto', None)
        if producto_id:
            queryset = queryset.filter(producto_id=producto_id)
        
        # Filtro por turno
        turno_id = self.request.query_params.get('turno', None)
        if turno_id:
            queryset = queryset.filter(turno_id=turno_id)
        
        # Filtro por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        
        if fecha_desde:
            queryset = queryset.filter(fecha_real_inicio__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_real_inicio__lte=fecha_hasta)
        
        # Filtro por en proceso
        en_proceso = self.request.query_params.get('en_proceso', None)
        if en_proceso is not None:
            if en_proceso.lower() == 'true':
                queryset = queryset.filter(estado='EN_PROCESO')
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LoteListSerializer
        return LoteSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [IsAdminOrSupervisor]
        elif self.request.method == 'POST':
            perm_classes = [IsAdminOrSupervisor]  # Crear lote: Admin o Supervisor
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]
    
    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
    
    @action(detail=False, methods=['get'])
    def en_proceso(self, request):
        """Endpoint: /api/lotes/en_proceso/"""
        lotes = self.get_queryset().filter(estado='EN_PROCESO')
        serializer = self.get_serializer(lotes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def resumen_hoy(self, request):
        """Endpoint: /api/lotes/resumen_hoy/"""
        hoy = timezone.now().date()
        lotes_hoy = self.get_queryset().filter(
            fecha_real_inicio__date=hoy
        )
        
        resumen = {
            'fecha': hoy,
            'total_lotes': lotes_hoy.count(),
            'en_proceso': lotes_hoy.filter(estado='EN_PROCESO').count(),
            'finalizados': lotes_hoy.filter(estado='FINALIZADO').count(),
            'cantidad_total_planificada': sum(l.cantidad_planificada for l in lotes_hoy),
            'cantidad_total_producida': sum(l.cantidad_producida for l in lotes_hoy),
            'por_estado': list(
                lotes_hoy.values('estado')
                .annotate(total=Count('id'))
                .order_by('-total')
            ),
            'por_producto': list(
                lotes_hoy.values('producto__nombre')
                .annotate(total=Count('id'))
                .order_by('-total')
            )
        }
        
        return Response(resumen)


class LoteEtapaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Etapas de Lotes"""
    queryset = LoteEtapa.objects.select_related(
        'lote', 'etapa', 'maquina', 'operario'
    ).all().order_by('-fecha_inicio')
    serializer_class = LoteEtapaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['lote__codigo_lote', 'etapa__nombre']
    ordering_fields = ['fecha_inicio', 'orden']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por lote
        lote_id = self.request.query_params.get('lote', None)
        if lote_id:
            queryset = queryset.filter(lote_id=lote_id)
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado.upper())
        
        return queryset
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [IsAdminOrSupervisor]
        elif self.request.method == 'POST':
            perm_classes = [IsAdminOrOperario]  # Registrar etapa: Admin u Operario
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]


class ParadaViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Paradas"""
    queryset = Parada.objects.select_related(
        'lote_etapa', 'registrado_por'
    ).all().order_by('-fecha_inicio')
    serializer_class = ParadaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['descripcion', 'lote_etapa__lote__codigo_lote']
    ordering_fields = ['fecha_inicio', 'duracion_minutos']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo.upper())
        
        # Filtro por categoría
        categoria = self.request.query_params.get('categoria', None)
        if categoria:
            queryset = queryset.filter(categoria=categoria.upper())
        
        return queryset
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [IsAdminOrSupervisor]
        else:
            perm_classes = [IsAdminOrOperario]
        return [p() for p in perm_classes]


class ControlCalidadViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Controles de Calidad"""
    queryset = ControlCalidad.objects.select_related(
        'lote_etapa', 'controlado_por'
    ).all().order_by('-fecha_control')
    serializer_class = ControlCalidadSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tipo_control', 'lote_etapa__lote__codigo_lote']
    ordering_fields = ['fecha_control', 'conforme']
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [IsAdminOrSupervisor]
        else:
            perm_classes = [IsAdmin]  # Solo Calidad/Admin puede registrar controles
        return [p() for p in perm_classes]


# ============================================
# INVENTARIO
# ============================================

class InsumoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Insumos"""
    queryset = Insumo.objects.select_related('categoria').all().order_by('codigo')
    serializer_class = InsumoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre']
    ordering_fields = ['codigo', 'nombre']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por categoría
        categoria_id = self.request.query_params.get('categoria', None)
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        # Filtro por activo
        activo = self.request.query_params.get('activo', None)
        if activo is not None:
            activo = activo.lower() == 'true'
            queryset = queryset.filter(activo=activo)
        
        return queryset
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [permissions.IsAuthenticated]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]


class LoteInsumoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Lotes de Insumos"""
    queryset = LoteInsumo.objects.select_related(
        'insumo', 'ubicacion'
    ).all().order_by('fecha_vencimiento', 'fecha_recepcion')  # FEFO
    serializer_class = LoteInsumoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['insumo__nombre', 'codigo_lote_proveedor']
    ordering_fields = ['fecha_vencimiento', 'fecha_recepcion']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por insumo
        insumo_id = self.request.query_params.get('insumo', None)
        if insumo_id:
            queryset = queryset.filter(insumo_id=insumo_id)
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado.upper())
        
        return queryset
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [permissions.IsAuthenticated]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]


class RepuestoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Repuestos"""
    queryset = Repuesto.objects.select_related('ubicacion').all().order_by('codigo')
    serializer_class = RepuestoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre']
    ordering_fields = ['codigo', 'nombre', 'stock_actual']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por categoría
        categoria = self.request.query_params.get('categoria', None)
        if categoria:
            queryset = queryset.filter(categoria=categoria.upper())
        
        # Filtro por crítico
        critico = self.request.query_params.get('critico', None)
        if critico is not None:
            critico = critico.lower() == 'true'
            queryset = queryset.filter(critico=critico)
        
        return queryset
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [permissions.IsAuthenticated]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]


class ProductoTerminadoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Productos Terminados"""
    queryset = ProductoTerminado.objects.select_related(
        'lote', 'ubicacion'
    ).all().order_by('fecha_vencimiento')
    serializer_class = ProductoTerminadoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['lote__codigo_lote', 'lote__producto__nombre']
    ordering_fields = ['fecha_vencimiento', 'fecha_fabricacion']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado.upper())
        
        return queryset
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [permissions.IsAuthenticated]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]


# ============================================
# MANTENIMIENTO
# ============================================

class TipoMantenimientoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Tipos de Mantenimiento"""
    queryset = TipoMantenimiento.objects.all().order_by('codigo')
    serializer_class = TipoMantenimientoSerializer
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [permissions.IsAuthenticated]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]


class OrdenTrabajoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Órdenes de Trabajo"""
    queryset = OrdenTrabajo.objects.select_related(
        'tipo', 'maquina', 'creada_por', 'asignada_a'
    ).all().order_by('-fecha_creacion')
    serializer_class = OrdenTrabajoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'titulo', 'maquina__nombre']
    ordering_fields = ['fecha_creacion', 'fecha_planificada', 'prioridad']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por máquina
        maquina_id = self.request.query_params.get('maquina', None)
        if maquina_id:
            queryset = queryset.filter(maquina_id=maquina_id)
        
        # Filtro por tipo
        tipo_id = self.request.query_params.get('tipo', None)
        if tipo_id:
            queryset = queryset.filter(tipo_id=tipo_id)
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado.upper())
        
        # Filtro por prioridad
        prioridad = self.request.query_params.get('prioridad', None)
        if prioridad:
            queryset = queryset.filter(prioridad=prioridad.upper())
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OrdenTrabajoListSerializer
        return OrdenTrabajoSerializer
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [permissions.IsAuthenticated]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]
    
    def perform_create(self, serializer):
        serializer.save(creada_por=self.request.user)
    
    @action(detail=False, methods=['get'])
    def abiertas(self, request):
        """Endpoint: /api/ordenes-trabajo/abiertas/"""
        ordenes = self.get_queryset().exclude(estado__in=['COMPLETADA', 'CANCELADA'])
        serializer = self.get_serializer(ordenes, many=True)
        return Response(serializer.data)


# ============================================
# INCIDENTES
# ============================================

class TipoIncidenteViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Tipos de Incidente"""
    queryset = TipoIncidente.objects.all().order_by('codigo')
    serializer_class = TipoIncidenteSerializer
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [permissions.IsAuthenticated]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]


class IncidenteViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Incidentes"""
    queryset = Incidente.objects.select_related(
        'tipo', 'ubicacion', 'maquina', 'lote_afectado', 'reportado_por'
    ).all().order_by('-fecha_ocurrencia')
    serializer_class = IncidenteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'titulo', 'descripcion']
    ordering_fields = ['fecha_ocurrencia', 'severidad']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por tipo
        tipo_id = self.request.query_params.get('tipo', None)
        if tipo_id:
            queryset = queryset.filter(tipo_id=tipo_id)
        
        # Filtro por severidad
        severidad = self.request.query_params.get('severidad', None)
        if severidad:
            queryset = queryset.filter(severidad=severidad.upper())
        
        # Filtro por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado.upper())
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return IncidenteListSerializer
        return IncidenteSerializer
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [permissions.IsAuthenticated]
        else:
            perm_classes = [IsAdmin]
        return [p() for p in perm_classes]
    
    def perform_create(self, serializer):
        serializer.save(reportado_por=self.request.user)
    
    @action(detail=False, methods=['get'])
    def abiertos(self, request):
        """Endpoint: /api/incidentes/abiertos/"""
        incidentes = self.get_queryset().exclude(estado='CERRADO')
        serializer = self.get_serializer(incidentes, many=True)
        return Response(serializer.data)


# ============================================
# HOME & HEALTH CHECK
# ============================================

def home(request):
    """
    Página de bienvenida - redirige al panel de administración
    """
    from django.shortcuts import redirect
    return redirect('/admin/')


def health_check(request):
    """
    Devuelve el estado general del backend
    """
    db_ok = True
    try:
        connections['default'].cursor()
    except OperationalError:
        db_ok = False

    data = {
        "status": "ok" if db_ok else "error",
        "database": db_ok,
        "debug": settings.DEBUG,
        "django_version": django.get_version(),
        "server_time": datetime.now().isoformat(timespec='seconds'),
        "environment": "development" if settings.DEBUG else "production",
        "models_count": {
            "maquinas": Maquina.objects.count(),
            "productos": Producto.objects.count(),
            "lotes": Lote.objects.count(),
            "ordenes_trabajo": OrdenTrabajo.objects.count(),
            "incidentes": Incidente.objects.count(),
        }
    }

    return JsonResponse(data)