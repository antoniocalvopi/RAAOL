import os
import sys
import django
import json
from django.test import TestCase
from tests.tests_utils import export_test_results

# Agregar la carpeta raíz al path para que Python pueda encontrar `backend`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from collection.service import run_collection_pipeline
from cleaning.services import run_cleaning_pipeline_from_html

class CleaningIntegratedTest(TestCase):
    def load_test_data(self):
        test_file_path = os.path.join(os.path.dirname(__file__), 'cleaning_services.json')
        with open(test_file_path, encoding="utf-8") as f:
            return json.load(f)

    def string_parser(self, text):
        if isinstance(text, str):
            return text.replace('\xa0','').strip()
        return text

    def test_cleaning_pipeline_with_scraping(self):
        test_data = self.load_test_data()
        total = 0
        passed = 0
        results = []

        for idx, test in enumerate(test_data, start=1):
            url = test["url"]
            clases_objetivo = test["clases_objetivo"]
            expected_vector = test["expected_vector"]

            print(f"Scrapeando URL: {url}")
            html, images = run_collection_pipeline(url)
            result = run_cleaning_pipeline_from_html(html, clases_objetivo, images)
            feature_vector = result.feature_vector

            all_match = True
            mismatches = {}
            errors = []

            for key, expected_value in expected_vector.items():
                actual_value = self.string_parser(feature_vector.get(key))
                if actual_value != expected_value:
                    all_match = False
                    mismatches[key] = {"expected": expected_value, "actual": actual_value}
                    # Guardamos el error en vez de lanzar excepción
                    errors.append(f"Field '{key}': expected '{expected_value}', got '{actual_value}'")

            result_msg = "✅ PASSED" if all_match else "❌ FAILED"
            if all_match:
                passed += 1

            results.append({
                "test": idx,
                "url": url,
                "result": result_msg,
                "mismatches": mismatches if mismatches else None,
                "errors": errors if errors else None,
                "feature_vector": feature_vector
            })

            print(f"test{idx:02d} - {result_msg}")
            total += 1

        # Exportar resultados aunque haya fallos
        summary = {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed / total) * 100
        }
        export_test_results("results/cleaning_results.json", results, summary)

        if passed < total:
            self.fail(f"Fallaron {total - passed} tests. Ver 'results/cleaning_results.json' para detalles.")
