from django.db import models

class PriceData(models.Model):
    """ Modelo que almacena información relacionada con la evaluación de precios 
    para verificar la veracidad de anuncios de inmuebles.
    
    Atributos:
        ide (str): Identificador único de la entrada analizada.
        reported_price (float): Precio que fue declarado por el usuario o en el anuncio.
        estimated_price_m2 (float): Estimación promedio del precio por m² en la zona.
        estimated_price_m2_median (float): Mediana del precio por m² estimado.
        surface_m2 (float): Superficie del inmueble en metros cuadrados.
        price_per_m2 (float): Precio declarado dividido por los m².
        price_flag (str): Indicador textual de anomalía (ej. 'muy barato', 'muy caro').
        price_prob (float): Probabilidad de inconsistencia basada en el modelo de predicción.
        updated_at (datetime): Fecha de última actualización.
    """

    ide = models.CharField(max_length=30, unique=True)

    reported_price = models.FloatField()  # Precio declarado en el anuncio
    surface_m2 = models.FloatField(null=True, blank=True)  # Tamaño del inmueble en m²
    price_per_m2 = models.FloatField(null=True, blank=True)  # Precio/m² declarado

    estimated_price_m2 = models.FloatField(null=True, blank=True)  # Media del precio/m² idealista
    estimated_price_m2_median = models.FloatField(null=True, blank=True)  # Mediana

    price_flag = models.CharField(max_length=64, null=True, blank=True)  # Bandera textual (alerta)
    price_prob = models.FloatField(default=0.0)  # Probabilidad de fraude por precio

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PriceData {self.ide} - Precio declarado: {self.reported_price} €"
