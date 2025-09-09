import os
import logging
from dotenv import load_dotenv
from cleaning.models import RawData as raw_data
from classifying.location import LOCATION
from classifying.image import IMAGE
from classifying.price import PRICE
import re

logger = logging.getLogger("classifying")


class OSINT:
    """ Clase para realizar verificaciones con metodologías OSINT sobre datos inmobiliarios.

    Se encarga de realizar chequeos de precio, imágenes y ubicación a partir 
    de un identificador y su feature_vector asociado.

    Attributes:
        ide (str): Identificador del inmueble o anuncio.
        location (LOCATION): Instancia para operaciones de geocoding.
        image (IMAGE): Instancia para procesamiento de imágenes.
        raw_data (RawData|None): Instancia del modelo RawData asociado al ide.
        feature_vector (dict): Diccionario con características del anuncio.
    """

    def __init__(self, ide: str):
        """ Inicializa la clase cargando datos y configuraciones.

        Args:
            ide (str): Identificador único del anuncio o inmueble.
        """
        self.ide = ide
        self.location = LOCATION()

        load_dotenv('.config')
        self.image = IMAGE(os.getenv("SERPAPI"), os.getenv("AI_MODELS"), self.ide)

        try:
            self.raw_data = raw_data.objects.get(ide=ide)
            self.feature_vector = self.raw_data.feature_vector
        except raw_data.DoesNotExist:
            logger.error(f"[ERROR] No se encontró RawData para ide: {ide}")
            self.raw_data = None
            self.feature_vector = {}

    def extract_location_from_title(self,title, address):
        keywords = [
            r"C\.", r"Av\.", r"Pl\.", r"Pza\.",
            r"calle", r"avenida", r"plaza", r"barrio", r"zona", r"sector",
            r"parque", r"centro", r"ciudad", r"pueblo", r"camino", r"carretera",
            r"urbanización", r"residencial", r"localidad", r"provincia"
        ]

        title_lower = title.lower()
        for kw in keywords:
            # Buscar la palabra clave con el resto hasta el final
            pattern = re.compile(rf'({kw}.*)', re.IGNORECASE)
            match = pattern.search(title)
            if match:
                extracted = match.group(1)
                # Eliminar números
                extracted = re.sub(r'\d+', '', extracted).strip()
                combined = f"{extracted}, {address}".strip(", ")
                return combined

        return None

    def PriceCheck(self):
        """ Realiza la verificación del precio utilizando la clase PRICE.

        Returns:
            dict|None: Resultado del chequeo de precio o None si falla.
        """
        if not self.feature_vector:
            logger.error("feature_vector no es válido")
            return None

        logger.info("Realizando verificación del precio")
        price = PRICE(self.feature_vector, self.ide)
        result = price.check_consistency()
    
        return result

    def ImageCheck(self):
        """ Realiza comprobaciones basadas en imágenes del anuncio.

        Returns:
            dict|None: Resultado del procesamiento de imágenes o None si falla.
        """
        if not self.feature_vector:
            logger.error("feature_vector no es válido")
            return None

        images_urls = self.feature_vector.get("images", [])
        if not images_urls:
            logger.error("No se proporcionaron URLs de imágenes")
            return None

        logger.info("Realizando comprobaciones con imágenes")
        result = self.image.process_images([images_urls[0]])

        return result

    def LocationCheck(self):
        """ Realiza verificaciones de ubicación mediante geocoding, reverse geocoding y puntos de interés (POIs).

        Returns:
            dict|None: Diccionario con información y puntuaciones de ubicación,
                       o None si no se puede realizar la verificación.
        """
        if not self.feature_vector:
            logger.error("feature_vector no es válido")
            return None
        
        address_input = self.feature_vector.get("address", "")
        title = self.feature_vector.get("title", "")
        logger.info(f"titulo del anuncio: {title}")

        # Análisis con título + dirección si título existe
        combined_input = self.extract_location_from_title(title, address_input)
        if combined_input is not None:
            logger.info(f"titulo combinado con address: {combined_input}")
            return self.analyze_location(combined_input)
        else:
            return self.analyze_location(address_input)

        
    def analyze_location(self, input_address):
        populated_score = 0
        urban_score = 0
        # Geocode
        place = self.location.geocode(input_address)
        if not place:
            return None  # o resultado con score 0
        
        lat = float(place.get("lat", 0))
        lon = float(place.get("lon", 0))

        populated, urban = self.location.pre_check(lat, lon)
        if not populated or not urban:
            return {
                "claimed_address": input_address,
                "confidence_level": 0,
                "location_match_score": 0,
                "penalization_reason": "Unpopulated or non-urban area",
            }
        else:
            if populated:
                populated_score = 0.15
            if urban:
                urban_score = 0.15
        parsed_address = place.get("display_name", "")
        reverse_address, _, _ = self.location.reverse_geocode(lat, lon)

        context, matches, claimed_city, address_info = self.location.location_context(
            lat, lon, place, self.feature_vector
        )

        sim_score = self.location.string_similarity(input_address, parsed_address)
        loc_score = 0.4 if place else 0

        final_score = round(loc_score + sim_score * 0.1 +  populated_score + urban_score + context, 4)
        logger.info(
            f"Cálculo de final_score:\n"
            f"  loc_score: {loc_score}\n"
            f"  sim_score (input vs parsed): {sim_score} * 0.1 = {sim_score * 0.1}\n"
            f"  populated_score: {populated_score} * 0.15 = {populated_score * 0.15}\n"
            f"  urban_score: {urban_score} * 0.15 = {urban_score * 0.15}\n"
            f"  context: {context}\n"
            f"  final_score (redondeado): {final_score}"
        )

        confidence = int(final_score * 5)

        return {
            "claimed_addres": input_address,
            "claimed_city": claimed_city,
            "claimed_postal_code": address_info.get("postcode"),
            "claimed_neighborhood": address_info.get("neighbourhood"),
            "parsed_address": parsed_address,
            "latitude": lat,
            "longitude": lon,
            "geocode_source": place,
            "reverse_geocode_address": reverse_address,
            "matches": matches,
            "location_match_score": round(1 - final_score, 2),
            "confidence_level": confidence,
        }