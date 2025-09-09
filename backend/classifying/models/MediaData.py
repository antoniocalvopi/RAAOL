from django.db import models
from django.contrib.postgres.fields import ArrayField

class MediaData(models.Model):
    """ Modelo que representa datos de análisis y verificación sobre la o las imagen."""
    ide = models.CharField(max_length=30, unique=True)
    image_url = models.URLField(max_length=2048)
    image_data = models.BinaryField(null=True, blank=True)

    # Metadatos EXIF extraídos, puede incluir GPS, fecha, cámara, etc.
    exif_data = models.JSONField(null=True, blank=True)
    extracted_location = models.CharField(max_length=147, null=True, blank=True)

    # Datos de búsqueda inversa de imagen
    reverse_search_count = models.PositiveIntegerField(default=0)
    reverse_search_sources = ArrayField(
        models.URLField(max_length=2048), default=list, blank=True
    )

    # Análisis visual
    visual_notes = ArrayField(
        models.CharField(max_length=280), default=list, blank=True
    )
    visual_match = models.BooleanField(null=True)
    verification_score = models.FloatField(null=True)
    manipulation_detected = models.BooleanField(null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"MediaData {self.ide} - Score: {self.verification_score}"