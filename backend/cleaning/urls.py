from django.urls import path
from cleaning.views import cleaning_pip

""" Exposición de endpoint para interactuar con el módulo de limpieza (microbackend) """
urlpatterns = [
    path('api/cleaning/clean/', cleaning_pip.as_view(), name='cleaning')
]