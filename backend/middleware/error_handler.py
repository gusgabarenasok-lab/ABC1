import logging
import traceback
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger(__name__)

class GlobalErrorMiddleware:
    """
    Middleware para capturar excepciones globales,
    registrar el error y devolver una respuesta JSON segura.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            logger.exception(f"🔥 Excepción capturada: {str(e)}")

            if settings.DEBUG:
                # En modo desarrollo mostramos más información
                return JsonResponse({
                    "error": str(e),
                    "type": e.__class__.__name__,
                    "trace": traceback.format_exc().splitlines(),
                }, status=500)
            else:
                # En modo producción devolvemos un mensaje genérico
                return JsonResponse({
                    "error": "Ocurrió un error interno. El incidente fue registrado.",
                }, status=500)

