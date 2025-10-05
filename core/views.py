# core/views.py
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import Maquina, Produccion
from .serializers import (
    MaquinaSerializer, 
    ProduccionSerializer,
    ProduccionListSerializer
)
from .permissions import (
    IsAdmin, IsAdminOrSupervisor, IsAdminOrOperario
)


class MaquinaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Máquinas.
    
    Permisos:
    - Ver: Admin o Supervisor
    - Crear: Solo Admin
    - Editar/Eliminar: Solo Admin
    
    Filtros disponibles:
    - ?activa=true/false
    - ?search=nombre
    """
    queryset = Maquina.objects.all().order_by('nombre')
    serializer_class = MaquinaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'ubicacion', 'descripcion']
    ordering_fields = ['nombre', 'ubicacion', 'activa']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por estado activo/inactivo
        activa = self.request.query_params.get('activa', None)
        if activa is not None:
            activa = activa.lower() == 'true'
            queryset = queryset.filter(activa=activa)
        
        return queryset

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [IsAdminOrSupervisor]     # ver: Admin o Supervisor
        elif self.request.method == 'POST':
            perm_classes = [IsAdmin]                 # crear: solo Admin
        elif self.request.method in ['PUT', 'PATCH', 'DELETE']:
            perm_classes = [IsAdmin]                 # editar/borrar: solo Admin
        else:
            perm_classes = [permissions.IsAuthenticated]
        return [p() for p in perm_classes]
    
    @action(detail=True, methods=['get'])
    def producciones_recientes(self, request, pk=None):
        """
        Endpoint personalizado: /api/maquinas/{id}/producciones_recientes/
        Retorna las últimas 10 producciones de esta máquina
        """
        maquina = self.get_object()
        producciones = maquina.producciones.all().order_by('-fecha_inicio')[:10]
        serializer = ProduccionListSerializer(producciones, many=True)
        return Response(serializer.data)


class ProduccionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Producción.
    
    Permisos:
    - Ver: Admin o Supervisor
    - Crear: Admin u Operario
    - Editar/Eliminar: Solo Admin
    
    Filtros disponibles:
    - ?maquina=1
    - ?turno=M/T/N
    - ?fecha_desde=2025-01-01
    - ?fecha_hasta=2025-12-31
    - ?en_proceso=true/false
    - ?search=codigo_lote o producto
    """
    queryset = Produccion.objects.select_related('maquina').all().order_by('-fecha_inicio')
    serializer_class = ProduccionSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo_lote', 'producto', 'maquina__nombre']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'cantidad_producida']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro por máquina
        maquina_id = self.request.query_params.get('maquina', None)
        if maquina_id:
            queryset = queryset.filter(maquina_id=maquina_id)
        
        # Filtro por turno
        turno = self.request.query_params.get('turno', None)
        if turno:
            queryset = queryset.filter(turno=turno.upper())
        
        # Filtro por rango de fechas
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        
        if fecha_desde:
            queryset = queryset.filter(fecha_inicio__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_inicio__lte=fecha_hasta)
        
        # Filtro por estado (en proceso o finalizados)
        en_proceso = self.request.query_params.get('en_proceso', None)
        if en_proceso is not None:
            if en_proceso.lower() == 'true':
                queryset = queryset.filter(fecha_fin__isnull=True)
            else:
                queryset = queryset.filter(fecha_fin__isnull=False)
        
        return queryset
    
    def get_serializer_class(self):
        """Usa serializer simplificado para listados"""
        if self.action == 'list':
            return ProduccionListSerializer
        return ProduccionSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            perm_classes = [IsAdminOrSupervisor]     # ver: Admin o Supervisor
        elif self.request.method == 'POST':
            perm_classes = [IsAdminOrOperario]       # crear: Admin u Operario
        elif self.request.method in ['PUT', 'PATCH', 'DELETE']:
            perm_classes = [IsAdmin]                 # editar/borrar: solo Admin
        else:
            perm_classes = [permissions.IsAuthenticated]
        return [p() for p in perm_classes]
    
    @action(detail=False, methods=['get'])
    def en_proceso(self, request):
        """
        Endpoint personalizado: /api/producciones/en_proceso/
        Retorna solo las producciones que están actualmente en proceso
        """
        producciones = self.get_queryset().filter(fecha_fin__isnull=True)
        serializer = self.get_serializer(producciones, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def resumen_hoy(self, request):
        """
        Endpoint personalizado: /api/producciones/resumen_hoy/
        Retorna un resumen de producción del día actual
        """
        hoy = timezone.now().date()
        producciones_hoy = self.get_queryset().filter(
            fecha_inicio__date=hoy
        )
        
        resumen = {
            'fecha': hoy,
            'total_producciones': producciones_hoy.count(),
            'en_proceso': producciones_hoy.filter(fecha_fin__isnull=True).count(),
            'finalizadas': producciones_hoy.filter(fecha_fin__isnull=False).count(),
            'cantidad_total_producida': sum(p.cantidad_producida for p in producciones_hoy),
            'por_turno': {
                'manana': producciones_hoy.filter(turno='M').count(),
                'tarde': producciones_hoy.filter(turno='T').count(),
                'noche': producciones_hoy.filter(turno='N').count(),
            },
            'por_maquina': list(
                producciones_hoy.values('maquina__nombre')
                .annotate(total=Count('id'))
                .order_by('-total')
            )
        }
        
        return Response(resumen)


def health_check(request):
    """
    Devuelve el estado general del backend:
    - Base de datos
    - Versión de Django
    - Modo DEBUG
    - Hora del servidor
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
        "environment": "development" if settings.DEBUG else "production"
    }

    return JsonResponse(data)
