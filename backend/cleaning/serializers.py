from rest_framework import serializers
from .models import RawData as raw_data


class CleaningResultSerializer(serializers.ModelSerializer):
    """ Serializer para representar los resultados del proceso de limpieza HTML.

    Serializa instancias del modelo RawData, incluyendo el HTML limpio, los
    vectores de características extraídos y la fecha de creación.
    """

    class Meta:
        """ Configuración del serializer.

        Attributes:
            model: El modelo al que se asocia este serializer (RawData).
            fields: Lista de campos que serán incluidos en la serialización.
        """
        model = raw_data
        fields = ['ide', 'cleaned_html', 'feature_vector', 'timestamp']