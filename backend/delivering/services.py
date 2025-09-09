import requests
import logging

class IA_GENERATION:
    """ Clase para interactuar con el servicio de generación e interpretación con IA."""

    def __init__(self):
        """ Inicializa la instancia con la URL del servicio desplegado."""
        self.api_url = "http://localhost:8000/interpretation"
        self.logger = logging.getLogger("delivering")
        
    def run(self, verifications, features):
        """ Envía datos al endpoint de IA generativa generalista y obtiene la interpretación.

        Args:
            verifications (dict): Diccionario con datos de verificación.
            features (dict): Diccionario con características para interpretar.

        Returns:
            dict: Resultado del servicio IA o un dict con clave 'error' si hubo fallo.
        """
        payload = {
            "verifications": verifications,
            "features": features
        }
                
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}