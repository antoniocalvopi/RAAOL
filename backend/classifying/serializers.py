from rest_framework import serializers
from .models import osintResult, LocationData

class ClassificationResultSerializer(serializers.ModelSerializer):
    """ Serializador para el modelo `osintResult`.

    Este serializador se encarga de representar todos los campos del modelo 
    `osintResult`, el cual contiene los resultados generados a partir de procesos 
    de clasificación OSINT.

    Atributos:
        Meta (class): Clase interna que define el modelo y los campos a serializar.
    """
    class Meta:
        model = osintResult
        fields = '__all__'
        
class LocationDataSerializer(serializers.ModelSerializer):
    """ Serializador para el modelo `LocationData`.

    Permite la serialización de datos relacionados con la ubicación, incluyendo 
    dirección reclamada, coordenadas geográficas, fuente de geolocalización, y nivel 
    de confianza.

    Atributos:
        Meta (class): Clase interna que especifica el modelo y los campos incluidos.
    """
    class Meta:
        model = LocationData
        fields = [
            'id',
            'ide',
            'claimed_addres',
            'claimed_neighborhood',
            'claimed_city',
            'claimed_postal_code',
            'parsed_address',
            'latitude',
            'longitude',
            'geocode_source',
            'reverse_geocode_address',
            'location_match_score',
            'confidence_level',
        ]