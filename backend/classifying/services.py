from sqlite3 import DatabaseError, IntegrityError
from classifying.models import LocationData
from classifying.osint_pipeline import OSINT
from rest_framework import status
import logging
from backend.services import _error_response

logger = logging.getLogger("classifying")

def classify_fraud(ide):
    """ Clasifica la probabilidad de fraude para un anuncio dado su identificador.

    Esta función utiliza métodos OSINT (Open Source Intelligence) para realizar
    distintas verificaciones sobre el anuncio, entre ellas: ubicación, imágenes y precio.
    Calcula un score de probabilidad de fraude basado en estas verificaciones,
    y guarda los datos de todo el análisis en la Base de datos. Permite repetir el análisis para un mismo
    anuncio.

    Args:
        ide (str): Identificador único del anuncio.

    Returns:
        dict or None: Un diccionario con los resultados del análisis si todo va bien.
                      Devuelve `None` si no hay datos de ubicación o si ocurre un error
                      al guardar en la base de datos.

                      Estructura del diccionario retornado:
                      {
                          "fraud_prob": float,           # Probabilidad estimada de fraude (0 a 1)
                          "location_prob": float,        # Puntaje de coincidencia de ubicación (0 a 1)
                          "price_prob": float,           # Puntaje de precio anómalo (0 a 1)
                          "price_flag": str,             # Etiqueta o estado del precio (por ejemplo: 'low', 'high', 'ok')
                          "confidence_level": int        # Nivel de confianza (0 a 5)
                      }
    """
    osint = OSINT(ide)

    # Address verification
    location = osint.LocationCheck()
    
    print(f"location output: {location}")
    
    # Image verification
    image = osint.ImageCheck()
    
    # Price verification
    price = osint.PriceCheck()

    logger.info(f"Location output: {location}")
    location_score = location.get("location_match_score", 0)
    logger.info(f"Image output: {image}")
    if image is None:
        image_score = 0
    else:
        image_score = image['similarity_score']
    
    logger.info(f"Price output: {price}")
    price_score = price.get("score")
    price_flag = price.get("status")
    
    if image_score is None:
        image_score = 0
    final_score = (float(location_score) + float(image_score) + float(price_score)) / 3

    confidence = int((1-final_score) * 5)
    
    # Persistencia de datos y score final
    if location is not None:
        try:
            LocationData.objects.update_or_create(
                ide=ide,
                defaults=location
            )
            # El resto se hace en sus propias clases
            
            return {
                "fraud_prob": final_score,
                "location_prob": location_score,
                "image_prob": image_score,
                "price_prob": price_score,
                "price_flag": price_flag,
                "confidence_level": confidence
            }

        except (IntegrityError, DatabaseError) as e:
            logger.error(f"Fallo al guardar ubicación para ide={ide}: {e}")
            _error_response("Fallo al guardar ubicación para ide={ide}: {e}", status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
            return None