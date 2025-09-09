from django.db import models
from django.utils.timezone import now

def generate_ide():
    """ Genera un identificador único basado en la fecha y hora actual.

    Returns:
        str: Identificador con formato 'YYYYMMDD_HHMMSS' (consultar regex en la wiki del repo).
    """
    return now().strftime("%Y%m%d_%H%M%S")


class RawData(models.Model):
    """ Modelo que representa datos HTML procesados y sus características extraídas.

    Atributos:
        ide (CharField): Identificador único generado por fecha/hora.
        cleaned_html (TextField): HTML limpio sin scripts, estilos ni comentarios.
        feature_vector (JSONField): Diccionario con los datos extraídos del HTML.
        timestamp (DateTimeField): Fecha y hora de creación del registro.
    """
    ide = models.CharField(max_length=20, unique=True, default=generate_ide)
    cleaned_html = models.TextField()
    feature_vector = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """ Retorna una representación legible del objeto (su identificador)."""
        return self.ide