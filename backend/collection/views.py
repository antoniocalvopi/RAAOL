from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from collection.service import run_collection_pipeline
from backend.services import _error_response

class scrape_view(APIView):
    """ Clase que define endpoints para interactuar con el módulo scraper"""
    def get(self, request):
        """ Gestiona peticiones HTTP post para realizar el scrap de una web.

        Args:
            request (Request): recibe parámetros como url del anuncio y proxy (si aplica)

        Returns:
            Response: html en crudo y tupla con imágenes obtenidas.
            
        Raises:
            Exception: en caso de fallo el pipeline de scraping
        """
        url = request.query_params.get("url")
        plat = request.query_params.get("plat")
        proxy = request.query_params.get("proxy")
        if not url:
            return _error_response("Parámetro 'url' es requerido.",status.HTTP_400_BAD_REQUEST)
            
        try:
            html, images = run_collection_pipeline(plat, url, proxy)
            return Response({"html": html, "images": images}, status=status.HTTP_200_OK)
        except Exception as e:
            return _error_response(str(e),status.HTTP_500_INTERNAL_SERVER_ERROR)
