import os
import sys
import django
import json
from django.test import TestCase
from tests.tests_utils import export_test_results

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from crawling.services import crawling_check

class CrawlingServicesTest(TestCase):
    def load_test_data(self):
        test_file_path = os.path.join(os.path.dirname(__file__), 'crawling_services.json')
        with open(test_file_path) as f:
            return json.load(f)
    
    def test_crawling_check(self):
        test_data = self.load_test_data()
        total = 0
        passed = 0
        results_export = []

        for idx, test in enumerate(test_data, start=1):
            url = test["url"]
            expected_result = test["expected_result"]

            plat, val, conexion_ok, plataforma = crawling_check(url)
            passed_test = (
                plat == expected_result["plat"] and
                val == expected_result["val"] and
                conexion_ok == expected_result["conexion_ok"]
            )

            result = "passed ✅" if passed_test else "failed ❌"
            if passed_test:
                passed += 1

            print(f"test{idx:02d} - {result} (URL: {url})")

            results_export.append({
                "test_id": idx,
                "url": url,
                "expected": expected_result,
                "obtained": {
                    "plat": plat,
                    "val": val,
                    "conexion_ok": conexion_ok,
                    "plataforma": plataforma
                },
                "status": result
            })

            self.assertEqual(plat, expected_result["plat"])
            self.assertEqual(val, expected_result["val"])
            self.assertEqual(conexion_ok, expected_result["conexion_ok"])
            total += 1

        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": f"{(passed / total) * 100:.2f} %"
        }

        print(f"Total test: {passed}/{total} | {summary['success_rate']}")

        export_test_results("results/crawling_results.json", results_export, summary)


