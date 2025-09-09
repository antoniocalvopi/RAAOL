from django.shortcuts import render
from rest_framework.views import APIView
import requests
from datetime import datetime
from cleaning.models import RawData
from delivering.services import IA_GENERATION
import logging

logger = logging.getLogger("delivering")


class DeliverResultView(APIView):
    """ Vista para obtener, mostrar e interpretar el resultado del análisis de un anuncio."""
    def get(self, request, ide):
        """ Maneja la solicitud GET para obtener el resultado del análisis.

        Args:
            request (HttpRequest): Objeto de la petición HTTP.
            ide (str): Identificador único del anuncio a analizar.

        Returns:
            HttpResponse: Renderiza plantilla con los resultados del análisis o mensaje de error.
        """
        logger.info(f"Inicio de proceso de delivering para ide={ide}")

        try:
            url = f"http://localhost:8001/api/classify/{ide}/"
            logger.info(f"Solicitando datos de análisis a {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            result_data = response.json()
            logger.info(f"Datos recibidos correctamente para ide={ide}")
        except Exception as e:
            logger.error(f"Error al obtener resultado para ide={ide}: {str(e)}")
            return render(request, "delivering/result.html", {
                "ide": ide,
                "result_message": f"Error al obtener resultado: {str(e)}",
                "ia_message": None,
                "verifications": None,
                "probabilidad": 0,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

        prob = result_data.get("fraud_prob", 0) * 100
        timestamp = result_data.get("timestamp")

        if prob <= 30:
            result_message = f"El anuncio tiene una baja probabilidad de fraude ({prob:.2f}%)."
        elif prob <= 60:
            result_message = f"El anuncio tiene una probabilidad moderada de fraude ({prob:.2f}%)."
        else:
            result_message = f"El anuncio tiene alta probabilidad de fraude ({prob:.2f}%)."

        logger.info(f"Probabilidad de fraude para ide={ide}: {prob:.2f}% - Mensaje: {result_message}")

        ia = IA_GENERATION()
        try:
            raw_data = RawData.objects.get(ide=result_data.get("ide"))
            feature_vector = raw_data.feature_vector
            logger.info(f"Feature vector obtenido para ide={ide}")
            ia_message = ia.run(result_data, feature_vector)
            logger.info(f"Explicación IA obtenida para ide={ide}: {ia_message}")
        except RawData.DoesNotExist:
            logger.error(f"No se encontró RawData para ide={ide}")
            ia_message = None
        except Exception as e:
            logger.error(f"Error en IA_GENERATION para ide={ide}: {str(e)}")
            ia_message = None

        return render(request, "delivering/result.html", {
            "ide": ide,
            "result_message": result_message,
            "ia_message": None,
            "verifications": result_data,
            "probabilidad": prob,
            "timestamp": timestamp,
        })