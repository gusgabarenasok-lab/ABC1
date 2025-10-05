"""
Serializers para SIPROSA MES
Nota: Esta es una versión inicial. Se expandirá según se necesite.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    # Usuarios
    UserProfile, Rol,
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


# ============================================
# USUARIOS
# ============================================

class UserSerializer(serializers.ModelSerializer):
    """Serializer básico de usuario"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer de perfil de usuario"""
    usuario = UserSerializer(source='user', read_only=True)
    area_display = serializers.CharField(source='get_area_display', read_only=True)
    turno_display = serializers.CharField(source='get_turno_habitual_display', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'usuario', 'legajo', 'area', 'area_display', 
                  'turno_habitual', 'turno_display', 'telefono', 'fecha_ingreso', 'activo']
        read_only_fields = ['id']


# ============================================
# CATÁLOGOS
# ============================================

class UbicacionSerializer(serializers.ModelSerializer):
    """Serializer de ubicaciones"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Ubicacion
        fields = ['id', 'codigo', 'nombre', 'tipo', 'tipo_display', 'descripcion', 'activa']
        read_only_fields = ['id']


class MaquinaSerializer(serializers.ModelSerializer):
    """Serializer de máquinas"""
    ubicacion_nombre = serializers.CharField(source='ubicacion.nombre', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = Maquina
        fields = [
            'id', 'codigo', 'nombre', 'tipo', 'tipo_display', 'fabricante', 'modelo',
            'ubicacion', 'ubicacion_nombre', 'descripcion', 'capacidad_nominal',
            'unidad_capacidad', 'activa', 'fecha_instalacion'
        ]
        read_only_fields = ['id']


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer de productos"""
    forma_display = serializers.CharField(source='get_forma_farmaceutica_display', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id', 'codigo', 'nombre', 'forma_farmaceutica', 'forma_display',
            'principio_activo', 'concentracion', 'unidad_medida',
            'lote_minimo', 'lote_optimo', 'activo'
        ]
        read_only_fields = ['id']


class FormulaSerializer(serializers.ModelSerializer):
    """Serializer de fórmulas"""
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    aprobada_por_nombre = serializers.CharField(source='aprobada_por.get_full_name', read_only=True)
    
    class Meta:
        model = Formula
        fields = [
            'id', 'producto', 'producto_nombre', 'version',
            'fecha_vigencia_desde', 'fecha_vigencia_hasta',
            'rendimiento_teorico', 'tiempo_estimado_horas',
            'aprobada_por', 'aprobada_por_nombre', 'activa'
        ]
        read_only_fields = ['id']


class EtapaProduccionSerializer(serializers.ModelSerializer):
    """Serializer de etapas de producción"""
    
    class Meta:
        model = EtapaProduccion
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'orden_tipico', 'activa']
        read_only_fields = ['id']


class TurnoSerializer(serializers.ModelSerializer):
    """Serializer de turnos"""
    nombre_display = serializers.CharField(source='nombre', read_only=True)
    
    class Meta:
        model = Turno
        fields = ['id', 'codigo', 'nombre', 'nombre_display', 'hora_inicio', 'hora_fin', 'activo']
        read_only_fields = ['id']


# ============================================
# PRODUCCIÓN
# ============================================

class LoteListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de lotes"""
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    supervisor_nombre = serializers.CharField(source='supervisor.get_full_name', read_only=True)
    rendimiento = serializers.ReadOnlyField(source='rendimiento_porcentaje')
    
    class Meta:
        model = Lote
        fields = [
            'id', 'codigo_lote', 'producto', 'producto_nombre',
            'estado', 'estado_display', 'cantidad_planificada', 'cantidad_producida',
            'rendimiento', 'fecha_real_inicio', 'fecha_real_fin',
            'supervisor', 'supervisor_nombre'
        ]


class LoteSerializer(serializers.ModelSerializer):
    """Serializer completo de lotes"""
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    formula_version = serializers.CharField(source='formula.version', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    turno_nombre = serializers.CharField(source='turno.nombre', read_only=True)
    supervisor_nombre = serializers.CharField(source='supervisor.get_full_name', read_only=True)
    creado_por_nombre = serializers.CharField(source='creado_por.get_full_name', read_only=True)
    rendimiento = serializers.ReadOnlyField(source='rendimiento_porcentaje')
    
    class Meta:
        model = Lote
        fields = [
            'id', 'codigo_lote', 'producto', 'producto_nombre',
            'formula', 'formula_version', 'cantidad_planificada', 'cantidad_producida',
            'cantidad_rechazada', 'unidad', 'estado', 'estado_display',
            'prioridad', 'prioridad_display', 'fecha_planificada_inicio',
            'fecha_real_inicio', 'fecha_planificada_fin', 'fecha_real_fin',
            'turno', 'turno_nombre', 'supervisor', 'supervisor_nombre',
            'observaciones', 'creado_por', 'creado_por_nombre',
            'fecha_creacion', 'rendimiento'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'creado_por']
    
    def validate(self, data):
        """Validaciones de negocio"""
        # Validar fechas
        if data.get('fecha_real_fin') and data.get('fecha_real_inicio'):
            if data['fecha_real_fin'] < data['fecha_real_inicio']:
                raise serializers.ValidationError({
                    "fecha_real_fin": "La fecha de fin debe ser posterior a la fecha de inicio"
                })
        
        return data


class LoteEtapaSerializer(serializers.ModelSerializer):
    """Serializer de etapas de lote"""
    lote_codigo = serializers.CharField(source='lote.codigo_lote', read_only=True)
    etapa_nombre = serializers.CharField(source='etapa.nombre', read_only=True)
    maquina_nombre = serializers.CharField(source='maquina.nombre', read_only=True)
    operario_nombre = serializers.CharField(source='operario.get_full_name', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = LoteEtapa
        fields = [
            'id', 'lote', 'lote_codigo', 'etapa', 'etapa_nombre',
            'orden', 'maquina', 'maquina_nombre', 'estado', 'estado_display',
            'fecha_inicio', 'fecha_fin', 'duracion_minutos',
            'operario', 'operario_nombre', 'cantidad_entrada', 'cantidad_salida',
            'cantidad_merma', 'porcentaje_rendimiento', 'observaciones'
        ]
        read_only_fields = ['id', 'duracion_minutos', 'porcentaje_rendimiento']


class ParadaSerializer(serializers.ModelSerializer):
    """Serializer de paradas"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    
    class Meta:
        model = Parada
        fields = [
            'id', 'lote_etapa', 'tipo', 'tipo_display',
            'categoria', 'categoria_display', 'fecha_inicio', 'fecha_fin',
            'duracion_minutos', 'descripcion', 'solucion', 'registrado_por'
        ]
        read_only_fields = ['id', 'duracion_minutos']


class ControlCalidadSerializer(serializers.ModelSerializer):
    """Serializer de controles de calidad"""
    
    class Meta:
        model = ControlCalidad
        fields = [
            'id', 'lote_etapa', 'tipo_control', 'valor_medido', 'unidad',
            'valor_minimo', 'valor_maximo', 'conforme',
            'fecha_control', 'controlado_por', 'observaciones'
        ]
        read_only_fields = ['id', 'conforme', 'fecha_control']


# ============================================
# INVENTARIO
# ============================================

class InsumoSerializer(serializers.ModelSerializer):
    """Serializer de insumos"""
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    stock_disponible = serializers.ReadOnlyField(source='stock_actual')
    
    class Meta:
        model = Insumo
        fields = [
            'id', 'codigo', 'nombre', 'categoria', 'categoria_nombre',
            'unidad_medida', 'stock_minimo', 'stock_maximo', 'punto_reorden',
            'stock_disponible', 'activo'
        ]
        read_only_fields = ['id']


class LoteInsumoSerializer(serializers.ModelSerializer):
    """Serializer de lotes de insumo"""
    insumo_nombre = serializers.CharField(source='insumo.nombre', read_only=True)
    ubicacion_nombre = serializers.CharField(source='ubicacion.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    dias_vencimiento = serializers.ReadOnlyField(source='dias_para_vencimiento')
    
    class Meta:
        model = LoteInsumo
        fields = [
            'id', 'insumo', 'insumo_nombre', 'codigo_lote_proveedor',
            'fecha_recepcion', 'fecha_vencimiento', 'dias_vencimiento',
            'cantidad_inicial', 'cantidad_actual', 'unidad',
            'ubicacion', 'ubicacion_nombre', 'ubicacion_detalle',
            'estado', 'estado_display', 'proveedor'
        ]
        read_only_fields = ['id']


class RepuestoSerializer(serializers.ModelSerializer):
    """Serializer de repuestos"""
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    ubicacion_nombre = serializers.CharField(source='ubicacion.nombre', read_only=True)
    
    class Meta:
        model = Repuesto
        fields = [
            'id', 'codigo', 'nombre', 'categoria', 'categoria_display',
            'stock_minimo', 'stock_actual', 'punto_reorden',
            'ubicacion', 'ubicacion_nombre', 'critico', 'activo'
        ]
        read_only_fields = ['id']


class ProductoTerminadoSerializer(serializers.ModelSerializer):
    """Serializer de productos terminados"""
    lote_codigo = serializers.CharField(source='lote.codigo_lote', read_only=True)
    producto_nombre = serializers.CharField(source='lote.producto.nombre', read_only=True)
    ubicacion_nombre = serializers.CharField(source='ubicacion.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = ProductoTerminado
        fields = [
            'id', 'lote', 'lote_codigo', 'producto_nombre',
            'cantidad', 'unidad', 'fecha_fabricacion', 'fecha_vencimiento',
            'ubicacion', 'ubicacion_nombre', 'ubicacion_detalle',
            'estado', 'estado_display'
        ]
        read_only_fields = ['id']


# ============================================
# MANTENIMIENTO
# ============================================

class TipoMantenimientoSerializer(serializers.ModelSerializer):
    """Serializer de tipos de mantenimiento"""
    
    class Meta:
        model = TipoMantenimiento
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'activo']
        read_only_fields = ['id']


class OrdenTrabajoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de OT"""
    maquina_nombre = serializers.CharField(source='maquina.nombre', read_only=True)
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    
    class Meta:
        model = OrdenTrabajo
        fields = [
            'id', 'codigo', 'maquina', 'maquina_nombre',
            'tipo', 'tipo_nombre', 'prioridad', 'prioridad_display',
            'estado', 'estado_display', 'titulo', 'fecha_creacion',
            'fecha_planificada', 'asignada_a'
        ]


class OrdenTrabajoSerializer(serializers.ModelSerializer):
    """Serializer completo de órdenes de trabajo"""
    maquina_nombre = serializers.CharField(source='maquina.nombre', read_only=True)
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    creada_por_nombre = serializers.CharField(source='creada_por.get_full_name', read_only=True)
    
    class Meta:
        model = OrdenTrabajo
        fields = [
            'id', 'codigo', 'tipo', 'tipo_nombre', 'maquina', 'maquina_nombre',
            'prioridad', 'prioridad_display', 'estado', 'estado_display',
            'titulo', 'descripcion', 'fecha_creacion', 'fecha_planificada',
            'fecha_inicio', 'fecha_fin', 'duracion_real_horas',
            'creada_por', 'creada_por_nombre', 'asignada_a', 'completada_por',
            'trabajo_realizado', 'observaciones', 'requiere_parada_produccion',
            'costo_estimado', 'costo_real'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'duracion_real_horas', 'creada_por']


# ============================================
# INCIDENTES
# ============================================

class TipoIncidenteSerializer(serializers.ModelSerializer):
    """Serializer de tipos de incidente"""
    
    class Meta:
        model = TipoIncidente
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'requiere_investigacion', 'activo']
        read_only_fields = ['id']


class IncidenteListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de incidentes"""
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)
    severidad_display = serializers.CharField(source='get_severidad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    reportado_por_nombre = serializers.CharField(source='reportado_por.get_full_name', read_only=True)
    
    class Meta:
        model = Incidente
        fields = [
            'id', 'codigo', 'tipo', 'tipo_nombre',
            'severidad', 'severidad_display', 'estado', 'estado_display',
            'titulo', 'fecha_ocurrencia', 'reportado_por', 'reportado_por_nombre'
        ]


class IncidenteSerializer(serializers.ModelSerializer):
    """Serializer completo de incidentes"""
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)
    ubicacion_nombre = serializers.CharField(source='ubicacion.nombre', read_only=True)
    maquina_nombre = serializers.CharField(source='maquina.nombre', read_only=True, allow_null=True)
    lote_codigo = serializers.CharField(source='lote_afectado.codigo_lote', read_only=True, allow_null=True)
    severidad_display = serializers.CharField(source='get_severidad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    reportado_por_nombre = serializers.CharField(source='reportado_por.get_full_name', read_only=True)
    
    class Meta:
        model = Incidente
        fields = [
            'id', 'codigo', 'tipo', 'tipo_nombre', 'severidad', 'severidad_display',
            'estado', 'estado_display', 'titulo', 'descripcion',
            'fecha_ocurrencia', 'ubicacion', 'ubicacion_nombre',
            'maquina', 'maquina_nombre', 'lote_afectado', 'lote_codigo',
            'reportado_por', 'reportado_por_nombre', 'fecha_reporte',
            'asignado_a', 'impacto_produccion', 'impacto_calidad',
            'impacto_seguridad', 'requiere_notificacion_anmat'
        ]
        read_only_fields = ['id', 'fecha_reporte', 'reportado_por']