from django.urls import path
from collection.views import scrape_view

""" Exposición de endpoint para interactuar con el scraper """
urlpatterns = [
    path('api/collection/scrape/', scrape_view.as_view(), name='scrape-web'),
]