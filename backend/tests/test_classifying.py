import os
import sys
import django
import unittest
import json
from tests.tests_utils import export_test_results

# Agregar la carpeta raíz del proyecto al path para que Python pueda encontrar `backend`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from classifying.location import LOCATION

class TestLocationContext(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.loc = LOCATION()
        cls.lat, cls.lon = 40.4255, -3.7074
        cls.place = {"address": {"city": "Madrid", "suburb": "Malasaña"}}
        cls.feature_vector = {
            "description": (
                "Piso ubicado en Malasaña, a pocos metros de la Plaza del Dos de Mayo "
                "y cerca del famoso Café Central. Zona cultural y muy activa con teatros y museos."
            ),
            "address": "Malasaña, Madrid"
        }
        cls.results = []

    def test_location_context_simple(self):
        try:
            ctx_simple = self.loc.location_context(
                self.lat, self.lon, self.place, self.feature_vector, method="simple"
            )
            print("Método simple:", ctx_simple)
            self.results.append({
                "method": "simple",
                "result": ctx_simple,
                "status": "PASSED"
            })
            self.assertIsNotNone(ctx_simple)
        except AssertionError as e:
            self.results.append({
                "method": "simple",
                "result": None,
                "status": "FAILED",
                "error": str(e)
            })
            raise

    def test_location_context_embeddings(self):
        try:
            ctx_embed = self.loc.location_context(
                self.lat, self.lon, self.place, self.feature_vector, method="embeddings"
            )
            print("Método embeddings:", ctx_embed)
            self.results.append({
                "method": "embeddings",
                "result": ctx_embed,
                "status": "PASSED"
            })
            self.assertIsNotNone(ctx_embed)
        except AssertionError as e:
            self.results.append({
                "method": "embeddings",
                "result": None,
                "status": "FAILED",
                "error": str(e)
            })
            raise

    @classmethod
    def tearDownClass(cls):
        summary = {
            "total": len(cls.results),
            "passed": sum(1 for r in cls.results if r["status"] == "PASSED"),
            "success_rate": (sum(1 for r in cls.results if r["status"] == "PASSED") / len(cls.results)) * 100
        }
        export_test_results("results/classifying_results.json", cls.results, summary)


if __name__ == '__main__':
    unittest.main()