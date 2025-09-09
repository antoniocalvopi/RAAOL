from django.db import models

class LocationData(models.Model):
    """ Modelo que almacena información geográfica y contextual sobre la ubicació verificada de un anuncio.
    
    Atributos:
        ide (str): Identificador único asociado a la entrada.
        
        claimed_addres (str): Dirección reclamada por la fuente original.
        claimed_neighborhood (str): Barrio o zona obtenida tras análisis.
        claimed_city (str): Ciudad  obtenida tras análisis.
        claimed_postal_code (str): Código postal  obtenida tras análisis.
        
        parsed_address (str): Dirección interpretada por el geocodificador (OSM/Nominatim).
        latitude (float): Latitud obtenida tras geocodificación directa.
        longitude (float): Longitud obtenida tras geocodificación directa.
        geocode_source (dict): Respuesta JSON completa del geocodificador directo.

        reverse_geocode_address (str): Dirección obtenida mediante geocodificación inversa.

        matches (list): Lista de coincidencias encontradas en puntos de interés (POIs) cercanos 
                        al punto geográfico.

        location_match_score (float): Puntuación general de coincidencia de la ubicación 
                                      (0.0 a 1.0).
        confidence_level (int): Nivel de confianza en la veracidad de la ubicación (1 a 5).
    """
    
    ide = models.CharField(max_length=30, unique=True)

    # Datos reclamados en origen
    claimed_addres = models.CharField(max_length=147)  # obligatorio
    claimed_neighborhood = models.CharField(max_length=176, null=True, blank=True)
    claimed_city = models.CharField(max_length=96, null=True, blank=True)
    claimed_postal_code = models.CharField(max_length=8, null=True, blank=True)

    # Resultados de geocodificación directa
    parsed_address = models.CharField(max_length=300)  # obligatorio
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    geocode_source = models.JSONField(null=True, blank=True)

    # Resultados de geocodificación inversa
    reverse_geocode_address = models.CharField(max_length=300, null=True, blank=True)

    # Verificación contextual basada en POIs
    matches = models.JSONField(null=True)

    # Puntaje y nivel de confianza
    location_match_score = models.FloatField()  # obligatorio
    confidence_level = models.IntegerField()  # obligatorio (1 a 5)