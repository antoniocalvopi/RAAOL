import os
import sys
import django
import json
from django.test import TestCase
from tests.tests_utils import export_test_results 

# Configuración de entorno Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from collection.service import run_collection_pipeline

class CollectionServicesTest(TestCase):
    """
    Tests para el pipeline de scraping definido en `run_collection_pipeline`.
    Carga datos desde un archivo JSON con casos de prueba y valida el contenido devuelto.
    """

    def load_test_data(self):
        """Carga el archivo JSON con las URLs y resultados esperados."""
        test_file_path = os.path.join(os.path.dirname(__file__), 'collection_services.json')
        with open(test_file_path, encoding="utf-8") as f:
            return json.load(f)
    
    def test_collection_pipeline(self):
        test_data = self.load_test_data()
        results = []

        for idx, test in enumerate(test_data, start=1):
            url = test["url"]
            expected_result = test["expected_result"]
            min_length = expected_result.get("min_content_length", 0)
            min_images = expected_result.get("min_images", None)  # opcional

            try:
                html, images = run_collection_pipeline(url)
                html_length = len(html) if html else 0
                num_images = len(images) if images else 0

                passed = html_length > min_length
                if min_images is not None:
                    passed = passed and num_images >= min_images

                results.append({
                    "test": idx,
                    "url": url,
                    "html_length": html_length,
                    "images_count": num_images,
                    "min_length_required": min_length,
                    "min_images_required": min_images,
                    "result": "✅ PASSED" if passed else "❌ FAILED"
                })

                self.assertTrue(html and html_length > min_length,
                                f"HTML demasiado corto para {url}")
                if min_images is not None:
                    self.assertGreaterEqual(num_images, min_images,
                                            f"No se encontraron suficientes imágenes en {url}")

            except Exception as e:
                results.append({
                    "test": idx,
                    "url": url,
                    "error": str(e),
                    "result": "❌ ERROR"
                })
                self.fail(f"Error procesando {url}: {e}")

        # Crear resumen
        total = len(results)
        passed_count = sum(1 for r in results if "PASSED" in r["result"])
        summary = {
            "total_tests": total,
            "passed": passed_count,
            "failed": total - passed_count,
            "success_rate": f"{(passed_count / total) * 100:.2f} %"
        }

        # Exportar resultados incluyendo resumen
        export_test_results("results/collection_results.json", results, summary)

        # Imprimir resumen en consola
        print(f"Total tests: {passed_count}/{total} | {(passed_count / total) * 100:.2f}% completados con éxito")