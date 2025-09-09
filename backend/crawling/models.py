from django.db import models

class Portales(models.Model):
    """ Modelo que representa plataformas admitidas para el sistema de crawling.

    Cada objeto almacena información sobre una plataforma específica, incluyendo
    su nombre, URL base, patrón de URL y selectores CSS para extracción de datos.
    """
    name = models.CharField(max_length=255)  # nombre de la plataforma
    base_url = models.URLField()  # URL base de la plataforma
    url_pattern = models.CharField(max_length=255)  # patrón URL
    selectors = models.JSONField(null=True, blank=True) # selectores

    class Meta:
        db_table = 'portales'

    def __str__(self):
        return self.name
