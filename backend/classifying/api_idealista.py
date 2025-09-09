import os
import requests
import statistics
import logging
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv('.config')


class IdealistaAPI:
    """ Clase para interactuar con la API de Idealista que permite obtener datos de alquileres.

    Métodos:
        get_oauth_token: Obtiene token de autenticación OAuth2.
        estimar_precio_m2_idealista: Estima precio medio y mediano por m².
        realizar_peticion_idealista: Lógica principal pública para acceder al precio.
    """

    def __init__(self):
        """ Inicializa el cliente de Idealista con claves desde entorno."""
        self.logger = logging.getLogger('classifying')
        self.API_KEY = os.getenv("IDE_API_KEY")
        self.API_SECRET = os.getenv("IDE_SECRET")
        self.precio_idealista_m2 = None

    def get_oauth_token(self):
        """ Solicita un token OAuth para autenticar las futuras peticiones a la API de Idealista.

        Returns:
            str | None: Token si la solicitud fue exitosa, None en caso de error.
        """
        url = "https://api.idealista.com/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        data = {
            "grant_type": "client_credentials"
        }

        response = requests.post(
            url, headers=headers, data=data, auth=HTTPBasicAuth(self.API_KEY, self.API_SECRET)
        )

        if response.status_code == 200:
            token_info = response.json()
            self.logger.info("Token OAuth obtenido correctamente.")
            return token_info['access_token']
        else:
            self.logger.error(f"Error al obtener token: {response.status_code} - {response.text}")
            return None

    def estimar_precio_m2_idealista(self, lat, lon, distancia=1500):
        """ Estima el precio de alquiler por m² en base a propiedades cercanas a la ubicación dada.

        Args:
            lat (float): Latitud del punto de búsqueda.
            lon (float): Longitud del punto de búsqueda.
            distancia (int, optional): Radio de búsqueda en metros. Default es 1500.

        Returns:
            dict | None: Resultados de precios o None si la API falla o no hay datos válidos.
        """
        token = self.get_oauth_token()
        if not token:
            return None

        self.logger.info("Realizando solicitud a la API de Idealista.")

        url = "https://api.idealista.com/3.5/es/search"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        data = {
            "center": f"{lat},{lon}",
            "distance": str(distancia),
            "propertyType": "homes",
            "operation": "rent",
            "maxItems": "5",
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            propiedades = response.json().get("elementList", [])
            precios_m2 = []

            for p in propiedades:
                size = p.get("size", 0)
                precio = p.get("price", 0)
                if precio and size > 0:
                    precios_m2.append(precio / size)

            if precios_m2:
                media = statistics.mean(precios_m2)
                mediana = statistics.median(precios_m2)
                self.precio_idealista_m2 = media
                self.logger.info(
                    f"Precio Idealista (alquiler) - Media: {media:.2f} €/m², Mediana: {mediana:.2f} €/m² "
                    f"(basado en {len(precios_m2)} propiedades)."
                )
                return {
                    "precio_m2_medio": round(media, 2),
                    "precio_m2_mediana": round(mediana, 2),
                    "num_propiedades": len(precios_m2)
                }
            else:
                self.logger.warning("No se encontraron propiedades válidas en Idealista.")
                return None

        elif response.status_code == 429:
            self.logger.warning("Límite de peticiones a la API alcanzado (HTTP 429).")
            return None
        else:
            self.logger.error(f"Error en búsqueda: {response.status_code} - {response.text}")
            return None

    def realizar_peticion_idealista(self, lat, lon):
        """ Ejecuta el proceso de consulta de precio de alquiler por m².

        Args:
            lat (float): Latitud.
            lon (float): Longitud.

        Returns:
            float | None: Precio mediano por metro cuadrado o None si no se pudo obtener.
        """
        resultado = self.estimar_precio_m2_idealista(lat, lon)
        if resultado:
            self.logger.info(f"Consulta Idealista completada. Precio medio m²: {resultado['precio_m2_mediana']} €")
        else:
            self.logger.warning("Consulta Idealista fallida o sin resultados.")
        return resultado.get("precio_m2_mediana", None) if resultado else None