from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from cleaning.services import run_cleaning_pipeline_from_html
from rest_framework.generics import RetrieveAPIView
from .models import RawData as raw_data
from .serializers import CleaningResultSerializer
from crawling.models import Portales
from backend.services import _error_response

class cleaning_pip(APIView):
    """ Clase que permite realizar limpieza de HTML bruto en función de la plataforma recibida.
    """
    def post(self, request):
        """ Maneja peticiones HTTP post para interactuar con el módulo de limpiza.

        Args:
            request (Request): Recibe en el cuerpo de la petición un JSON con el html en bruto, la plataforma detectada
                               y la tupla de imágenes obtenidas en el scraper.

        Returns:
            Response: el output con los datos serializados = ['ide', 'cleaned_html', 'feature_vector', 'timestamp']
       
        Raises: 
            Response: mensaje con el tipo de error y tipo de estado HTTP
        """
        html = request.data.get("html")
        plat = request.data.get("plat")
        images = request.data.get("images")
        if not html:
            _error_response("HTML no proporcionado.")
 
        plataforma = Portales.objects.get(name=plat)
        clases_objetivo = plataforma.selectors

        try:
            result = run_cleaning_pipeline_from_html(html, clases_objetivo, images)
            serializer = CleaningResultSerializer(result)
            return Response({"result": serializer.data})
        except Exception as e:
            _error_response(f"error: {str(e)}", status.HTTP_500_INTERNAL_SERVER_ERROR)