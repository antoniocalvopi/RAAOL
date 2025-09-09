import re
import requests
from fake_useragent import UserAgent
from .models import Portales
import logging

""" Instancia de logger, permite registrar logs durante el proceso de verificación de la URL """
logger = logging.getLogger("crawling")

def crawling_check(url: str):
    """ Módulo que verifica la compatibilidad de la url y su estructura.

    Args:
        url (str): url a analizar

    Returns:
        Dict[str, bool, bool, bool]: diccionario con plataforma detectada y flags de las verificaciones realizadas.
    """
    logger.info(f"Verificando URL: {url}")
    plataforma = None

    for p in Portales.objects.all():
        if url.startswith(p.base_url):
            plataforma = p
            break

    plataforma_admitida = plataforma is not None
    if not plataforma_admitida:
        logger.warning("Plataforma no admitida.")
        return False, False, False, None
    else:
        plat = True
        logger.info(f"Plataforma admitida: {plataforma.name}")

        url_valida = bool(re.match(plataforma.url_pattern, url))
        if not url_valida:
            logger.warning("La estructura de la URL no es válida.")
            val = False
        else:
            val = True
            logger.info("La estructura de la URL es válida.")
    
        ua = UserAgent()
        headers = {
            "User-Agent": ua.random,
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }

        try:
            logger.info("Probando conexión con la URL...")
            response = requests.head(url, headers=headers, timeout=5)
            if response.status_code == 403:
                logger.warning("403 Forbidden con HEAD, intentando GET...")
                response = requests.get(url, headers=headers, timeout=5)
            conexion_ok = response.status_code == 200
            if conexion_ok:
                logger.info("Conexión exitosa.")
            else:
                logger.warning(f"Conexión fallida con status: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Excepción de conexión: {e}")
            conexion_ok = False
    
    return plat, val, conexion_ok, plataforma.name
