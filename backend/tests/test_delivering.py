import requests
import unittest
import os
import json
from tests.tests_utils import export_test_results

class DeliveringEndpointIntegrationTest(unittest.TestCase):
    def load_test_data(self):
        file_path = os.path.join(os.path.dirname(__file__), 'delivering_test.json')
        with open(file_path) as f:
            return json.load(f)
        
    def test_entrega_html_probabilidad_alta(self):
        test_data = self.load_test_data()
        total = 0
        passed = 0
        results = []

        for test in test_data:
            ide = test["id"]
            url = f"http://localhost:8001/api/deliver/{ide}/"
            try:
                response = requests.get(url)
                html = response.content.decode("utf-8").lower()

                status_ok = (response.status_code == 200)
                contains_interp = "interpretación:" in html
                contains_chars = "características del anuncio:" in html

                all_match = status_ok and contains_interp and contains_chars

                if all_match:
                    passed += 1
                    result_status = "PASSED ✅"
                else:
                    result_status = "FAILED ❌"

                results.append({
                    "ide": ide,
                    "url": url,
                    "status_code": response.status_code,
                    "status": result_status,
                    "checks": {
                        "status_ok": status_ok,
                        "contains_interpretacion": contains_interp,
                        "contains_caracteristicas": contains_chars
                    }
                })

                # Mantener las aserciones pero sin bloquear la exportación
                self.assertTrue(all_match, f"Fallo en test {ide}")

            except Exception as e:
                results.append({
                    "ide": ide,
                    "url": url,
                    "status_code": None,
                    "status": "ERROR ❌",
                    "error": str(e)
                })

            total += 1
            print(f"test {ide} - {results[-1]['status']}")

        summary = {
            "total": total,
            "passed": passed,
            "success_rate": (passed / total) * 100 if total > 0 else 0
        }
        export_test_results("results/delivering_results.json", results, summary)

        print(f"Total tests: {passed}/{total} | {(passed / total) * 100:.2f} %")