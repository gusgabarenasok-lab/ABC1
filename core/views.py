# core/views.py
from rest_framework import viewsets, permissions
from .models import Maquina, Produccion
from .serializers import MaquinaSerializer, ProduccionSerializer
from .permissions import (
    IsAdmin, IsAdminOrSupervisor, IsAdminOrOperario
)
from django.http import JsonResponse
from django.conf import settings
from django.db import connections
from django.db.utils import OperationalError
import django
from datetime import datetime

class MaquinaViewSet(viewsets.ModelViewSet):
    queryset = Maquina.objects.all()
    serializer_class = MaquinaSerializer

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


class ProduccionViewSet(viewsets.ModelViewSet):
    queryset = Produccion.objects.all()
    serializer_class = ProduccionSerializer

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
