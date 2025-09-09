from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import crawling_check
from backend.services import _error_response
from rest_framework import status

class check_url(APIView):
    
    """ Clase que verifica y comprueba la compatibilidad de la URL"""

    def post(self, request):
        """ Procesa peticiones post para verificación de una url
        
        Args:
            request (Request): petición HTTP con los datos .
            
        Returns:
            Response: respuesta JSON con información de la validación y tipo de plataforma detectada.
            
        """
        url = request.data.get("url")

        if not url:
            return _error_response("URL no proporcionada.",status.HTTP_400_BAD_REQUEST)
        try:
            output = self._validate_url(url)
            return Response(output, status=status.HTTP_200_OK)
        except Exception as e:
            return _error_response(f"Error interno al procesar la URL: {str(e)}",status.HTTP_500_INTERNAL_SERVER_ERROR)
     
    def _validate_url(self, url):
        """ Maneja la verificacion y validación de la estructura de la URL a través del método crawling_check()

        Args:
            url (str): url a verificar

        Returns:
            Dict[str, bool, bool, bool]: diccionario con flags del análisis y plataforma detectada, los flags son Bool. 
        """
        plataforma_admitida, url_valida, conexion_ok, plataforma = crawling_check(url)
        
        return {
            "plataforma": plataforma,
            "plataforma_admitida": plataforma_admitida,
            "url_valida": url_valida,
            "conexion_ok": conexion_ok,
        }