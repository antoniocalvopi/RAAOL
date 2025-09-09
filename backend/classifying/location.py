import requests
import re
import logging
from difflib import SequenceMatcher
from sentence_transformers import SentenceTransformer, util
import numpy as np

logger = logging.getLogger("classifying")


class LOCATION:
    """ Clase para operaciones de geolocalización y verificación contextual.

    Permite realizar geocodificación, geocodificación inversa, obtención de puntos
    de interés (POIs), y verificación de contexto en base a descripciones.
    """

    def __init__(self):
        """ Inicializa la clase con la URL del servicio para verificación contextual.
        """
        self.api_url = "http://localhost:8000/location_context"
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def normalize_string(self, text):
        """ Normaliza una cadena eliminando puntuación y convirtiendo a minúsculas. (uso de regex)

        Args:
            text (str): Texto a normalizar.

        Returns:
            str: Texto limpio y normalizado.
        """
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()

    def string_similarity(self, a, b):
        """ Calcula la similitud entre dos cadenas utilizando SequenceMatcher.

        Args:
            a (str): Primera cadena.
            b (str): Segunda cadena.

        Returns:
            float: Valor de similitud entre 0 y 1.
        """
        a_norm = self.normalize_string(a)
        b_norm = self.normalize_string(b)
        return SequenceMatcher(None, a_norm, b_norm).ratio()

    def points_of_interest(self, lat, lon):
        """ Obtiene puntos de interés cercanos a unas coordenadas mediante Overpass API.

        Args:
            lat (float): Latitud.
            lon (float): Longitud.

        Returns:
            list[dict]: Lista de puntos de interés con nombre y etiquetas.
        """
        overpass_url = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        node(around:5000, {lat}, {lon})[amenity];
        out;
        """
        try:
            response = requests.get(overpass_url, params={'data': query}, timeout=15)
            response.raise_for_status()
            raw = response.json().get('elements', [])
            return [
                {'name': pt['tags'].get('name'), 'tags': pt.get('tags')}
                for pt in raw if pt.get('tags', {}).get('name')
            ]
        except requests.RequestException as e:
            logger.error(f"Overpass API falló: {e}")
        return []

    def compare_with_description_embeddings(self, description, points_of_interest):
        """
        Versión con embeddings: compara la descripción con POIs
        usando similitud coseno en el espacio semántico.
        """
        if not points_of_interest and not description or not isinstance(description, str):
            return {"verified": False, "matches": []}

        # Extraer nombres de POIs (similar a tu código original)
        points_of_interest_list = []
        for point in points_of_interest:
            name = None
            if isinstance(point, dict):
                tags = point.get('tags')
                if isinstance(tags, dict):
                    name = tags.get('name')
                if not name:
                    name = point.get('name')
            if name:
                points_of_interest_list.append(name)

        if not points_of_interest_list:
            return {"verified": False, "matches": []}

        logger.info(f"Puntos de interés a analizar: {points_of_interest_list}")

        # Generar embeddings
        desc_emb = self.embedding_model.encode(description, convert_to_tensor=True)
        pois_emb = self.embedding_model.encode(points_of_interest_list, convert_to_tensor=True)

        # Calcular similitudes coseno
        cos_scores = util.cos_sim(desc_emb, pois_emb)[0]  # vector de similitud con cada POI

        # Umbral para considerar "match" (puedes ajustar este valor)
        threshold = 0.5

        matches = []
        for idx, score in enumerate(cos_scores):
            sim_score = float(score)
            if sim_score >= threshold:
                matches.append({
                    "poi": points_of_interest_list[idx],
                    "similarity": sim_score
                })

        verified = len(matches) > 0

        return {
            "verified": verified,
            "matches": matches
        }


    def compare_with_description(self, description, points_of_interest):
        """ Compara una descripción del anuncio con los puntos de interés cercanos.

        Args:
            description (str): descripción del anuncio.
            points_of_interest (list): lista de POIs con nombres.

        Returns:
            dict|bool: Diccionario con coincidencias o False si falla la solicitud.
        """
        if not points_of_interest:
            return {"verified": False, "matches": []}

        points_of_interest_list = []
        for point in points_of_interest:
            name = None
            if isinstance(point, dict):
                tags = point.get('tags')
                if isinstance(tags, dict):
                    name = tags.get('name')
                if not name:
                    name = point.get('name')
            if name:
                points_of_interest_list.append(name)

        logger.info(f"Puntos de interés a analizar: {points_of_interest_list}")

        if not points_of_interest_list:
            return {"verified": False, "matches": []}

        payload = {
            "description": description,
            "points_of_interest": points_of_interest_list
        }

        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Fallo en verificación contextual: {e}")
            return False

    def geocode(self, address_input):
        """ Realiza geocodificación directa usando Nominatim.

        Args:
            address_input (str): Dirección a buscar.

        Returns:
            dict|None: Resultado de la geocodificación o None si falla.
        """
        search_url = "https://nominatim.openstreetmap.org/search"
        headers = {
            "User-Agent": "OSINT-Checker/1.0 (contact@yourdomain.com)"
        }
        address_input = re.sub(r'\s*,\s*', ', ', address_input.strip())
        params = {
            "q": address_input,
            "format": "json",
            "limit": 1
        }
        logger.info(f"Geocode de ubicación: {address_input}")
        try:
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Output nominatim: {data}")
            if not data or not isinstance(data[0], dict):
                logger.error("Output inválido de la API de Nominatim")
                return None
            return data[0]
        except requests.RequestException as e:
            logger.error(f"Acceso fallido a Nominatim: {e}")
            return None

    def reverse_geocode(self, lat, lon):
        """ Realiza geocodificación inversa usando Nominatim.

        Args:
            lat (float): Latitud.
            lon (float): Longitud.

        Returns:
            tuple[str, float, float]: Dirección obtenida, latitud y longitud.
        """
        url = "https://nominatim.openstreetmap.org/reverse"
        headers = {
            "User-Agent": "OSINT-Checker/1.0 (contact@yourdomain.com)"
        }
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json"
        }
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("display_name", ""), lat, lon
        except requests.RequestException as e:
            logger.error(f"Reverse geocoding falló: {e}")
            return "", None, None

    def location_context(self, lat, lon, place, feature_vector, method="embeddings"):
        """ Evalúa el contexto geográfico en base a descripción y POIs cercanos.

        Args:
            lat (float): Latitud del inmueble.
            lon (float): Longitud del inmueble.
            place (dict): Resultado del geocodificador.
            feature_vector (dict): Diccionario con información del anuncio.
            method (str): String que indica tipo de comparación de contexto (simple- palabra clave; embeddings- embeddings)

        Returns:
            tuple: 
                - context (float): Puntaje por coincidencia contextual.
                - matches (list|None): Coincidencias encontradas con POIs.
                - claimed_city (str): Ciudad obtenida de los datos.
                - address_info (dict): Información de dirección normalizada.
        """
        context = 0
        match = None

        if lat and lon:
            points = self.points_of_interest(lat, lon)
            description = feature_vector.get("description", "")

            if method == "embeddings":
                match = self.compare_with_description_embeddings(description, points[:10])
            else:
                match = self.compare_with_description(description, points[:10])

            if match and match.get("verified"):
                context = 0.2

            logger.info(f"Match encontrado: {match}")

        address_info = place.get("address", {}) if isinstance(place.get("address", {}), dict) else {}
        claimed_city = (
            address_info.get("city")
            or address_info.get("town")
            or address_info.get("village")
            or ""
        )

        return context, match.get("matches", None) if match else None, claimed_city, address_info
    
    def pre_check(self, lat, lon):
        """ Verificación previa de la ubicación, una vez realizada la geolocalización y obtenidas coordenadas, se evalua si forma parte 
        de una zona poblada y/o urbana, en caso negativo nivel de confianza 0 y score = 1, es decir "ubicación fraudulenta".
        
        Args:
            lat (float): Latitud del inmueble.
            lon (float): Longitud del inmueble.
            
        Returns:
            tuple:
                - populated (Boolean): flag con valor True or False, True en caso de constituirse una zona poblada.
                - urban (Boolean): flag con valor True or False, True en caso de constituirse una zona urbana.
        """
        overpass_url = "http://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
        node(around:3000,{lat},{lon})[place~"city|town|village|hamlet"];
        way(around:3000,{lat},{lon})[landuse=residential];
        way(around:3000,{lat},{lon})[building];
        way(around:3000,{lat},{lon})[highway~"residential|primary|secondary|tertiary"];
        ); 
        out center; 
        """
        try:
            response = requests.get(overpass_url, params={'data': query}, timeout=30)
            response.raise_for_status()
            output = response.json().get("elements", [])
            
            populated = any(e.get("tags", {}).get("place") in ["city", "town", "village", "hamlet"] for e in output)
            urban = any(
                e.get("tags", {}).get("landuse") == "residential"
                or e.get("tags", {}).get("building")
                or (e.get("tags", {}).get("highway") in ["residential", "primary", "secondary", "tertiary"])
                for e in output
            )
            
            return populated, urban
        except requests.RequestException as e:
            logger.error(f"Error comprobando zona poblada/urbana: {e}")
            return False, False
            
                