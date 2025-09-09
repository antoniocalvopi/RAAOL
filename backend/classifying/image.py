from sqlite3 import IntegrityError
import requests
import logging
from serpapi import GoogleSearch
from classifying.models import MediaData
from statistics import median

logger = logging.getLogger("classifying")


class IMAGE:
    """ Clase para procesamiento, análisis y verificación de imágenes usando múltiples fuentes.

    Métodos disponibles:
        - describe_image: Genera descripción automática de una imagen.
        - compare_image_to_text: Evalúa la similitud entre una imagen y un texto.
        - reverse_image_search: Realiza una búsqueda inversa de imagen (Yandex).
        - get_first_match_url: Extrae la URL de la imagen más parecida de la búsqueda inversa.
        - ia_image_detection: Detecta si una imagen ha sido generada por IA.
        - process_images: Proceso completo para una lista de imágenes.
    """

    def __init__(self, api_key: str, API: str, ide:str):
        """ Inicializa la clase con la clave de SerpAPI y la URL base del servicio de análisis.

        Args:
            api_key (str): Clave de API de SerpAPI.
            API (str): URL base para los servicios de análisis de imágenes.
        """
        self.serpapi_key = api_key
        self.BASE_URL = API
        self.ide = ide

    def describe_image(self, img_url):
        """ Obtiene una descripción automática para una imagen.

        Args:
            img_url (str): URL de la imagen.

        Returns:
            str|None: Descripción generada o None si falla.
        """
        endpoint = f"{self.BASE_URL}/describe_image"
        params = {"img_url": img_url}
        response = requests.get(endpoint, params=params)
        if response.ok:
            return response.json().get("description")
        else:
            logger.error(f"Falló descripción: {response.status_code}")
            return None

    def compare_image_to_text(self, image_url, text):
        """ Compara una imagen contra un texto para medir similitud semántica.

        Args:
            image_url (str): URL de la imagen.
            text (str): Texto para comparar.

        Returns:
            dict|None: Resultado con similitud o None si falla.
        """
        endpoint = f"{self.BASE_URL}/compare_image_to_text"
        params = {"image": image_url, "caption": text}
        response = requests.get(endpoint, params=params)
        if response.ok:
            return response.json()
        else:
            logger.error(f"Falló comparación imagen vs texto: {response.status_code}")
            return None

    def reverse_image_search(self, image_url: str):
        """ Realiza una búsqueda inversa de imagen usando Yandex a través de SerpAPI.

        Args:
            image_url (str): URL de la imagen.

        Returns:
            dict|None: Resultado de la búsqueda o None si falla.
        """
        params = {
            "engine": "yandex_images",
            "url": image_url,
            "api_key": self.serpapi_key
        }

        try:
            search = GoogleSearch(params)
            return search.get_dict()
        except Exception as e:
            logger.error(f"Reverse image search falló para {image_url}: {e}")
            return None

    def get_first_match_url(self, reverse_search_result):
        """ Obtiene la URL de la primera imagen similar encontrada.

        Args:
            reverse_search_result (dict): Resultado completo de la búsqueda inversa.

        Returns:
            str|None: URL de la imagen similar o None si no hay coincidencias.
        """
        try:
            images_results = reverse_search_result.get("image_results", [])
            if images_results:
                return images_results[0].get("original_image", {}).get("link")
        except Exception as e:
            logger.warning(f"Error extrayendo primera imagen: {e}")
        return None

    def ia_image_detection(self, image_url):
        """ Detecta si una imagen ha sido generada mediante inteligencia artificial.

        Args:
            image_url (str): URL de la imagen.

        Returns:
            dict|None: Resultado del análisis o None si falla.
        """
        endpoint = f"{self.BASE_URL}/ia_detection"
        params = {"image": image_url}
        response = requests.get(endpoint, params=params)
        if response.ok:
            return response.json()
        else:
            logger.error(f"Falló detección de IA en imagen: {response.status_code}")
            return None

    def filter_yandex_results(self, reverse_search_result, allowed_domains):
        """Filtra resultados de Yandex según dominios permitidos."""
        filtered = []
        try:
            for res in reverse_search_result.get("image_results", []):
                link = res.get("original_image", {}).get("link")
                if link and any(domain in link for domain in allowed_domains):
                    filtered.append(link)
        except Exception as e:
            logger.warning(f"Error filtrando resultados Yandex: {e}")
        return filtered


    def process_images(self, image_urls):
        """ Procesa un conjunto de imágenes para verificación mediante múltiples técnicas.

        Args:
            image_urls (list[str]): Lista de URLs de imágenes.

        Returns:
            list[dict]: Resultados del análisis por cada imagen procesada.
        """
        allowed_domains = ["idealista.com", "fotocasa.es", "pisos.com", "milanuncios.com"]
        results = []
        data = {}
        originals = []
        similars = []
        descriptions = []
        scores = []
        ia_flags = []

        for url in image_urls:
            logger.info(f"Procesando imagen: {url}")
            
            # Detección IA
            ia_generated = self.ia_image_detection(url)
            if ia_generated and ia_generated.get("is_ai", False):
                logger.info(f"Imagen detectada como IA: {url}")
                originals.append(url)
                similars.append(None)
                scores.append(1)
                descriptions.append(None)
                ia_flags.append(ia_generated)
            else:
                reverse_result = self.reverse_image_search(url)
                original_description = self.describe_image(url)
                logger.info(f"Descripción original: {original_description}")

                # Filtrar resultados por dominio
                filtered_urls = self.filter_yandex_results(reverse_result, allowed_domains)

                if not filtered_urls:
                    logger.warning(f"No se encontraron imágenes similares válidas para {url}")
                    originals.append(url)
                    similars.append(None)
                    descriptions.append(original_description)
                    ia_flags.append(False)
                    scores.append(0)
                    continue

                # Comparar con todas las similares filtradas
                similarities = []
                for match_url in filtered_urls:
                    comparison = self.compare_image_to_text(match_url, original_description)
                    score = comparison.get("similarity") if comparison else 0
                    similarities.append(score)

                if similarities:
                    max_score = max(similarities)
                    max_index = similarities.index(max_score)
                    max_url = filtered_urls[max_index]
                else:
                    max_score = 0
                    max_url = None

                originals.append(url)
                similars.append(max_url)
                scores.append(max_score)
                descriptions.append(original_description)
                ia_flags.append(ia_generated)

        results = {
            "image_url": tuple(originals),
            "auto_description": tuple(descriptions),
            "similar_image": tuple(similars),
            "similarity_score":  round(max(scores), 4) if scores else 0, 
            "ia_generated": round(sum(ia_flags) / len(ia_flags), 4) if ia_flags else 0
        }
        
        # Datos para guardar en DB
        data = {
            "image_url": tuple(originals),
            "image_data": None,
            "exif_data": None,
            "extracted_location": None,
            "reverse_search_count": sum(
                len(self.filter_yandex_results(self.reverse_image_search(url), allowed_domains))
                for url in originals
            ),
            "reverse_search_sources": [self.filter_yandex_results(self.reverse_image_search(url), allowed_domains) for url in originals],
            "visual_notes": tuple(descriptions),
            "visual_match": True,
            "verification_score": scores,
            "manipulation_detected": any(bool(x and x.get("is_ai", False)) for x in ia_flags),
        }

        # self.save_media_data(data, self.ide)
        return results
    
    def save_media_data(self, data, ide):
        """ Guarda o actualiza un objeto MediaData en la base de datos.

        Args:
            data (dict): Diccionario con claves compatibles con MediaData.

        Returns:
            MediaData|None: instancia guardada o None si hubo error.
        """
        try:
            MediaData.objects.update_or_create(
                ide=ide,
                defaults={
                    "image_url": data.get("image_url"),
                    "image_data": data.get("image_data"),
                    "exif_data": data.get("exif_data"),
                    "extracted_location": data.get("extracted_location"),
                    "reverse_search_count": data.get("reverse_search_count", 0),
                    "reverse_search_sources": data.get("reverse_search_sources", []),
                    "visual_notes": data.get("visual_notes", []),
                    "visual_match": data.get("visual_match"),
                    "verification_score": data.get("verification_score"),
                    "manipulation_detected": data.get("manipulation_detected"),
                }
            )
        except IntegrityError as e:
            logger.error(f"Fallo integridad MediaData ({data.get('ide')}): {e}")
        except Exception as e:
            logger.error(f"Excepción al guardar MediaData ({data.get('ide')}): {e}")
        return None