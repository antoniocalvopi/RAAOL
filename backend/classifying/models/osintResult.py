from django.db import models

class osintResult(models.Model):
    """ Modelo que almacena los resultados del análisis OSINT (Open Source Intelligence).

    Atributos:
        ide (str): Identificador único del anuncio analizado.

        fraud_prob (float): Probabilidad total estimada de fraude, combinando todas las fuentes.
        location_prob (float): Probabilidad de inconsistencia en la ubicación reportada.
        image_prob (float): Probabilidad de alteración o manipulación en la imagen.
        price_prob (float): Probabilidad de incoherencia en el precio respecto al mercado.

        price_flag (str): Indicador textual (opcional) que describe la anomalía de precio detectada.

        confidence_level (int): Nivel de confianza global (1 a 5), siendo 5 el más confiable.

        timestamp (datetime): Fecha y hora en que se generó el resultado.
    """
    # from raw data
    ide = models.CharField(max_length=30, unique=True)
    
    # from osint pipeline backend
    fraud_prob = models.FloatField(default=0.0)
    location_prob = models.FloatField(default=0.0)
    image_prob = models.FloatField(default=0.0)
    price_prob = models.FloatField(default=0.0)
    price_flag = models.CharField(null=True)
    confidence_level = models.IntegerField(null=False,default=5)
    timestamp = models.DateTimeField(auto_now_add=True)