import os
import json

def export_test_results(filename, test_results, summary):
    """
    Exporta resultados de tests a un archivo JSON.

    Args:
        filename (str): Nombre del archivo de salida (sin ruta).
        test_results (list[dict]): Lista con los resultados detallados de cada test.
        summary (dict): Resumen con totales y porcentaje de éxito.
    """
    output_path = os.path.join(os.path.dirname(__file__), filename)
    data = {
        "summary": summary,
        "details": test_results
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"[INFO] Resultados exportados a: {output_path}")
