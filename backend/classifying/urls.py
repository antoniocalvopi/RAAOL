from django.urls import path
from .views import ClassifyByIDView

""" Exposición de endpoint para interactuar con el módulo de clasificación (microbackend OSINT) """
urlpatterns = [
    path('api/classify/<str:ide>/', ClassifyByIDView.as_view(), name='classify_by_id'),
]