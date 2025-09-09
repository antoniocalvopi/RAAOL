from django.urls import path
from delivering.views import DeliverResultView

""" Exposición de endpoint para interactuar con el módulo de Delivering (microbackend Deliver) """
urlpatterns = [
    path("api/deliver/<str:ide>/", DeliverResultView.as_view(), name="deliver_result"),
]