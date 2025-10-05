from django.urls import path
from rest_framework import routers
from .views import MaquinaViewSet, ProduccionViewSet, health_check

router = routers.DefaultRouter()
router.register(r'maquinas', MaquinaViewSet)
router.register(r'producciones', ProduccionViewSet)

urlpatterns = [
    path("health/", health_check, name="health_check"),
] + router.urls

