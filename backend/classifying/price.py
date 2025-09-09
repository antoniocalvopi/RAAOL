import logging
import requests
from backend.services import _error_response
from classifying.models import PriceData
from classifying.models import LocationData

logger = logging.getLogger("classifying")

class PRICE:
    def __init__(self, feature_vector: dict, ide):
        self.ide = ide
        self.price = self._clean_number(feature_vector.get("price"))
        self.meters = self._clean_number(feature_vector.get("meters"))
        self.bedrooms = feature_vector.get("bedrooms", 0)
        self.province, self.comunity = self._extract_location_data()

        self.predicted_price_m2 = None
        self.predicted_price_real = None
        self.predicted_penalty = None
        self.predicted_suspicious = None
    
    def _extract_location_data(self):
        """Obtiene provincia y comunidad desde LocationData.parsed_address."""
        try:
            location = LocationData.objects.first()
            if not location or not location.parsed_address:
                return None, None
            
            parts = [p.strip() for p in location.parsed_address.split(",")]
            # Ejemplo: [..., 'Badajoz', 'Extremadura', '06200', 'España']
            if len(parts) >= 5:
                province = parts[-4]  
                comunity = parts[-3]
                return province, comunity
            return None, None
        except Exception as e:
            logger.error(f"Error extrayendo provincia y comunidad: {e}")
            return None, None

    def _clean_number(self, value):
        """Limpia valores numéricos quitando símbolos y convierte a float."""
        if value is None:
            return 0
        if isinstance(value, (int, float)):
            return value
        try:
            return float(
                str(value)
                .replace("€", "")
                .replace(",", ".")
                .replace(" ", "")
            )
        except ValueError:
            return 0

    def pretrain_model(self, province, comunity, bedrooms, meters, price):
        """Consulta el modelo entrenado para predecir el precio m2."""
        url = "http://localhost:8182/predict"
        payload = {
            "provincia": province or "",
            "comunidad": comunity or "",
            "bedrooms": bedrooms or 0,
            "metros": meters or 0,
            "precio": price or 0
        }
        headers = {"Content-Type": "application/json"}
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=5)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.error(f"Error al consultar modelo ML: {e}")
            return None

    def check_consistency(self):
        """Verifica consistencia solo usando el modelo entrenado."""
        ml_result = self.pretrain_model(
            self.province,
            self.comunity,
            self.bedrooms,
            self.meters,
            self.price
        )

        if not ml_result:
            return _error_response("No se pudo obtener predicción del modelo")

        self.predicted_price_m2 = ml_result.get("precio_estimado_m2")
        self.predicted_price_real = ml_result.get("precio_real_m2")
        self.predicted_penalty = ml_result.get("penalizacion")
        self.predicted_suspicious = ml_result.get("sospechoso")

        status = "SUSPICIOUS" if self.predicted_suspicious else "OK"
        score = self.predicted_penalty if self.predicted_penalty is not None else 0

        # Guardar en BD
        self.save_price_data(status, score)

        return {
            "status": status,
            "score": score,
            "predicted_price_m2": self.predicted_price_m2,
            "predicted_price_real": self.predicted_price_real,
            "penalty": self.predicted_penalty,
            "suspicious": self.predicted_suspicious
        }

    def save_price_data(self, status, score):
        try:
            PriceData.objects.update_or_create(
                ide=self.ide,
                defaults={
                    "reported_price": self.price,
                    "surface_m2": self.meters,
                    "estimated_price_m2": self.predicted_price_m2,
                    "estimated_price_m2_median": self.predicted_price_real,
                    "price_flag": status,
                    "price_prob": score
                }
            )
        except Exception as e:
            logger.error(f"Error guardando datos de precio: {e}")
