from django.urls import path
from crawling.views import check_url

""" Endpoint para verificar la compatibilidad de URLs"""
urlpatterns = [
    path('api/crawling/check-url/', check_url.as_view(), name='check-url'),
]