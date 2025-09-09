from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from classifying.services import classify_fraud
from classifying.models import osintResult
from classifying.serializers import ClassificationResultSerializer
from backend.services import _error_response
import logging
logger = logging.getLogger("classifying")

class ClassifyByIDView(APIView):
    """ Clase que define peticiones consumubles Rest para interacción con módulo
    de clasificación, análisis utilizando metodologías OSINT
    """
    def post(self, request, ide):
        """ Manejo de peticiones post, se recibe el ide de un anuncio por parámetros en la URL para 
        realizar el análsis de sus características.

        Args:
            request (Request): no aplica en este caso.
            ide (str): Identificador del anuncio.

        Returns:
            Response: Respuesta con el output del análsis.
            
        Raises:
            HTTP_400_BAD_REQUEST: en caso de error en el análisis.
            Exception (HTTP_500_INTERNAL_SERVER_ERROR): en caso de fallo en el bloque de código de try, desde el análsis, 
                                                        query a la base de datos y return (response).
        """
        logger.info(f"Se recibe petición de análisis de add: {ide}")
        try:
            logger.info("Procesando análisis ...")
            result = classify_fraud(ide)
            if result is None:
                logger.error("No se pudo clasificar el anuncio: ", ide)
                _error_response(f"No se pudo clasificar el anuncio con ID: {ide}",status.HTTP_400_BAD_REQUEST)
            
            # Creación o update del modelo OsintResult 
            # (almacena nivel confianza, probabilidades de fraude, flag del precio.. entre otros)
            osintResult.objects.update_or_create(
                ide=ide,
                defaults=result
            )
            
            result = osintResult.objects.get(ide=ide)
            serializer = ClassificationResultSerializer(result)
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error("Exception en ClassifyByIDView:", str(e))
            _error_response(f"Error interno del servidor: {str(e)}",status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get(self, request, ide):
        """ Manejo de peticiones get para obtener información de un análisis previamente analizado.
        Muy conveniente para el módulo de delivering o para el front.

        Args:
            request (Request): no aplica en este caso
            ide (str): Identificador del anuncio a devolver.

        Returns:
            Response: respuesta del output del análisis serializado.
            
        Raises:
            DoesNotExist: en caso de no existir el objeto en la base de datos.
        """
        try:
            result = osintResult.objects.get(ide=ide)
            serializer = ClassificationResultSerializer(result)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except osintResult.DoesNotExist:
            _error_response("Resultado no encontrado", status.HTTP_404_NOT_FOUND)